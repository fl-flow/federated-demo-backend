import re
from typing import Optional
from fastapi import UploadFile, File, Query, HTTPException
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime


class Token(BaseModel):
    # token_type: str = "bearer"
    # access_token: str
    token: str

#login
class UserLogin(BaseModel):
    username: Optional[str] = Query(..., max_length=11, min_length=11, regex=None)
    password: str


# Properties to receive via API on creation
class UserCreateBase(BaseModel):
    realName: str
    gender: str
    userEmail: EmailStr
    superuser: int = 0
    flag: int = 0
    @validator('gender')
    def password_check(cls, v):
        if v is not None and len(v) > 0:
            if v not in ["男", "女"]:
                raise ValueError('性别错误')
        return v.title()


# Properties to receive via API on update
class UserCreate(UserCreateBase):
    password: str

    @validator('password')
    def password_check(cls, v):
        if v is not None and len(v) > 0:
            if ' ' in v:
                raise ValueError('密码里面不允许用空格')
            if re.match("^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", v)==None:
                raise ValueError('密码必须包含大小写字母及数字')
        return v


class UserInDBBase(UserCreate):
    id: Optional[int] = None

    class Config:
        orm_mode = True


class SuperuserCrete(UserCreate):
    superuser: int = 1

class CommonUserCreate(BaseModel):
    realName: str
    gender: str
    userEmail: EmailStr
    superuser: int = 0
    flag: int = 3
    phoneNumber: str=None
    password: str
    @validator('password')
    def password_check(cls, v):
        if v is not None and len(v) > 0:
            if ' ' in v:
                raise ValueError('密码里面不允许用空格')
            if re.match("^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", v)==None:
                raise ValueError('密码必须包含大小写字母及数字')
        return v

# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str


class UserUpdatePwd(BaseModel):
    password: str=None
    new_password: str

    @validator('new_password')
    def password_check(cls, v):
        if v is not None and len(v) > 0:
            if ' ' in v:
                raise ValueError('密码里面不允许用空格')
            if re.match("^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", v)==None:
                raise ValueError('密码必须包含大小写字母及数字')
        return v

class UserUpdate(BaseModel):
    userEmail: Optional[EmailStr] = None
    realName: Optional[str] = None
    gender: Optional[str] = None
    flag:  Optional[int] = None
    roles: Optional[list] = None

class CheckUser(BaseModel):
    flag: int



class UserOut(BaseModel):
    realName: str
    userEmail: str = None
    phoneNumber: str
    hospital: str= None
    department: str= None
    flag: int
    gender: str
    orgname_list: list = None
    rolename_list: list = None
    id: int
    otherContact: str = None
    jobNumber: str= None
    intentionOrg: str = None

class UserReleteOut(BaseModel):
    realName: str
    userEmail: EmailStr= None
    hospital: str= None
    department: str= None
    create_time: str= None


#新增用户模型
class UserAddUser(BaseModel):
    """
    用户基本信息,
    角色id[],
    """
    realName: str
    gender: str
    userEmail: EmailStr
    superuser: int = 0
    flag: int = 3
    phoneNumber: str=None
    password: str
    roles: list=[]
    @validator('password')
    def password_check(cls, v):
        if v is not None and len(v) > 0:
            if ' ' in v:
                raise ValueError('密码里面不允许用空格')
            if re.match("^(?:(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])).*$", v)==None:
                raise ValueError('密码必须包含大小写字母及数字')
        return v


class OrgUserReturn(BaseModel):
    id: int
    code: str
    title: str
    class Config:
        orm_mode = True


class UserListQuery(BaseModel):
    phoneNumber: str = None
    userEmail: str = None
    realName: str = None
    gender: str = None
    flag: int = None

class UserUpdateOwner(BaseModel):
    id: int
    realName: Optional[EmailStr] = None
    hospital: Optional[str] = None
    department: Optional[str] = None
    otherContact: Optional[str] = None
    expertImage: Optional[str] = None
    phoneNumber: Optional[str] = None
    Roles_list: list
    # org_code: Optional[str] = None


class UserRecordsList(BaseModel):
    create_st: Optional[str] = None
    create_et: Optional[str] = None
    return_code: Optional[str] = None
