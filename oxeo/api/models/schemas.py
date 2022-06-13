# oxeo/api/models/data.py


from datetime import date

# data models for pydantic
from typing import List, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel, Field, conlist

# Auth


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True


# Geometry

Point = Tuple[float, float]
LinearRing = conlist(Point, min_items=4)
PolygonCoords = conlist(LinearRing, min_items=1)
MultiPolygonCoords = conlist(PolygonCoords, min_items=1)
BBox = Tuple[float, float, float, float]  # 2D bbox
Props = TypeVar("Props", bound=dict)


class Geometry(BaseModel):
    type: str = Field(..., example="Polygon")
    coordinates: Union[PolygonCoords, MultiPolygonCoords] = Field(
        ..., example=[[[1, 3], [2, 2], [4, 4], [1, 3]]]
    )

    def get(self, attr):
        return getattr(self, attr)


class Feature(BaseModel):
    type: str = Field("Feature", const=True)
    geometry: Geometry
    properties: Optional[Props]
    id: Optional[str]  # id corresponding to db entry. If present, updates db entry.
    bbox: Optional[BBox]
    labels: Optional[List[str]]


class FeatureCollection(BaseModel):
    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]
    properties: Optional[Props]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]


class AOIQuery(BaseModel):
    id: Optional[Union[int, List[int]]]
    geometry: Optional[Geometry]
    labels: Optional[List[str]]
    keyed_values: Optional[dict]
    limit: Optional[int]
    page: Optional[int]


class EventCreate(BaseModel):
    labels: Union[str, List[str]]
    aoi_id: int
    datetime: date
    keyed_values: dict


class Event(EventCreate):
    id: int


class EventQueryReturn(BaseModel):
    events: List[Event]
    next_page: Optional[int]


class EventQuery(BaseModel):
    aoi_id: Union[int, List[int]]
    id: Optional[Union[int, List[int]]]
    labels: Optional[List[str]]
    start_datetime: date
    end_datetime: date
    keyed_values: Optional[dict]
    limit: Optional[int]
    page: Optional[int]


class DeleteObj(BaseModel):
    id: Union[int, List[int]]
    table: str
