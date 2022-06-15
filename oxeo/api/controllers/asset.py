from typing import List

from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import or_

from oxeo.api.controllers.geom import (
    enforce_list,
    geom2pg,
    pg2gj,
    pg2shapely,
    schema2shp,
)
from oxeo.api.models import database, schemas


def check_not_id(asset):
    if isinstance(asset, schemas.AssetCreate) and not isinstance(asset, schemas.Asset):
        return True
    else:
        return False


def get_company_weights(db_assets_list: List[database.Asset], db: Session):

    links = {a.id: {} for a in db_assets_list}

    Q = db.query(database.AssetCompany)
    Q = Q.filter(
        database.AssetCompany.asset_id.in_(tuple(a.id for a in db_assets_list))
    )

    db_links = Q.all()

    db_companies = (
        db.query(database.Company)
        .filter(
            database.Company.id.in_(tuple({db_link.company_id for db_link in db_links}))
        )
        .all()
    )
    company_lookup = {c.id: c.name for c in db_companies}

    for db_link in db_links:
        links[db_link.asset_id][company_lookup[db_link.company_id]] = db_link.equity

    return links


def _postprocess_asset(asset: database.Asset, company_weight: dict) -> schemas.Feature:

    properties = asset.properties
    properties["labels"] = asset.labels
    properties["name"] = asset.name
    properties["company_weights"] = company_weight
    geometry = schemas.Geometry(**pg2gj(asset.geometry))

    return schemas.Feature(
        type="Feature", geometry=geometry, properties=properties, id=asset.id
    )


def postprocess_assets(
    db_assets_list: List[database.Asset], company_weights: dict, next_page: int
):

    """
    company_weights: {Asset.id: {Company1.id:int,Company2.id:int}
    """

    features = [
        _postprocess_asset(asset, company_weights[asset.id]) for asset in db_assets_list
    ]

    return schemas.FeatureCollection(
        type="FeatureCollection",
        features=features,
        properties={"next_page": next_page},
    )


def get_assets(
    asset_query: schemas.AssetQuery,
    db: Session,
    user: schemas.User,
):
    # db.query(database.Item).offset(skip).limit(limit).all()
    if asset_query.limit is not None and asset_query.limit > 1000:
        raise HTTPException(
            status_code=400,
            detail=f"query limit '{asset_query.limit}', max Asset limit is 1000.",
        )

    # set the page and limit if none
    if asset_query.page is None:
        asset_query.page = 0
    if asset_query.limit is None:
        asset_query.limit = 10000

    Q = db.query(database.Asset)

    # if single aoi_id is given, wrap it in list
    if isinstance(asset_query.id, int):
        asset_query.id = [asset_query.id]

    if asset_query.id is not None:
        Q = Q.filter(database.Asset.id.in_(tuple(asset_query.id)))

    # do geometry if it's available
    if asset_query.geometry is not None:
        Q = Q.filter(
            database.Asset.geometry.ST_Intersects(
                geom2pg(asset_query.geometry, allowed_types=["Polygon", "MultiPolygon"])
            )
        )

    # do company name if it's available
    if asset_query.company_name is not None:
        Q = Q.where(database.Company.name == asset_query.company_name)

    # do labels
    if asset_query.labels is not None:

        # OR condition
        conditions = [
            database.Asset.labels.contains(f"{{{label}}}")
            for label in asset_query.labels
        ]
        Q = Q.filter(or_(*conditions))

    # do key-value pairs
    if asset_query.keyed_values is not None:
        for key, value in asset_query.keyed_values.items():
            if value is not None:
                Q = Q.filter(database.Asset.properties[key].as_string() == value)
            else:
                Q = Q.filter(database.Asset.properties.has_key(key))  # noqa

    # do pagination
    Q = Q.offset(asset_query.page * asset_query.limit).limit(asset_query.limit + 1)

    results = Q.all()
    if len(results) > asset_query.limit:
        next_page = asset_query.page + 1
    else:
        next_page = None

    results = results[0 : asset_query.limit]  # noqa

    company_weights = get_company_weights(db_assets_list=results, db=db)

    return postprocess_assets(results, company_weights, next_page)


def update_asset(asset: schemas.Asset, db: Session, user: schemas.User):
    db_asset = db.query(database.Asset).filter(database.Asset.id == asset.id).first()

    # recreate company_weights
    company_name_keys = {company.id: company.name for company in db_asset.companies}
    db_links = (
        db.query(database.AssetCompany)
        .filter(database.AssetCompany.asset_id == asset.id)
        .all()
    )
    db_company_weights = {
        company_name_keys[link.company_id]: link.equity for link in db_links
    }

    # check labels
    if db_asset.labels != enforce_list(asset.labels):
        db_asset.labels = enforce_list(asset.labels)

    # check properties
    if db_asset.properties != asset.properties:
        db_asset.properties = asset.properties

    # check geometry
    if pg2shapely(db_asset.geometry) != schema2shp(
        asset.geometry, allowed_types=["Point"]
    ):
        db_asset.geometry = schema2shp(
            asset.geometry, allowed_types=["Polygon", "MultiPolygon"]
        ).wkt

    # commit here before continuing to relationships
    db.commit()
    db.refresh(db_asset)

    # check company_weights # todo
    if asset.company_weights != db_company_weights:

        companies = (
            db.query(database.Company)
            .filter(database.Company.name.in_(tuple(asset.company_weights.keys())))
            .all()
        )

        for company_name in asset.company_weights.keys():
            if company_name not in [company.name for company in companies]:
                # raise not found?

                new_company = schemas.CompanyCreate(name=company_name, properties={})
                companies.append(create_company(new_company, db, user))

        db_asset.companies = companies
        db.commit()
        db.refresh(db_asset)

        # for company in companies:
        #    if asset.id not in [a.id for a in company.assets]:
        #        company.assets.append(db_asset)
        # db.commit()
        # db.refresh(db_asset)

        # finally fix links
        company_dict = {company.name: company for company in companies}
        # put weight properties in link table
        for company_name, db_company in company_dict.items():
            Q = db.query(database.AssetCompany)
            Q = Q.where(database.AssetCompany.asset_id == db_asset.id)
            Q = Q.where(database.AssetCompany.company_id == db_company.id)
            link = Q.first()
            link.equity = asset.company_weights[company_name]

        db.commit()
        db.refresh(db_asset)

    return db_asset


def update_assets(assets: List[schemas.Asset], db: Session, user: schemas.User):

    db_assets = [update_asset(asset, db, user) for asset in assets]

    return db_assets


def create_company(company: schemas.CompanyCreate, db: Session, user: schemas.User):

    if company.properties is None:
        company.properties = {}

    db_company = database.Company(name=company.name, properties=company.properties)

    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return db_company


def update_company(company: schemas.Company, db: Session, user: schemas.User):

    db_company = (
        db.query(database.Company).filter(database.Company.id == company.id).first()
    )

    # check name
    if db_company.name != company.name:
        db_company.name = company.name

    # check properties
    if db_company.properties != company.properties:
        db_company.properties = company.properties

    db.commit()
    db.refresh(db_company)

    return db_company


def get_companies(company_query: schemas.CompanyQuery, db: Session, user: schemas.User):

    # db.query(database.Item).offset(skip).limit(limit).all()
    if company_query.limit is not None and company_query.limit > 1000:
        raise HTTPException(
            status_code=400,
            detail=f"query limit '{company_query.limit}', max Company limit is 1000.",
        )

    # set the page and limit if none
    if company_query.page is None:
        company_query.page = 0
    if company_query.limit is None:
        company_query.limit = 1000

    Q = db.query(database.Company)

    # if single id is given, wrap it in list
    if isinstance(company_query.id, int):
        company_query.id = [company_query.id]

    if company_query.id is not None:
        Q = Q.filter(database.Company.id.in_(tuple(company_query.id)))

    # if name is given
    if company_query.name is not None:
        Q = Q.filter(database.Company.name == company_query.name)

    # do key-value pairs
    if company_query.keyed_values is not None:
        for key, value in company_query.keyed_values.items():
            if value is not None:
                Q = Q.filter(database.Company.properties[key].as_string() == value)
            else:
                Q = Q.filter(database.Company.properties.has_key(key))  # noqa

    # do pagination
    Q = Q.offset(company_query.page * company_query.limit).limit(
        company_query.limit + 1
    )

    results = Q.all()
    if len(results) > company_query.limit:
        next_page = company_query.page + 1
    else:
        next_page = None

    return postprocess_companies(results[0 : company_query.limit], next_page)  # noqa


def _postprocess_company(db_company):
    return schemas.Company(
        id=db_company.id,
        name=db_company.name,
        properties=db_company.properties,
    )


def postprocess_companies(db_companies: List[database.Company], next_page):
    return dict(
        companies=[_postprocess_company(db_company) for db_company in db_companies],
        next_page=next_page,
    )


def create_asset(asset: schemas.AssetCreate, db: Session, user: schemas.User):

    # check labels
    if len(asset.labels) == 0:
        raise HTTPException(
            status_code=400,
            detail=f"Asset labels must be in {database.VALID_ASSET_LABELS}",
        )

    # check company formats and company_weights
    companies_400_msg = "asset.company_weights must be a {company_name:equity_weight} dict where equity weights sum to 100."  # noqa

    if sum(asset.company_weights.values()) != 100:
        raise HTTPException(status_code=400, detail=companies_400_msg)

    for equity_weight in asset.company_weights.values():
        if not isinstance(equity_weight, int):
            raise HTTPException(status_code=400, detail=companies_400_msg)

    # get companies
    companies = (
        db.query(database.Company)
        .filter(database.Company.name.in_(tuple(asset.company_weights.keys())))
        .all()
    )

    for company_name in asset.company_weights.keys():
        if company_name not in [company.name for company in companies]:
            # raise not found?

            new_company = schemas.CompanyCreate(name=company_name, properties={})
            companies.append(create_company(new_company, db, user))

    # create asset
    db_asset = database.Asset(
        geometry=schema2shp(asset.geometry, allowed_types=["Point"]).wkt,
        name=asset.name,
        labels=enforce_list(asset.labels),
        properties=asset.properties,
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)

    # append asset
    for company in companies:
        company.assets.append(db_asset)
    db.commit()

    # append companies
    db_asset.companies = companies
    db.commit()
    db.refresh(db_asset)

    company_dict = {company.name: company for company in companies}
    # put weight properties in link table
    for company_name, db_company in company_dict.items():
        Q = db.query(database.AssetCompany)
        Q = Q.where(database.AssetCompany.asset_id == db_asset.id)
        Q = Q.where(database.AssetCompany.company_id == db_company.id)
        link = Q.first()
        link.equity = asset.company_weights[company_name]

    db.commit()

    return db_asset


def create_assets(assets: List[schemas.AssetCreate], db: Session, user: schemas.User):

    # do stuff here. put that db asset in the db
    db_assets = [create_asset(asset, db, user) for asset in assets]

    db.add_all(db_assets)
    db.commit()
    for db_asset in db_assets:
        db.refresh(db_asset)

    return db_assets
