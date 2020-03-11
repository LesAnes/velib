from pydantic import BaseModel


class LatLngBoundsLiteral(BaseModel):
    east: float
    north: float
    south: float
    west: float


class Coordinate(BaseModel):
    lat: float
    lng: float
