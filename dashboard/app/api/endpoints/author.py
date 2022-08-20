from typing import Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query
from dashboard.db import cache
from dashboard.app.api import deps
from dashboard.app.api.deps import APIVERIFY
from dashboard.app import crud, models, schemas
from dashboard.app.common.utils import get_token


router = APIRouter()

@router.post("/",  dependencies=[Depends(APIVERIFY("AuthCreate"))], summary="授权码申请")
def auth_add(
    *,
    db: Session = Depends(deps.get_db),
    info_in: schemas.AuthCreate,
) -> Any:
    obj = crud.crud_auth.get_(db, info_in.appKey)
    if obj:
        raise HTTPException(status_code=402, detail="同名授权key已创建")

    auth_in = crud.crud_auth.create_(db, obj_in=info_in)
    if not auth_in:
        raise HTTPException(status_code=501, detail="创建失败")
    return {'code': 201, 'msg': 'successful'}


@router.get("/{id}",  dependencies=[Depends(APIVERIFY("AuthGet"))])
def auth_detail(
    id: int,
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    obj = crud.crud_auth.get(db, id)
    if not obj:
        raise HTTPException(status_code=404, detail="查找不到此授权key")
    return {'code': 200, 'msg': 'successful', 'data': obj.to_dict()}



@router.get("/list/",  dependencies=[Depends(APIVERIFY("AuthGet"))])
def auth_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10),
    order_by: str = 'id', #'-id' 如有 - 号为降序 从大到小
    like: int = 0, #传1 or 0,
    appKey: str = None,
    *,
    db: Session = Depends(deps.get_db)
):
    info = {'and': {'appKey': appKey}, 'page': page, 'page_size': page_size, 'order_by': order_by, 'like': like}
    obj_list, querys_count = crud.crud_auth.get_filter(db=db, query_info=info)
    return {'code': 200, 'msg': 'successful', 'data': obj_list, 'page': page, 'page_size': page_size, "query_total": querys_count}



@router.put("/{id}", dependencies=[Depends(APIVERIFY("AuthUpdate"))], summary="授权码修改")
def auth_update(
    id: int,
    *,
    db: Session = Depends(deps.get_db),
    auth_info: schemas.AuthUpdate):
    obj = crud.crud_role.get(db=db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="查无此id")
    if auth_info.appKey:
        obj = crud.crud_auth.get_(db, auth_info.appKey)
        if obj.id != int(id):
            raise HTTPException(status_code=401, detail="同名授权key已存在")
    auth_info_dict = auth_info.dict()
    auth_info_dict['id'] = id
    results = crud.crud_auth.update_(db=db, info=auth_info_dict)
    if not results:
        raise HTTPException(status_code=501, detail="修改失败")
    return {'code': 200, 'msg': '修改成功'}


@router.delete("/{id}", dependencies=[Depends(APIVERIFY("AuthDelete"))], summary="授权码删除")
def auth_delete(
    id: int,
    *,
    db: Session = Depends(deps.get_db)):
    obj = crud.crud_auth.get(db=db, id=id)
    if not obj:
        raise HTTPException(status_code=404, detail="查无此id")
    results = crud.crud_auth.remove(db=db, id=id)
    if not results:
        raise HTTPException(status_code=501, detail="删除失败")
    return {'code': 200, 'msg': '删除成功'}


