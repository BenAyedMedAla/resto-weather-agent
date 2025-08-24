from pydantic import BaseModel, Field as PydField
from dataclasses import Field
from typing import List, Optional, TypedDict
from pydantic import BaseModel
from typing_extensions import Annotated
from langgraph.graph.message import add_messages


class WeatherState(TypedDict):
    messages: Annotated[list, add_messages]
    weather_report: str

class Restaurant(TypedDict):
    name: str
    address: str
    details: str

class RestaurantsResponse(TypedDict):
    restaurants: List[Restaurant]

class RestaurantState(TypedDict):
    messages: Annotated[list, add_messages]
    location: str
    event: str
    date: str
    restaurants: list[Restaurant]

class ParentState(TypedDict):
    messages: Annotated[list, add_messages]
    location: str
    date: str
    event: str
    restaurants: list[Restaurant]
    weather_report: str
    recommendation: str

class QueryIntent(BaseModel):
    location: Optional[str] = PydField(default=None, description="City or area")
    date: Optional[str] = PydField(default=None, description="Natural language date, e.g., 'next Sunday'")
    event: Optional[str] = PydField(default=None, description="Occasion, e.g., 'date night', 'birthday'")