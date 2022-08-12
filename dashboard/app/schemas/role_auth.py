import datetime
from fastapi import HTTPException
from pydantic import BaseModel, validator
from typing import Optional


#**********************角色**********************
class RoleBase(BaseModel):
    title: str

class RoleCreate(RoleBase):
    pers_list: list
    code: str

    @validator('pers_list')
    def check_match(cls, v, values, **kwargs):
        for item in v:
            if not isinstance(item, int) and not isinstance(item, str):
                raise HTTPException(status_code= 404, detail= "pers_list所传格式错误")
        return v



class RoleTimeRange(BaseModel):
    create_st: datetime.datetime = None
    create_et: datetime.datetime = None

class RoleDetail(RoleBase):
    title: str = None
    code: str = None

class RoleUpdate(BaseModel):
    title: Optional[str]= None
    pers_list: list = None

class RoleReturn(RoleBase):
    title: str = None
    id: int = None
    class Config:
        orm_mode = True



#**********************权限**********************

#权限
class PermissionsBase(BaseModel):
    title: str
    key: str

class PermissionsCreate(PermissionsBase):
    pass

class PermissionsUpdate(BaseModel):
    # key:str= None
    title:str= None
    pass

class PermissionsReturn(PermissionsBase):
    title: str= None
    id: int
    role_title: str= None
    class Config:
        orm_mode = True

class PermissionsDetail(BaseModel):
    title: str= None
    key: str= None


class MiddleCreate(BaseModel):
    roleId: int
    permissionId: int
    pass

