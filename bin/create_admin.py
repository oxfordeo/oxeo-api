import getpass

import click
from fastapi import HTTPException

from oxeo.api.controllers import authentication as auth
from oxeo.api.models import database, schemas


@click.command()
@click.argument("email", type=click.STRING)
def create_user(email):

    password = getpass.getpass()
    if len(password) < 8:
        exit("A minimum of 8 characters is required for a password.")
    password_verify = getpass.getpass()
    if password != password_verify:
        exit("ERROR: Passwords must match.")

    user = schemas.UserCreate(email=email, password=password)

    _create_user(user)


def _create_user(user: schemas.UserCreate):

    db = next(database.get_db())

    db_user = auth.get_user(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return auth.create_user(db=db, user=user, role="admin")


if __name__ == "__main__":
    create_user()
