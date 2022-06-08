from datetime import timedelta
from typing import List, Union

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from oxeo.api.controllers import authentication as auth
from oxeo.api.controllers import geom
from oxeo.api.models import database, schemas

router = APIRouter()


requires_auth = [Depends(auth.get_current_active_user)]
admin_checker = auth.RoleChecker(["admin"])
requires_admin = [Depends(auth.get_current_active_user), Depends(admin_checker)]


@router.get("/")
async def redirect():
    response = RedirectResponse(url="/docs#")
    return response


@router.post("/auth/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(database.get_db),
):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=10)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user, role="user")


@router.get("/users/", dependencies=requires_auth, response_model=schemas.User)
def read_users(
    db: Session = Depends(database.get_db),
    user: database.User = Depends(auth.get_current_active_user),
):
    user = dict(id=user.id, role=user.role, email=user.email, is_active=user.is_active)

    return user


@router.post("/aoi/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED)
def post_aoi(
    aoi: schemas.Feature,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(auth.get_current_active_user),
):
    created_aoi = geom.create_aoi(db=db, aoi=aoi, user=user)
    return {"id": created_aoi.id}


@router.get(
    "/aoi/",
    dependencies=requires_auth,
    response_model=Union[schemas.Feature, schemas.FeatureCollection],
)
def get_aoi(
    aoi_query: schemas.AOIQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(auth.get_current_active_user),
):
    return geom.get_aoi(aoi_query=aoi_query, db=db, user=user)


@router.post(
    "/events/", dependencies=requires_admin, status_code=status.HTTP_201_CREATED
)
def post_events(
    events: Union[schemas.EventCreate, List[schemas.EventCreate]],
    db: Session = Depends(database.get_db),
    user: database.User = Depends(auth.get_current_active_user),
):
    if isinstance(events, schemas.EventCreate):
        events = [events]

    created_events = geom.create_events(events=events, db=db, user=user)

    return {"id": [event.id for event in created_events]}


@router.get(
    "/events/", dependencies=requires_auth, response_model=schemas.EventQueryReturn
)
def get_events(
    event_query: schemas.EventQuery,
    db: Session = Depends(database.get_db),
    user: database.User = Depends(auth.get_current_active_user),
):
    return geom.get_events(event_query=event_query, db=db, user=user)
