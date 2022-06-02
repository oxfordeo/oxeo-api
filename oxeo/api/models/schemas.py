# oxeo/api/models/data.py


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


class Feature(BaseModel):
    type: str = Field("Feature", const=True)
    geometry: Geometry
    properties: Optional[Props]
    id: Optional[str]
    bbox: Optional[BBox]


class FeatureCollection(BaseModel):
    type: str = Field("FeatureCollection", const=True)
    features: List[Feature]

    def __iter__(self):
        """iterate over features"""
        return iter(self.features)

    def __len__(self):
        """return features length"""
        return len(self.features)

    def __getitem__(self, index):
        """get feature at a given index"""
        return self.features[index]
