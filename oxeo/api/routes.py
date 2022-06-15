from datetime import timedelta
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import oxeo.api.controllers as C
from oxeo.api.models import database, schemas

router = APIRouter()

requires_auth = [Depends(C.auth.get_current_active_user)]
admin_checker = C.auth.RoleChecker(["admin"])
requires_admin = [Depends(C.auth.get_current_active_user), Depends(admin_checker)]


@router.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = C.auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=10)
    access_token = C.auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", dependencies=requires_admin, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = C.auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return C.auth.create_user(db=db, user=user, role="user")


@router.get("/users/", dependencies=requires_auth, response_model=schemas.User)
def read_users(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    user = dict(id=user.id, role=user.role, email=user.email, is_active=user.is_active)

    return user


@router.post("/aoi/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED)
def post_aoi(
    aoi: schemas.Feature,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    _aoi = C.geom.create_aoi(db=db, aoi=aoi, user=user)

    return {"id": _aoi.id}


@router.post(
    "/aoi/update/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED
)
def update_aoi(
    aoi: schemas.Feature,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    _aoi = C.geom.update_aoi(db=db, aoi=aoi, user=user)

    return {"id": _aoi.id}


@router.get(
    "/aoi/",
    dependencies=requires_auth,
    response_model=schemas.FeatureCollection,
)
def get_aoi(
    aoi_query: schemas.AOIQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return C.geom.get_aoi(aoi_query=aoi_query, db=db, user=user)


@router.post(
    "/events/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED
)
def post_events(
    events: Union[
        schemas.EventCreate,
        List[schemas.EventCreate],
    ],
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    events = C.geom.enforce_list(events)

    _events = C.geom.create_events(events=events, db=db, user=user)

    return {"id": [event.id for event in _events]}


@router.post(
    "/events/update/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED
)
def update_events(
    events: Union[
        schemas.Event,
        List[schemas.Event],
    ],
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    events = C.geom.enforce_list(events)

    _events = C.geom.update_events(events=events, db=db, user=user)

    return {"id": [event.id for event in _events]}


@router.get(
    "/events/", dependencies=requires_auth, response_model=schemas.EventQueryReturn
)
def get_events(
    event_query: schemas.EventQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return C.geom.get_events(event_query=event_query, db=db, user=user)


@router.post("/assets/", dependencies=requires_admin, status_code=200)
def post_assets(
    assets: Union[
        schemas.AssetCreate,
        List[schemas.AssetCreate],
    ],
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):

    assets = C.geom.enforce_list(assets)

    _assets = C.asset.create_assets(assets=assets, db=db, user=user)

    return {"id": [asset.id for asset in _assets]}


@router.post("/assets/update/", dependencies=requires_admin, status_code=200)
def update_assets(
    assets: Union[
        schemas.Asset,
        List[schemas.Asset],
    ],
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):

    assets = C.geom.enforce_list(assets)

    _assets = C.asset.update_assets(assets=assets, db=db, user=user)

    return {"id": [asset.id for asset in _assets]}


@router.get(
    "/assets/", dependencies=requires_auth, response_model=schemas.FeatureCollection
)
def get_assets(
    asset_query: schemas.AssetQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):

    return C.asset.get_assets(asset_query=asset_query, db=db, user=user)


@router.post("/companies/", dependencies=requires_admin, status_code=200)
def post_companies(
    company_create: schemas.CompanyCreate,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return {"id": C.asset.create_company(company_create, db, user).id}


@router.post("/companies/update/", dependencies=requires_admin, status_code=200)
def update_companies(
    company: schemas.Company,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return {"id": C.asset.update_company(company, db, user).id}


@router.get(
    "/companies/", dependencies=requires_auth, response_model=schemas.CompanyQueryReturn
)
def get_companies(
    company_query: schemas.CompanyQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):

    return C.asset.get_companies(company_query, db, user)


@router.post("/delete/", dependencies=requires_admin, status_code=200)
def delete_objs(
    delete_query: schemas.DeleteObj,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return {
        "dropped ids": C.geom.delete_objects(
            delete_query=delete_query, db=db, user=user
        )
    }
