from typing import Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Request, Header, Query
from dashboard.db import cache
from dashboard.app.api import deps
from dashboard.app.api.deps import APIVERIFY
from dashboard.app import crud, models, schemas
from dashboard.app.common.utils import get_token


router = APIRouter()

#创建角色
@router.post("/",  dependencies=[Depends(APIVERIFY("CreateRoles"))])
def Roles_add(
    *,
    db: Session = Depends(deps.get_db),
    role_in: schemas.RoleCreate,
) -> Any:
    obj = db.query(models.Roles).filter(models.Roles.title == role_in.title).first()
    if obj:
        raise HTTPException(status_code=402, detail="同名角色已创建")
    if len(role_in.pers_list) > 0:
        for item in role_in.pers_list:
            per_obj = crud.crud_per.get(db= db, id= int(item))
            if not per_obj:
                raise HTTPException(status_code=404, detail="无此({})id权限".format(item))
    Role_in = crud.crud_role.create(db, obj_in=role_in)
    if not Role_in:
        raise HTTPException(status_code=501, detail="创建失败")
    return {'code': 201, 'msg': 'successful'}



#角色详情
@router.get("/{id}",  dependencies=[Depends(APIVERIFY("RolesDetail"))])
def role_detail(
    id: int,
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    obj = db.query(models.Roles).filter(models.Roles.id== id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="查找不到此角色")
    role_info = obj.to_dict()
    per_dict_list = crud.crud_role.get_relation_per(db, role_info)
    role_info['per_info'] = per_dict_list
    return {'code': 200, 'msg': 'successful', 'data': role_info}



@router.get("/list/",  dependencies=[Depends(APIVERIFY("RolesList"))])
def role_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10),
    order_by: str = 'id', #'-id' 如有 - 号为降序 从大到小
    like: int = 0, #传1 or 0,
    title: str = None,
    *,
    db: Session = Depends(deps.get_db)
):
    info = {'and': {'title': title}, 'page': page, 'page_size': page_size, 'order_by': order_by, 'like': like}
    obj_list, querys_count = crud.crud_role.get_filter(db=db, query_info=info)
    for item in obj_list:
        per_dict_list = crud.crud_role.get_relation_per(db, item)
        item['per_info'] = per_dict_list
    return {'code': 200, 'msg': 'successful', 'data': obj_list, 'page': page, 'page_size': page_size, "query_total": querys_count}


#修改角色信息
@router.put("/{id}", dependencies=[Depends(APIVERIFY("UpdateRoles"))])
def role_update(
    id: int,
    *,
    db: Session = Depends(deps.get_db),
    role_info: schemas.RoleUpdate):
    obj = crud.crud_role.get(db=db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="查无此id")
    if role_info.title:
        title_obj = db.query(models.Roles).filter_by(title=role_info.title).first()
        if title_obj:
            raise HTTPException(status_code=401, detail="同名角色已存在")
    if role_info.pers_list and len(role_info.pers_list) > 0:
        for item in role_info.pers_list:
            per_obj = crud.crud_per.get(db=db, id=int(item))
            if not per_obj:
                raise HTTPException(status_code=404, detail="无此({})id权限".format(item))
    role_info_dict = role_info.dict()
    role_info_dict['id'] = id
    results = crud.crud_role.update_(db=db, info=role_info_dict)
    if not results:
        raise HTTPException(status_code=501, detail="修改失败")
    return {'code': 200, 'msg': '修改成功'}


#删除角色信息及其与权限关系
@router.delete("/{id}", dependencies=[Depends(APIVERIFY("DeleteRoles"))])
def role_delete(
    id: int,
    *,
    db: Session = Depends(deps.get_db)):
    obj = crud.crud_role.get(db=db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="查无此id")
    results = crud.crud_role.delete_(db=db, id=id)
    if not results:
        raise HTTPException(status_code=501, detail="删除失败")
    return {'code': 200, 'msg': '删除成功'}


