import json
import os
from datetime import timedelta
from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import oxeo.api.controllers as C
from oxeo.api.models import bridges, database, schemas

router = APIRouter()

requires_auth = [Depends(C.auth.get_current_active_user)]
admin_checker = C.auth.RoleChecker(["admin"])
requires_admin = [Depends(C.auth.get_current_active_user), Depends(admin_checker)]


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


@router.post("/auth/token", response_model=schemas.Token, tags=["Authorisation"])
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
    access_token_expires = timedelta(minutes=30)

    access_token = C.auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/auth/forgot_password", status_code=200, tags=["Authorisation"])
async def forgot_password(
    user: schemas.UserBase,
    db: Session = Depends(database.get_db),
):
    # check that user exists
    db_user = C.auth.get_user(db, user.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found.")

    # generate a reset token
    db_reset_token = C.auth.create_pwreset_token(db, db_user)

    return await C.auth.email_pw_reset(db_reset_token, user)


@router.post("/auth/reset_password", status_code=200, tags=["Authorisation"])
async def reset_password(
    reset_password: schemas.ResetPassword, db: Session = Depends(database.get_db)
):

    if reset_password.new_password != reset_password.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords don't match!")

    db_token = C.auth.get_reset_token(db, reset_password)

    # now use it to actually reset the password
    db_user = C.auth.get_user(db, db_token.email)
    db_user = C.auth.reset_password(db, reset_password, db_user, db_token)

    return {"email": db_user.email}


@router.post(
    "/users/",
    response_model=schemas.User,
    tags=["Authorisation"],
)
def create_user(
    user: schemas.UserCreate,
    db: Session = Depends(database.get_db),
    req_user: Optional[database.User] = Depends(C.auth.maybe_get_current_active_user),
):

    print("REQ USER", req_user)

    # if requesting user is admin
    if req_user is not None:
        print("REQ USER not None")
        if req_user.role == "admin":
            db_user = C.auth.get_user(db, email=user.email)
            if db_user:
                raise HTTPException(status_code=400, detail="Email already registered")
            return C.auth.create_user(db=db, user=user, role="user")

    # else check token
    VALID_TOKENS = json.loads(os.environ.get("USER_TOKENS"))
    print(type(user.token), type(VALID_TOKENS[0]), user.token in VALID_TOKENS)
    if user.token in VALID_TOKENS:

        db_user = C.auth.get_user(db, email=user.email)
        if db_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        return C.auth.create_user(db=db, user=user, role="user")
    else:
        raise HTTPException(status_code=400, detail=f"Token {user.token} not valid.")


@router.get(
    "/users/",
    dependencies=requires_auth,
    response_model=schemas.User,
    tags=["Authorisation"],
)
def read_users(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    user = dict(id=user.id, role=user.role, email=user.email, is_active=user.is_active)

    return user


@router.post(
    "/aoi/",
    dependencies=requires_admin,
    status_code=status.HTTP_201_CREATED,
    tags=["AOIs"],
)
def post_aoi(
    aoi: schemas.Feature,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    _aoi = C.geom.create_aoi(db=db, aoi=aoi, user=user)

    return {"id": _aoi.id}


@router.post(
    "/aoi/update/",
    dependencies=requires_admin,
    status_code=status.HTTP_201_CREATED,
    tags=["AOIs"],
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
    response_model=Union[schemas.FeatureCollection, str],
    tags=["AOIs"],
)
def get_aoi(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
    aoi_query: schemas.AOIQuery = Depends(bridges.to_aoiquery),
):

    return C.geom.get_aoi(aoi_query=aoi_query, db=db, user=user)


@router.post(
    "/events/",
    dependencies=requires_admin,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"],
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
    "/events/update/",
    dependencies=requires_admin,
    status_code=status.HTTP_201_CREATED,
    tags=["Events"],
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
    "/events/",
    dependencies=requires_auth,
    response_model=schemas.EventQueryReturn,
    tags=["Events"],
)
def get_events(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
    event_query: schemas.EventQuery = Depends(bridges.to_eventquery),
):

    return C.geom.get_events(event_query=event_query, db=db, user=user)


@router.get(
    "/forecast/",
    dependencies=requires_auth,
    response_model=schemas.ForecastQueryReturn,
    tags=["Forecast"],
)
def get_forecast(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
    event_query: schemas.EventQuery = Depends(bridges.to_eventquery),
    forecast_query: schemas.ForecastQuery = Depends(bridges.to_forecastquery),
):

    return C.forecast.get_forecast(db, user, event_query, forecast_query)


@router.post("/assets/", dependencies=requires_admin, status_code=200, tags=["Assets"])
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


@router.post(
    "/assets/update/", dependencies=requires_admin, status_code=200, tags=["Assets"]
)
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
    "/assets/",
    dependencies=requires_auth,
    response_model=schemas.FeatureCollection,
    tags=["Assets"],
)
def get_assets(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
    asset_query: schemas.AssetQuery = Depends(bridges.to_assetquery),
):

    return C.asset.get_assets(asset_query=asset_query, db=db, user=user)


@router.post(
    "/companies/", dependencies=requires_admin, status_code=200, tags=["Companies"]
)
def post_companies(
    company_create: schemas.CompanyCreate,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return {"id": C.asset.create_company(company_create, db, user).id}


@router.post(
    "/companies/update/",
    dependencies=requires_admin,
    status_code=200,
    tags=["Companies"],
)
def update_companies(
    company: schemas.Company,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
):
    return {"id": C.asset.update_company(company, db, user).id}


@router.get(
    "/companies/",
    dependencies=requires_auth,
    response_model=schemas.CompanyQueryReturn,
    tags=["Companies"],
)
def get_companies(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(C.auth.get_current_active_user),
    company_query: schemas.CompanyQuery = Depends(bridges.to_companyquery),
):

    return C.asset.get_companies(company_query, db, user)


@router.post(
    "/delete/",
    dependencies=requires_admin,
    status_code=200,
    tags=["AOIs", "Events", "Assets", "Companies"],
)
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
