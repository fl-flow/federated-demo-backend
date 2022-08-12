from sqlalchemy.orm import Session
from dashboard.app.api import deps
from dashboard.app.api.deps import APIVERIFY, APIVERIFYSUPER
from fastapi import APIRouter, Depends, HTTPException
from dashboard.app import crud, schemas

router = APIRouter()


#创建权限
@router.post("/", dependencies=[Depends(APIVERIFYSUPER())])
def auth_add(
    *,
    db: Session = Depends(deps.get_db),
    auth_info: schemas.PermissionsCreate
):

    obj = crud.crud_per.get_title(db= db, title= auth_info.title)
    if obj:
        raise HTTPException(status_code=404, detail="此权限已存在")
    auth_in = crud.crud_per.create_(db, obj_in=auth_info)
    if not auth_in:
        raise HTTPException(status_code=501, detail="创建失败")
    return {'code': 201, 'msg': '创建成功'}

#权限列表
@router.get("/list", dependencies=[Depends(APIVERIFY("PermissionsList"))])
def auth_list(
    page: int = 1,
    page_size: int = 10,
    order_by: str = 'id', #'-id' 如有 - 号为降序 从大到小
    like: int = 0, #传1 or 0
    *,
    db: Session = Depends(deps.get_db),
    title: str=None,
    key: str=None
):
    info = {'and': {'title': title, 'key': key}, 'page': page, 'page_size': page_size, 'order_by': order_by, 'like': like}
    obj_list, querys_count = crud.crud_per.get_filter(db=db, query_info=info)
    if not obj_list:
        raise HTTPException(status_code=404, detail="搜索不到")
    return {'code': 200, 'msg': '修改成功', 'data': obj_list, 'page': page, 'page_size': page_size, 'query_total': querys_count}


#权限详情
@router.get("/{key}", dependencies=[Depends(APIVERIFYSUPER())])
def auth_detail(
    key: str,
    db: Session = Depends(deps.get_db)
    ):
    obj = crud.crud_per.get_(db= db, key= key)
    if not obj:
        raise HTTPException(status_code=404, detail="搜索不到")
    return {'code': 200, 'msg': 'successful', 'data': obj.to_dict()}


#权限修改
@router.put("/{key}", dependencies=[Depends(APIVERIFYSUPER())])
def auth_update(
    key: str,
    *,
    db: Session = Depends(deps.get_db),
    per_info: schemas.PermissionsUpdate):
    if not per_info:
        raise HTTPException(status_code=404, detail="请传入数据")
    obj = crud.crud_per.get_(db= db, key= key)
    if not obj:
        raise HTTPException(status_code= 404, detail= "查无此权限id")
    per_info_dict = per_info.dict()
    per_info_dict['id'] = obj.id
    auth_in = crud.crud_per.update_(db= db, info= per_info_dict)
    if auth_in == None:
        raise HTTPException(status_code=500, detail="修改失败")
    return {'code': 200, 'msg': '修改成功'}


#删除权限信息及其关系数据
@router.delete("/{key}", dependencies=[Depends(APIVERIFYSUPER())])
def auth_delete(
    key: str,
    *,
    db: Session = Depends(deps.get_db)):
    obj = crud.crud_per.get_(db= db, key= key)
    if not obj:
        raise HTTPException(status_code= 404, detail= "查无此id")
    results = crud.crud_per.delete_(db= db, id= obj.id)
    if not results:
        raise HTTPException(status_code=501, detail="删除失败")
    return {'code': 200, 'msg': '删除成功'}
