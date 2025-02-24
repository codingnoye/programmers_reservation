import hashlib
import os
import binascii
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(stored_password: str, provided_password: str) -> bool:
    return pwd_context.verify(provided_password, stored_password)