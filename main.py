import datetime
from dotenv import load_dotenv
from typing_extensions import TypedDict, Annotated

from langgraph.prebuilt import ToolNode, tools_condition

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from llm_client import llm
from restaurant import build_restaurant_graph
from states import ParentState, QueryIntent
from weather import build_weather_graph



load_dotenv()

# Initialize the Groq chat model


def query_analyzer(state: ParentState):
    # Safely get the latest message (works if it's a dict, str, or LangChain message object)
    last = state["messages"][-1]
    user_msg = getattr(last, "content", last)

    # Ask the LLM to extract structured fields
    structured_llm = llm.with_structured_output(QueryIntent)
    intent = structured_llm.invoke(
        f"Extract location, date, and event from this message: {user_msg}\n"
        "If a field is missing, leave it null."
    )

    return {
        "location": intent.location or state.get("location", ""),
        "date": intent.date or state.get("date", ""),   # 👈 plain string stays here
        "event": intent.event or state.get("event", ""),
        "messages": state["messages"],
    }

def recommendation_analyzer(state: ParentState):
    # Take top 5 and show names + 1-line detail (include URL if present)
    lines = []
    for r in state.get("restaurants", [])[:5]:
        # try to surface the first URL found in details
        url = ""
        for tok in r.get("details","").split():
            if tok.startswith("http"):
                url = tok; break
        snippet = r.get("details","").split("\n")[0][:160]
        lines.append(f"- {r.get('name','(unknown)')}" + (f" — {snippet}" if snippet else "") + (f" ({url})" if url else ""))

    shortlist = "\n".join(lines) if lines else "No restaurants were found."

    prompt = (
        "You are a helpful concierge.\n"
        f"Weather report (raw): {state.get('weather_report','(unknown)')}\n"
        f"Event: {state.get('event','')}\n"
        f"Location: {state.get('location','')}\n"
        f"Date: {state.get('date','')}\n\n"
        "Shortlist (top picks):\n"
        f"{shortlist}\n\n"
        "Write a concise recommendation that:\n"
        "1) states GO / STAY-IN with a reason tied to weather and options,\n"
        "2) lists 3 named picks with a one-liner each,\n"
        "3) ends with 2 practical tips (reservation/time/neighborhood).\n"
        "Keep it under 10 lines."
    )
    result = llm.invoke(prompt)
    return {"recommendation": result.content}

# Building the parent graph
weather_graph = build_weather_graph()
restaurant_graph = build_restaurant_graph()
entry_builder = StateGraph(ParentState)
entry_builder.add_node("query_analyzer", query_analyzer)
entry_builder.add_node("weather_graph", weather_graph)
entry_builder.add_node("restaurant_graph", restaurant_graph)
entry_builder.add_node("recommendation_analyzer", recommendation_analyzer)

entry_builder.add_edge(START, "query_analyzer")
entry_builder.add_edge("query_analyzer", "weather_graph")
entry_builder.add_edge("query_analyzer", "restaurant_graph")
entry_builder.add_edge("weather_graph", "recommendation_analyzer")
entry_builder.add_edge("restaurant_graph", "recommendation_analyzer")
entry_builder.add_edge("recommendation_analyzer", END)

graph = entry_builder.compile()

# Invoking the graph
result = graph.invoke({
    "messages": ["Tell me about the best restaurants for breakfast in barcelone for next saturday"]
})

print("\nAgent:\n" + result.get("recommendation",""))
