from typing import List

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
