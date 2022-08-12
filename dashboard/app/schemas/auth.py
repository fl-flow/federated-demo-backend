from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AuthBase(BaseModel):
    appKey: str
    appSecret: str

class AuthCreate(AuthBase):
    remarks: str=None
    pass

class AuthUpdate(BaseModel):
    appKey: str=None
    appSecret: str=None
    remarks: str=None