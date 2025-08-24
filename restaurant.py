from typing import List
from ddgs import DDGS
from urllib.parse import urlparse
from langgraph.graph import StateGraph, START, END
from states import RestaurantState, Restaurant  # your TypedDicts

GOOD_DOMAINS = {"zomato", "swiggy", "tripadvisor", "dineout", "lbb", "agoda", "timeout"}

def _domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""

def restaurant_fetch(state: RestaurantState):
    loc  = state.get("location", "")
    date = state.get("date", "")
    event = state.get("event", "")
    query = f"best {event} restaurants in {loc} {date}".strip()

    rows: List[dict] = []
    with DDGS() as ddgs:
        # ddgs.text yields dicts: {'title','href','body','date','source',...}
        for r in ddgs.text(query, max_results=20):
            rows.append(r)

    # Keep raw text for debugging
    blob_lines = []
    restaurants: List[Restaurant] = []
    seen = set()

    for r in rows:
        title = (r.get("title") or "").strip()
        href  = (r.get("href") or "").strip()
        body  = (r.get("body") or "").strip()
        if not title:
            continue

        # de-dup by name
        key = title.lower()
        if key in seen:
            continue
        seen.add(key)

        # Build your TypedDict
        restaurants.append({
            "name": title,
            "address": "",  # search result usually doesn't include a postal address
            "details": (body + ("\n" + href if href else "")).strip()
        })
        blob_lines.append(f"{title}\n{href}\n{body}\n")

    return {
        "restaurants": restaurants,                 # <- IMPORTANT
        "search_blob": "\n".join(blob_lines).strip()  # <- for debugging
    }

def build_restaurant_graph():
    g = StateGraph(RestaurantState)
    g.add_node("restaurant_fetch", restaurant_fetch)
    g.add_edge(START, "restaurant_fetch")
    g.add_edge("restaurant_fetch", END)
    return g.compile()
