import json, os
import shutil
from typing import Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Header, Request, Query, File, UploadFile
from sqlalchemy.orm import Session
from dashboard.app.core.config import settings
from dashboard.app import crud, models, schemas
from dashboard.app.core.security import YunAuthJWT
from dashboard.app.api.deps import APIVERIFY, get_db
from dashboard.app.common.utils import get_token, CustUploadFile
from dashboard.app.resources import strings as base

router = APIRouter()

#节点信息上传
@router.post("/upload", dependencies=[Depends(APIVERIFY("NodeUpload"))], summary="节点信息上传")
def node_load(
    db: Session = Depends(get_db),
    *,
    file: UploadFile = File(...)
):
    file_read = file.file.read()
    data = json.loads(file_read)
    appKey = data['appkey']
    appkey_obj = crud.crud_auth.get_(db, appKey)
    if not appkey_obj:
        raise HTTPException(status_code=400, detail="授权信息不合法")
    if not data['appSecret']:
        raise HTTPException(status_code=400, detail="请填写密钥")
    nodeName = data['nodeName']
    db_obj = db.query(models.WebsitNode).filter_by(nodeName=nodeName).first()
    if db_obj:
        raise HTTPException(status_code=401, detail="{}已存在".format(nodeName))
    check_pwd = YunAuthJWT().verify_password(plain_password=data['appSecret'], hashed_password=appkey_obj.appSecret)
    if not check_pwd:
        raise HTTPException(status_code=400, detail="授权密钥不合法")
    key = data['nodeName']
    obj_in = schemas.NodeCreate(**data)
    return_in = crud.crud_node.create_(db=db, obj_in=obj_in)
    net_node_path = CustUploadFile.upload(file=file, file_read=file_read, save_path='/node',
                                          p_name=key)
    return {"code": 201, "msg": "successful"}



@router.post("/", dependencies=[Depends(APIVERIFY("NodeCreate"))], summary="节点创建")
def node_create(
    request: Request,
    Authorization: str = Header(None),
    *,
    db: Session = Depends(get_db),
    node_in: schemas.NodeCreate,
) -> Any:
    token = get_token(Authorization)
    appkey_obj = crud.crud_auth.get_(db, node_in.appKey)
    if not appkey_obj:
        raise HTTPException(status_code=400, detail="授权信息不合法")
    obj = db.query(models.WebsitNode).filter_by(title= node_in.nodeName).first()
    if obj:
        raise HTTPException(status_code=402, detail="此节点已存在")
    else:
        return_in = crud.crud_node.create_(db=db, obj_in= node_in.dict())
        if not return_in:
            raise HTTPException(status_code=501, detail="创建失败")
    return {'code': 201, 'msg': '创建成功'}


@router.get("/list", dependencies=[Depends(APIVERIFY("NodeGet"))])
def node_list(
    Authorization: str = Header(None),
    Cookies: str = Header(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=10),
    order_by: str = 'id', #'-id' 如有 - 号为降序 从大到小
    like: int = 0, #传1 or 0
    *,
    db: Session = Depends(get_db),
    code: str = None,
    nodeName: str = None,
    flag: int = None,

):
    info = {'page': page, 'page_size': page_size, 'order_by': order_by,
            'like': like}
    info['and'] = {'code': code, 'nodeName': nodeName}
    obj_list, querys_count = crud.crud_node.get_filter(db=db, query_info=info, flag=flag)

    return {'code': 200, 'msg': 'successful', 'data': obj_list, 'page': page, 'page_size': page_size, 'query_total': querys_count}


@router.put("/{code}", dependencies=[Depends(APIVERIFY("NodeUpdate"))], summary="节点信息修改")
def node_update(
    code: str,
    request: Request,
    Authorization: str = Header(None),
    *,
    db: Session = Depends(get_db),
    node_info: schemas.NodeUpdate=None):
    if not node_info:
        raise HTTPException(status_code=404, detail="请传入数据")
    obj = crud.crud_node.get_(db=db, code=code)
    if not obj:
        raise HTTPException(status_code=404, detail="查无此节点code")

    org_dict = node_info.dict()
    org_dict['id'] = obj.id
    node_in = crud.crud_node.update_(db= db, info= org_dict)
    if not node_in:
        raise HTTPException(status_code=502, detail="修改失败")
    return {'code': 200, 'msg': '修改成功'}


@router.get("/{code}", dependencies=[Depends(APIVERIFY("NodeGet"))])
def nodes_detail(
    code: str,
    db: Session = Depends(get_db)):
    obj = crud.crud_node.get_(db=db, code=code)
    if not obj:
        raise HTTPException(status_code=404, detail="查找不到此节点数据")
    data = obj.to_dict()
    return {'code': 200, 'msg': 'successful', 'data': data}

#节点信息下载
@router.get("/down/{code}", dependencies=[Depends(APIVERIFY("NodeDown"))], summary="节点信息下载")
def nodes_load(
    code: str,
    Authorization: str = Header(None),
    db: Session = Depends(get_db)):
    print(code,22222222222222)
    obj = crud.crud_node.get_(db=db, code=code)
    if obj.flag != 0:
        raise HTTPException(status_code=400, detail="站点未恢复正常")
    data = obj.to_dict()
    id = data.pop("id")
    flag = data.pop("flag")
    token = get_token(Authorization)
    data['token'] = token
    data['expirtime'] = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    now_time = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = obj.nodeName+"_"+now_time
    zip_name = (obj.code)[:6]+"_"+now_time
    file_path = base.insert_file_path+"/zip/"+zip_name+"/"+file_name+".json"
    zip_path = base.insert_file_path+"/zip/" + zip_name
    if not os.path.exists(zip_path):
        os.makedirs(zip_path)
    with open(file_path, 'w', encoding="utf-8") as f:
        f.write(json.dumps(data, indent=4, ensure_ascii=False))
    shutil.make_archive(zip_path, 'zip', zip_path)
    shutil.rmtree(zip_path)
    return {"code": 200, "msg": "successful", "data": "/zip/"+zip_name+".zip"}
