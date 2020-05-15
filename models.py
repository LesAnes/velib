from enum import IntEnum
from typing import List, Optional

from pydantic import BaseModel


class LatLngBoundsLiteral(BaseModel):
    east: float
    north: float
    south: float
    west: float


class Coordinate(BaseModel):
    lat: float
    lng: float


class Station:
    stationId: int
    name: str
    lat: float
    lng: float
    capacity: int
    distance: float
    numBikesAvailable: int
    numDocksAvailable: int
    isInstalled: bool
    isReturning: bool
    isRenting: bool
    lastReported: int
    mechanical: int
    ebike: int
    rentalMethods: List[str]


class FeedbackType(IntEnum):
    confirmed = 0
    broken = 1


class OptionsList(BaseModel):
    delta: int = None


class Feedback(BaseModel):
    stationId: int
    type: FeedbackType
    mechanical: int
    ebike: int
    dock: int
