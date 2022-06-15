from typing import List, Union

from fastapi import HTTPException
from geoalchemy2.shape import from_shape, to_shape
from shapely import geometry
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_

from oxeo.api.models import database, schemas


def geom2pg(geom: schemas.Geometry, allowed_types: List[str]):
    shapely_geom = schema2shp(geom=geom, allowed_types=allowed_types)
    pg_geom = from_shape(shapely_geom, srid=4326)
    return pg_geom


def pg2shapely(pg_geom):
    return to_shape(pg_geom)


def pg2gj(pg_geom):
    return geometry.mapping(to_shape(pg_geom))


def schema2shp(geom: schemas.Geometry, allowed_types: List[str]):
    shapely_geom = geometry.shape(geom.__dict__)

    if shapely_geom.type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Supplied geometry must one of f{allowed_types}.",
        )

    if shapely_geom.type == "Polygon":
        return geometry.MultiPolygon([shapely_geom])
    elif shapely_geom.type == "MultiPolygon":
        return shapely_geom
    elif shapely_geom.type == "Point":
        return shapely_geom
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Geometry type {shapely_geom.type} not supported",
        )


def enforce_list(obj):
    if isinstance(obj, list):
        return obj
    else:
        return [obj]


def check_aoi(aoi: schemas.Feature):
    """repackage aoi into a {geometry:, properties:} Feature"""

    if aoi.properties is None:
        aoi.properties = {}

    # if aoi is supplied with an id or bbox update them in properties.
    if aoi.bbox is not None:
        aoi.properties["bbox"] = aoi.bbox

    if aoi.labels is None and "labels" not in aoi.properties.keys():
        raise HTTPException(
            status_code=400,
            detail="'labels' required as a keyed value or as a property.",
        )
    if aoi.labels is not None and "labels" in aoi.properties.keys():
        raise HTTPException(
            status_code=400,
            detail="supply 'labels' required as either a keyed value or as a property.",
        )
    if aoi.labels is not None:
        aoi.labels = enforce_list(aoi.labels)
    else:
        aoi.labels = enforce_list(aoi.properties["labels"])
        del aoi.properties["labels"]

    for label in aoi.labels:
        if label not in database.VALID_AOI_LABELS:
            raise HTTPException(
                status_code=400,
                detail=f"got label '{label}', must be in {database.VALID_AOI_LABELS}",
            )

    return aoi


def update_aoi(db: Session, aoi: schemas.Feature, user: schemas.User):

    aoi = check_aoi(aoi)

    # update the db
    db_aoi = db.query(database.AOI).filter(database.AOI.id == aoi.id).first()

    # check labels
    if db_aoi.labels != aoi.labels:
        db_aoi.labels = aoi.labels

    # check properties
    if db_aoi.properties != aoi.properties:
        db_aoi.properties = aoi.properties

    # check geometry
    if pg2shapely(db_aoi.geometry) != schema2shp(
        aoi.geometry, allowed_types=["Polygon", "MultiPolygon"]
    ):
        db_aoi.geometry = schema2shp(
            aoi.geometry, allowed_types=["Polygon", "MultiPolygon"]
        ).wkt

    # commit
    db.commit()
    db.refresh(db_aoi)

    return db_aoi


def create_aoi(db: Session, aoi: schemas.Feature, user: schemas.User):

    aoi = check_aoi(aoi)

    # do stuff here. put that db aoi in the db
    db_aoi = database.AOI(
        geometry=schema2shp(
            aoi.geometry, allowed_types=["Polygon", "MultiPolygon"]
        ).wkt,
        labels=aoi.labels,
        properties=aoi.properties,
    )

    db.add(db_aoi)
    db.commit()
    db.refresh(db_aoi)

    return db_aoi


def _postprocess_aoi(aoi: database.AOI) -> schemas.Feature:

    properties = aoi.properties
    properties["labels"] = aoi.labels
    geometry = schemas.Geometry(**pg2gj(aoi.geometry))

    return schemas.Feature(
        type="Feature", geometry=geometry, properties=properties, id=aoi.id
    )


def postprocess_aois(aois: Union[database.AOI, List[database.AOI]], next_page: int):
    if isinstance(aois, list):
        return schemas.FeatureCollection(
            type="FeatureCollection",
            features=[_postprocess_aoi(aoi) for aoi in aois],
            properties={"next_page": next_page},
        )
    else:
        return _postprocess_aoi(aois)


def get_aoi(aoi_query: schemas.AOIQuery, db: Session, user: schemas.User):

    # db.query(database.Item).offset(skip).limit(limit).all()
    if aoi_query.limit is not None and aoi_query.limit > 1000:
        raise HTTPException(
            status_code=400,
            detail=f"query limit '{aoi_query.limit}', max query limit is 1000.",
        )

    # set the page and limit if none
    if aoi_query.page is None:
        aoi_query.page = 0
    if aoi_query.limit is None:
        aoi_query.limit = 1000

    if isinstance(aoi_query.id, int):
        aoi_query.id = enforce_list(aoi_query.id)

    Q = db.query(database.AOI)

    # if a single id is given, just get that id
    if aoi_query.id is not None:
        if isinstance(aoi_query.id, int):
            # single aoi requested, just return it.
            return postprocess_aois(
                Q.filter(database.AOI.id == aoi_query.id).first(), aoi_query.page
            )
        else:
            # multiple aoi requested. Add as a filter.
            Q = Q.filter(database.AOI.id.in_(tuple(aoi_query.id)))

    # do labels
    if aoi_query.labels is not None:

        # OR condition
        conditions = [
            database.AOI.labels.contains(f"{{{label}}}") for label in aoi_query.labels
        ]
        Q = Q.filter(or_(*conditions))
        # AND condition
        # for label in aoi_query.labels:
        #     Q = Q.filter(database.AOI.labels.contains(f"{{{label}}}"))

    # do geometry if it's available
    if aoi_query.geometry is not None:
        Q = Q.filter(
            database.AOI.geometry.ST_Intersects(
                geom2pg(aoi_query.geometry, allowed_types=["Polygon", "MultiPolygon"])
            )
        )

    # do key-value pairs
    if aoi_query.keyed_values is not None:
        for key, value in aoi_query.keyed_values.items():
            if value is not None:
                Q = Q.filter(database.AOI.properties[key].as_string() == value)
            else:
                Q = Q.filter(database.AOI.properties.has_key(key))  # noqa

    # do pagination
    Q = Q.offset(aoi_query.page * aoi_query.limit).limit(aoi_query.limit + 1)

    results = Q.all()

    if len(results) > aoi_query.limit:
        next_page = aoi_query.page + 1
    else:
        next_page = None

    return postprocess_aois(results[0 : aoi_query.limit], next_page)  # noqa


def check_not_id(event):
    if isinstance(event, schemas.EventCreate) and not isinstance(event, schemas.Event):
        return True
    else:
        return False


def update_event(event: schemas.Event, db: Session, user: schemas.User):
    db_event = db.query(database.Event).filter(database.Event.id == event.id).first()

    if db_event.labels != enforce_list(event.labels):
        db_event.labels = enforce_list(event.labels)
    if db_event.aoi_id != event.aoi_id:
        db_event.aoi_id = event.aoi_id
    if db_event.datetime != event.datetime:
        db_event.datetime = event.datetime
    if db_event.properties != event.keyed_values:
        db_event.properties = event.keyed_values

    db.commit()
    db.refresh(db_event)

    return db_event


def update_events(events: List[schemas.Event], db: Session, user: schemas.User):

    db_events = [update_event(event, db, user) for event in events]

    return db_events


def create_events(events: List[schemas.EventCreate], db: Session, user: schemas.User):
    db_events = [
        database.Event(
            labels=enforce_list(event.labels),
            aoi_id=event.aoi_id,
            datetime=event.datetime,
            properties=event.keyed_values,
        )
        for event in events
    ]

    db.add_all(db_events)
    db.commit()
    for db_event in db_events:
        db.refresh(db_event)

    return db_events


def postprocess_events(db_events_list: List[database.Event], next_page: int):

    events_list = [
        schemas.Event(
            id=event.id,
            labels=event.labels,
            aoi_id=event.aoi_id,
            datetime=event.datetime,
            keyed_values=event.properties,
        )
        for event in db_events_list
    ]

    return schemas.EventQueryReturn(events=events_list, next_page=next_page)


def get_events(event_query: schemas.EventQuery, db: Session, user: schemas.User):

    # db.query(database.Item).offset(skip).limit(limit).all()
    if event_query.limit is not None and event_query.limit > 10000:
        raise HTTPException(
            status_code=400,
            detail=f"query limit '{event_query.limit}', max Event limit is 10000.",
        )

    # set the page and limit if none
    if event_query.page is None:
        event_query.page = 0
    if event_query.limit is None:
        event_query.limit = 10000

    Q = db.query(database.Event)

    # if single aoi_id is given, wrap it in list
    if isinstance(event_query.aoi_id, int):
        event_query.aoi_id = [event_query.aoi_id]
    if isinstance(event_query.id, int):
        event_query.id = [event_query.id]

    if event_query.id is not None:
        Q = Q.filter(database.Event.id.in_(tuple(event_query.id)))

    Q = Q.filter(database.Event.aoi_id.in_(tuple(event_query.aoi_id)))

    # do labels
    if event_query.labels is not None:

        # OR condition
        conditions = [
            database.Event.labels.contains(f"{{{label}}}")
            for label in event_query.labels
        ]
        Q = Q.filter(or_(*conditions))

    # do key-value pairs
    if event_query.keyed_values is not None:
        for key, value in event_query.keyed_values.items():
            if value is not None:
                Q = Q.filter(database.Event.properties[key].as_string() == value)
            else:
                Q = Q.filter(database.Event.properties.has_key(key))  # noqa

    # do dates
    Q = Q.filter(database.Event.datetime >= event_query.start_datetime)
    Q = Q.filter(database.Event.datetime <= event_query.end_datetime)

    # do pagination
    Q = Q.offset(event_query.page * event_query.limit).limit(event_query.limit + 1)

    results = Q.all()
    if len(results) > event_query.limit:
        next_page = event_query.page + 1
    else:
        next_page = None

    return postprocess_events(results[0 : event_query.limit], next_page)  # noqa


def delete_objects(delete_query: schemas.DeleteObj, db: Session, user: schemas.User):

    if delete_query.table not in ["event", "aoi", "asset", "company"]:
        raise HTTPException(
            status_code=400,
            detail="Field `Table` must be one of [event,aoi,asset,company]",
        )
    delete_query.id = enforce_list(delete_query.id)

    if delete_query.table == "events":
        db.query(database.Event).filter(
            database.Event.id.in_(tuple(delete_query.id))
        ).delete()
        db.commit()
    if delete_query.table == "aoi":
        db.query(database.AOI).filter(
            database.AOI.id.in_(tuple(delete_query.id))
        ).delete()
        db.commit()
    if delete_query.table == "asset":
        db_asset = (
            db.query(database.Asset)
            .filter(database.Asset.id.in_(tuple(delete_query.id)))
            .first()
        )
        for company in db_asset.companies:
            company.assets.remove(db_asset)

        db.delete(db_asset)

        db.commit()

    if delete_query.table == "company":
        db_company = (
            db.query(database.Company)
            .filter(database.Company.id.in_(tuple(delete_query.id)))
            .first()
        )
        for asset in db_company.assets:
            asset.companies.remote(db_company)

        db.delete(db_company)
        db.commit()

    return delete_query.id
