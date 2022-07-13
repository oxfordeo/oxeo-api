import os
import uuid
from datetime import datetime, timedelta
from typing import List, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jose import JWTError, jwt
from loguru import logger
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from oxeo.api.models import database, schemas

SECRET_KEY = os.environ.get("SERVER_SECRET")
ALGORITHM = os.environ.get("SERVER_ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# default to dummy data to pass CI
mail_cfg = ConnectionConfig(
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME", "demo@oxfordeo.com"),
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD", "demopass"),
    MAIL_FROM=os.environ.get("MAIL_FROM_EMAIL", "demo@oxfordeo.com"),
    MAIL_PORT=587,
    MAIL_SERVER=os.environ.get("MAIL_SERVER", "a_mail_server"),
    MAIL_FROM_NAME=os.environ.get("MAIL_FROM_NAME", "demo@oxfordeo.com"),
    MAIL_TLS=True,
    MAIL_SSL=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, email: str):
    return db.query(database.User).filter(database.User.email == email).first()


def authenticate_user(db, email: str, password: str):
    user = get_user(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_reset_token(db: Session, reset_token: schemas.ResetPassword):

    #
    Q = db.query(database.PasswordResetToken)
    Q = Q.filter(database.PasswordResetToken.reset_token == reset_token.reset_token)
    Q = Q.filter(database.PasswordResetToken.status == True)  # noqa
    db_token = Q.first()

    if db_token is None:
        raise HTTPException(status_code=400, detail="No valid tokens found!")

    if db_token.create_datetime < datetime.now() - timedelta(hours=72):
        raise HTTPException(
            status_code=400,
            detail="Password reset token expired. Tokens are valid 72 hours.",
        )

    return db_token


def reset_password(
    db: Session,
    reset_token: schemas.ResetPassword,
    db_user: database.User,
    db_token: database.PasswordResetToken,
):
    hashed_password = get_password_hash(reset_token.new_password)
    db_user.hashed_password = hashed_password
    db.commit()
    db.refresh(db_user)

    db_token.status = False
    db.commit()

    return db_user


def create_pwreset_token(db: Session, user: database.User):

    # only can have one token at a time.
    existing_tokens = (
        db.query(database.PasswordResetToken)
        .filter(database.PasswordResetToken.email == user.email)
        .all()
    )
    for token in existing_tokens:
        token.status = False
    db.commit()

    # create a pw reset token
    reset_token = str(uuid.uuid1())

    db_token = database.PasswordResetToken(
        email=user.email,
        reset_token=reset_token,
        status=True,
        create_datetime=datetime.now(),
    )
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return db_token


async def email_pw_reset(token: database.PasswordResetToken, user: database.User):

    fm = FastMail(mail_cfg)

    message = "".join(
        [
            "<!DOCTYPE html>",
            "<html>",
            "<title>Reset Password</title>",
            "<body>",
            '<div style="width:100%;font-family: monospace;">',
            f"<h1> Hi {token.email}!</h1>",
            "<p>Someone has requested a link to reset your password. If you requested ",
            "this, you can change your password with this token: ",
            f"{token.reset_token}.</p>",
            "<p> Use this token to POST https://api.oxfordeo.com/auth/reset_password/ ",
            f"with the following json: {{'reset_token':'{token.reset_token}',",
            "'new_password':'YOUR-NEW-PASSWORD',",
            "'confirm_password':'YOUR-NEW-PASSWORD'}.</p>",
            "<p>If you didn't request this, you can ignore this email.</p>",
            "<p>Your password won't change until you access the link above ",
            "and submit a new one.</p>",
            "</div>",
            "</body>",
            "</html>",
        ]
    )

    message = MessageSchema(
        subject="OxEO Password Reset",
        recipients=[token.email],
        body=message,
        subtype="html",
    )

    fm = FastMail(mail_cfg)
    await fm.send_message(message)

    return f"Password reset instructions sent to {token.email}!"


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


class RoleChecker:
    def __init__(self, allowed_roles: List):
        self.allowed_roles = allowed_roles

    def __call__(self, user: schemas.User = Depends(get_current_active_user)):
        if user.role not in self.allowed_roles:
            logger.debug(f"User with role {user.role} not in {self.allowed_roles}")
            raise HTTPException(status_code=403, detail="Operation not permitted")


def create_user(db: Session, user: schemas.UserCreate, role: str):
    hashed_password = get_password_hash(user.password)
    print("CREAT_USER")
    print(hashed_password)
    db_user = database.User(
        email=user.email, hashed_password=hashed_password, role=role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
