import json

# data models for pydantic
from typing import List, Optional, Union

from dateutil import parser
from dateutil.parser._parser import ParserError
from fastapi import HTTPException, Query
from pydantic import parse_obj_as

from oxeo.api.models import schemas


def err_msg(key, val, type_ob):
    if key == "geometry":
        msg = f"Parameter '{key}' could not be parsed." + "Please submit valid geojson."
    elif type_ob is not None:
        msg = f"Parameter '{key}' with val '{val}' not parseable to type: {type_ob}"
    else:
        msg = f"Parameter '{key}' not json parseable: {val}"

    raise HTTPException(
        status_code=400,
        detail=msg,
    )


def to_assetquery(
    id: Optional[str] = None,
    name: Optional[str] = None,
    company_name: Optional[str] = None,
    geometry: Optional[str] = None,
    labels: Optional[str] = None,
    keyed_values: Optional[str] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
):
    params = {"company_name": company_name}

    for key, val, type_ob in zip(
        ["id", "geometry", "labels", "keyed_values"],
        [id, geometry, labels, keyed_values],
        [
            Union[int, List[int]],
            Optional[schemas.Geometry],
            Optional[List[str]],
            Optional[dict],
        ],
    ):
        try:
            params[key] = json.loads(val) if val is not None else val
        except TypeError:
            err_msg(key, val, None)

        try:
            parse_obj_as(type_ob, params[key])
        except TypeError:
            err_msg(key, val, type_ob)

    asset_query = schemas.AssetQuery(**params, limit=limit, page=page)

    return asset_query


def to_companyquery(
    id: Optional[str] = Query(default=None, example=None),
    name: Optional[str] = Query(default=None, example="""my-company-name"""),
    keyed_values: Optional[str] = Query(default=None, example=None),
    limit: Optional[int] = Query(default=None, example=None),
    page: Optional[int] = Query(default=None, example=None),
):
    params = {"name": name}

    for key, val, type_ob in zip(
        ["id", "keyed_values"],
        [id, keyed_values],
        [Union[int, List[int]], Optional[dict]],
    ):
        try:
            params[key] = json.loads(val) if val is not None else val
        except TypeError:
            err_msg(key, val, None)

        try:
            parse_obj_as(type_ob, params[key])
        except TypeError:
            err_msg(key, val, type_ob)

    asset_query = schemas.CompanyQuery(**params, limit=limit, page=page)

    return asset_query


def to_eventquery(
    aoi_id: str = Query(default=..., example="2197"),
    start_datetime: str = Query(default=..., example="2018-01-01"),
    end_datetime: str = Query(default=..., example="2018-06-30"),
    id: Optional[str] = Query(default=None, example=None),
    labels: Optional[str] = Query(default=None, example="""["ndvi"]"""),
    keyed_values: Optional[str] = Query(default=None, example=None),
    limit: Optional[int] = Query(default=None, example=None),
    page: Optional[int] = Query(default=None, example=None),
):

    params = {}

    for key, val, type_ob in zip(
        ["id", "aoi_id", "labels", "keyed_values"],
        [id, aoi_id, labels, keyed_values],
        [
            Optional[Union[int, List[int]]],
            Optional[Union[int, List[int]]],
            Optional[List[str]],
            Optional[dict],
        ],
    ):
        try:
            params[key] = json.loads(val) if val is not None else val
        except TypeError:
            err_msg(key, val, None)

        try:
            parse_obj_as(type_ob, params[key])
        except TypeError:
            err_msg(key, val, type_ob)

    try:
        start_datetime = parser.parse(start_datetime).date()
        end_datetime = parser.parse(end_datetime).date()
    except ParserError:
        raise HTTPException(
            status_code=400,
            detail=(
                "Datetime parameters not datetime parseable: "
                + f"{start_datetime},{end_datetime}"  # noqa
            ),
        )

    event_query = schemas.EventQuery(
        **params,
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        limit=limit,
        page=page,
    )

    return event_query


def to_aoiquery(
    id: Optional[str] = Query(default=None, example=None),
    geometry: Optional[str] = Query(
        default=None,
        example="""
        {"type": "Polygon",
        "coordinates":
        [[[32.7, -17.4], [32.7, -17.2],
        [32.4, -17.2], [32.4, -17.4],
        [32.7, -17.4]]]}
        """,
    ),
    labels: Optional[str] = Query(default=None, example="""["agricultural_area"]"""),
    keyed_values: Optional[str] = Query(default=None, example=None),
    simplify: Optional[float] = Query(default=None, example=None),
    centroids: Optional[bool] = Query(default=None, example=None),
    clip: Optional[bool] = Query(default=None, example=None),
    format: Optional[str] = Query(default="GeoJSON", example="GeoJSON"),
    limit: Optional[int] = Query(default=None, example=2),
    page: Optional[int] = Query(default=None, example=None),
):

    params = {}

    for key, val, type_ob in zip(
        ["id", "geometry", "labels", "keyed_values"],
        [id, geometry, labels, keyed_values],
        [
            Optional[Union[int, List[int]]],
            Optional[schemas.Geometry],
            Optional[List[str]],
            Optional[dict],
        ],
    ):

        print(key, val, type_ob)

        try:
            params[key] = json.loads(val) if val is not None else val
        except TypeError:
            err_msg(key, val, None)

        try:
            parse_obj_as(type_ob, params[key])
        except TypeError:
            err_msg(key, val, type_ob)

    print("PARAMS")
    print(params)

    aoi_query = schemas.AOIQuery(
        **params,
        simplify=simplify,
        centroids=centroids,
        clip=clip,
        format=format,
        limit=limit,
        page=page,
    )

    return aoi_query
