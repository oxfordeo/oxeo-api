# oxeo/api/models/data.py

from datetime import date

# data models for pydantic
from typing import Dict, List, Optional, Tuple, TypeVar, Union

from pydantic import BaseModel, Field, conlist

# Auth


def safe_cast(val, to_type, default=None):

    # cannot instantiate Union
    def safecaster(foo: to_type):
        return foo

    try:
        return to_type(val)
    except (ValueError, TypeError):
        raise TypeError


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Union[str, None] = None


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    token: str


class User(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        orm_mode = True


class ResetPassword(BaseModel):
    reset_token: str
    new_password: str
    confirm_password: str


# Geometry

Point = Tuple[float, float]
LinearRing = conlist(Point, min_items=4)
PolygonCoords = conlist(LinearRing, min_items=1)
MultiPolygonCoords = conlist(PolygonCoords, min_items=1)
BBox = Tuple[float, float, float, float]  # 2D bbox
Props = TypeVar("Props", bound=dict)


class Geometry(BaseModel):
    type: str = Field(..., example="Polygon")
    coordinates: Union[PolygonCoords, MultiPolygonCoords, Point] = Field(
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

    def to_geojson(self):
        return {
            "type": self.type,
            "geometry": self.geometry.__dict__,
            "properties": self.properties,
            "id": self.id,
        }


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
    id: Optional[Union[int, List[int]]] = Field(default=None, example=None)
    geometry: Optional[Geometry] = Field(
        default=None,
        example={
            "type": "Polygon",
            "coordinates": [
                [
                    [32.7, -17.4],
                    [32.7, -17.2],
                    [32.4, -17.2],
                    [32.4, -17.4],
                    [32.7, -17.4],
                ]
            ],
        },
    )
    labels: Optional[List[str]] = Field(default=None, example=["agricultural_area"])
    keyed_values: Optional[dict] = Field(default=None, example=None)
    simplify: Optional[float] = Field(default=None, example=None)
    centroids: Optional[bool] = Field(default=None, example=None)
    clip: Optional[bool] = Field(default=None, example=None)
    format: Optional[str] = Field(default="GeoJSON", example="GeoJSON")
    limit: Optional[int] = Field(default=None, example=2)
    page: Optional[int] = Field(default=None, example=None)


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


class ForecastQuery(BaseModel):
    bbox: Tuple[float, float, float, float]


class ForecastQueryReturn(BaseModel):
    forecast: List[float]


class AssetCreate(BaseModel):
    geometry: Geometry
    name: str
    labels: Union[str, List[str]]
    properties: dict
    company_weights: Dict[str, int]


class Asset(AssetCreate):
    id: int


class AssetQuery(BaseModel):
    id: Optional[Union[int, List[int]]]
    name: Optional[str]
    company_name: Optional[str]
    geometry: Optional[Geometry]
    labels: Optional[List[str]]
    keyed_values: Optional[dict]
    limit: Optional[int]
    page: Optional[int]


class AssetQueryReturn(BaseModel):
    assets: List[Asset]
    next_page: Optional[int]


class CompanyCreate(BaseModel):
    name: str
    properties: Optional[dict]


class Company(CompanyCreate):
    id: int


class CompanyQuery(BaseModel):
    id: Optional[Union[List[int], int]]
    name: Optional[str]
    keyed_values: Optional[dict]
    limit: Optional[int]
    page: Optional[int]


class CompanyQueryReturn(BaseModel):
    companies: List[Company]
    next_page: Optional[int]


class DeleteObj(BaseModel):
    id: Union[int, List[int]]
    table: str
