# oxeo/api/models/tables.py
import os

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String, create_engine
from sqlalchemy.dialects.postgresql import ARRAY, ENUM, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DB_USER = os.environ.get("PG_DB_USER")
DB_PW = os.environ.get("PG_DB_PW")
DB_HOST = os.environ.get("PG_DB_HOST")
DB_NAME = os.environ.get("PG_DB_NAME")


SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PW}@{DB_HOST}/{DB_NAME}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

VALID_ROLES = ("user", "admin")
VALID_AOI_LABELS = ("waterbody", "agricultural_area", "basin", "admin_area")
VALID_EVENT_LABELS = ("ndvi", "water_extents", "soil_moisture", "prediction")
VALID_ASSET_LABELS = ("mine", "power_station")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(ENUM(*VALID_ROLES, name="role"))
    data = Column(JSONB)


class AOI(Base):

    __tablename__ = "aois"

    id = Column(Integer, primary_key=True, index=True)
    geometry = Column(Geometry(geometry_type="MultiPolygon", srid=4326))
    labels = Column(ARRAY(ENUM(*VALID_AOI_LABELS, name="AOILabel")), index=True)
    properties = Column(JSONB)


class Events(Base):

    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    labels = Column(ARRAY(ENUM(*VALID_EVENT_LABELS, name="EventLabel")), index=True)
    aoi_id = Column(Integer, ForeignKey("aois.id"))
    datetime = Column(Date, index=True)
    properties = Column(JSONB)

    # aoi = relationship("AOI", back_populates="events")


class Asset(Base):

    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    geometry = Column(Geometry(geometry_type="Point", srid=4326))
    name = Column(String, unique=True)
    labels = Column(ARRAY(ENUM(*VALID_ASSET_LABELS, name="AssetLabel")), index=True)
    properties = Column(JSONB)
    company = relationship("Company", secondary="asset_company_link")


class Company(Base):

    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    assets = relationship("Asset", secondary="asset_company_link")
    properties = Column(JSONB)


class AssetCompany(Base):

    __tablename__ = "asset_company_link"
    company_id = Column(Integer, ForeignKey("companies.id"), primary_key=True)
    asset_id = Column(Integer, ForeignKey("assets.id"), primary_key=True)
    properties = Column(JSONB)  # ownership percentages and such
