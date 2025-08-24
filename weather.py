from llm_client import llm
from states import WeatherState
from langgraph.graph import StateGraph, START, END

# Weather assistant node
def weather_assistant(state: WeatherState):
    return {"messages": [llm.invoke(state["messages"])]}

def weather_formatter(state: WeatherState):
    weather_report = ""
    for message in state['messages']:
        weather_report += message.content
    return {"weather_report": weather_report}

# Building the weather graph
def build_weather_graph():
    weather_builder = StateGraph(WeatherState)
    weather_builder.add_node("weather_assistant", weather_assistant)
    weather_builder.add_node("weather_formatter", weather_formatter)
    weather_builder.add_edge(START, "weather_assistant")
    weather_builder.add_edge("weather_assistant", "weather_formatter")
    weather_builder.add_edge("weather_formatter", END)

    weather_graph = weather_builder.compile()
    return weather_graph