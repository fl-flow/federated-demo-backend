import os
import time
import random
from typing import Any
from loguru import logger
from sqlalchemy.orm import Session

from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, Depends, HTTPException, Header, Request, UploadFile, File, Form, Query


from dashboard.app.api import deps
from dashboard.app.core import security
from dashboard.db import cache
from dashboard.app import crud, models, schemas
from dashboard.app.resources import strings as base
from dashboard.app.api.deps import APIVERIFY
from dashboard.app.common.utils import get_authorization_scheme_param, get_token

router = APIRouter()



#注册普通用户
@router.post("/register")
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.CommonUserCreate,
) -> Any:
    user = crud.user.get_by_email(db, phoneNumber= user_in.userEmail)
    if user:
        raise HTTPException(
            status_code=402,
            detail="该邮箱已存在",
        )
    user_in = crud.user.create(db, obj_in=user_in)
    if not user_in:
        raise HTTPException(status_code=501, detail="创建失败")
    return {'code': 201, 'msg': 'successful'}



#新增用户
@router.post("/newuser", dependencies=[Depends(APIVERIFY("CreateNewUser"))])
async def create_newuser(
    *,
    Authorization: str = Header(None),
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserAddUser,
) -> Any:
    token = get_token(Authorization)
    _info = {item: user_in.dict()[item] for item in user_in.dict() if user_in.dict()[item]}
    user = crud.user.get_by_email(db, phoneNumber= user_in.userEmail)
    if user:
        raise HTTPException(status_code=402, detail="该手机用户名已创建")

    user_login_id = cache.get(token)
    user_in = user_in.dict()
    user_in['ownerUser'] = int(user_login_id)
    user_obj, middle_list = crud.user.create_newuser(db= db, obj_in= user_in)
    return {'code': 201, 'msg': 'successful'}


#个人详情
@router.get("/", dependencies=[Depends(APIVERIFY())])
async def read_users(
    db: Session = Depends(deps.get_db),
    Authorization: str = Header(None),
) -> Any:
    token = get_token(Authorization)
    login_userid = cache.get(token)
    login_users_dict = (crud.user.get(db, login_userid)).to_dict()
    roles_users_sets = db.query(models.UsersRoles).filter_by(userId=login_userid).all()
    rolesIds = [item.rolesId for item in roles_users_sets]
    roles_sets = db.query(models.Roles).filter(models.Roles.id.in_(rolesIds)).all()
    login_users_dict['roles'] = [item.to_dict() for item in roles_sets]

    return {'code': 200, 'msg': 'successful', 'data': login_users_dict}


#用户详情
@router.get("/{id}", dependencies=[Depends(APIVERIFY())])
async def read_users(
    id: int,
    db: Session = Depends(deps.get_db)
) -> Any:
    login_users_dict = (crud.user.get(db, id)).to_dict()
    roles_users_sets = db.query(models.UsersRoles).filter_by(userId=id).all()
    rolesIds = [item.rolesId for item in roles_users_sets]
    roles_sets = db.query(models.Roles).filter(models.Roles.id.in_(rolesIds)).all()
    login_users_dict['roles'] = [item.to_dict() for item in roles_sets]

    return {'code': 200, 'msg': 'successful', 'data': login_users_dict}


#获取用户列表
@router.get("/list", dependencies=[Depends(APIVERIFY())])
async def get_user_list(
                        *,
                        db: Session = Depends(deps.get_db),
                        order_by: str = '-id',
                        page: int = 1,
                        page_size: int = 10,
                        realName: str = None,
                        phoneNumber: str = None,
                        userEmail: str = None,
                        flag: int = None) -> Any:
    """查看用户列表"""
    info = {
        'page': page,
        'page_size': page_size,
        'order_by': order_by,
        'like': {
            'realName': realName,
            'phoneNumber': phoneNumber,
            'userEmail': userEmail
        }
    }
    data_list, querys_count = crud.user.get_filter(db, query_info=info, flag=flag)
    return {'code': 200, 'msg': 'successful', 'data': data_list, 'page': page, 'page_size': page_size, "query_total": querys_count}


#重置密码；只需传用户id
@router.put("/{id}/pwd/reset", dependencies=[Depends(APIVERIFY("ResetPwd"))])
async def update_user_me(
    id: int,
    Authorization: str = Header(None),
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    token = get_token(Authorization)
    user_id = cache.get(token)
    user_obj = crud.user.get(db, id=int(user_id))
    alter_user_obj = crud.user.get(db, id=int(id))
    if not alter_user_obj:
        raise HTTPException(status_code=404, detail="无此用户")
    if not user_obj.superuser and user_id != id:
        raise HTTPException(status_code=400, detail="无权限访问")
    original_pwd = alter_user_obj.phoneNumber
    realName = alter_user_obj.realName
    new_user_obj = crud.user.update_(db= db, info={'info': {'id': id, 'password': original_pwd}})
    if not new_user_obj:
        raise HTTPException(status_code=502, detail="修改失败")




#put用户信息 传旧密码和新密码,
#旧密码不对
#(token保存时间只有三个小时);
@router.put("/{id}/pwd/set", dependencies=[Depends(APIVERIFY("UpdatePwd"))])
async def update_user_me(
    id: int,
    Authorization: str = Header(None),
    *,
    db: Session = Depends(deps.get_db),
    user: schemas.UserUpdatePwd
) -> Any:
    t_type, token = get_authorization_scheme_param(Authorization)
    user_id = cache.get(token)
    user_obj = crud.user.get(db, id=int(user_id))
    alter_user_obj = crud.user.get(db, id=int(id))
    if not alter_user_obj:
        raise HTTPException(status_code= 404, detail= "无此用户")
    if user_obj.superuser != 1 and int(user_id) != int(id):
        raise HTTPException(status_code=407, detail="无权限操作")
    check_pwd = security.YunAuthJWT().verify_password(plain_password=user.password, hashed_password=user_obj.password)
    if not check_pwd:
        raise HTTPException(status_code=404, detail="原密码错误")
    new_user_obj = crud.user.update_(db= db, info={'info': {'id': id, 'password': user.new_password}})
    if not new_user_obj:
        raise HTTPException(status_code=502, detail="修改失败")

#修改个人资料
@router.put("/{id}", dependencies=[Depends(APIVERIFY("UpdateUserData"))])
async def update_user_me(
    id: int,
    Authorization: str = Header(None),
    *,
    request: Request,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserUpdate
) -> Any:
    t_type, token = get_authorization_scheme_param(Authorization)
    user_id = cache.get(token)
    user_obj = crud.user.get(db, id=int(user_id))
    alter_user_obj = crud.user.get(db, id=int(id))
    if user_obj.superuser != 1 and int(user_id) != int(id):
        raise HTTPException(status_code=407, detail="无权限操作")
    if not alter_user_obj:
        raise HTTPException(
            status_code= 404,
            detail= "无此用户",
        )
    if user_in.flag and user_in.flag not in base.Users_status_list:
        raise HTTPException(
            status_code= 400,
            detail= "请检查修改的状态是否正确",
        )

    user_info_dict = user_in.dict()
    user_info_dict['id'] = id
    new_user_obj = crud.user.update_(db= db, info={'info': user_info_dict})
    if not new_user_obj:
        raise HTTPException(status_code=502, detail="修改失败")

#审核注册用户
@router.put("/check/{id}", dependencies=[Depends(APIVERIFY("CheckUsers"))])
async def update_user_me(
    id: int,
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.CheckUser
) -> Any:
    if user_in.flag not in base.Users_status_list:
        raise HTTPException(status_code=404, detail="状态不合法")
    user_obj = crud.user.get(db, id=id)
    if not user_obj:
        raise HTTPException(status_code=404, detail="无此用户")
    new_user_obj = crud.user.update_(db=db, info={'info': {'id': id, 'flag': user_in.flag}})
    if not new_user_obj:
        raise HTTPException(status_code=502, detail="修改失败")


#注册用户审核列表审核列表
@router.post("/applyfor", dependencies=[Depends(APIVERIFY("CheckUsersList"))])
async def superuser_check_userlist(
    *,
    db: Session = Depends(deps.get_db),
    query_info: schemas.UserListQuery = None
):
    flag = query_info.flag if query_info and query_info.flag else 3
    user_sets = db.query(models.Users).filter_by(flag=flag).all()
    user_list = [item.to_dict() for item in user_sets]
    data = [(schemas.UserOut(**item)).dict() for item in user_list]
    querys_count = len(data)
    return {'code': 200, 'msg': 'successful', 'data': data, "query_total": querys_count}
