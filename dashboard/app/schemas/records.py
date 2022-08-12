from typing import Optional
import datetime
from pydantic import BaseModel


#******************************UsersRecords******************************

class UsersRecordsBase(BaseModel):
    userId: int
    path: str
    methodType: str
    module: str
    userName: str
    phoneNumber: str

