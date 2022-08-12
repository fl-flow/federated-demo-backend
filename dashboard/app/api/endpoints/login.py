from typing import Any
from loguru import logger
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Header
from dashboard.app import crud
from dashboard.app.api import deps
from dashboard.db.database import cache
from dashboard.app.api.deps import APIVERIFY
from dashboard.app.core.config import settings
from dashboard.app.schemas.user import UserLogin
from dashboard.app.resources import strings as base
from dashboard.app.core.security import YunAuthJWT
from dashboard.app.common.utils import get_token, from_redis_token

router = APIRouter()

#用户登录接口 -->返回token
@router.post("/login/access-token", tags=["Login"])
async def login_access_token(
    user_in: UserLogin,
    db: Session = Depends(deps.get_db)
) -> Any:
    form_data = user_in
    user = crud.user.get_by_phoneNumber(
        db, phoneNumber=form_data.username
    )
    if not user:
        raise HTTPException(status_code=404, detail="登录失败，未注册")
    user_info = user.to_dict()
    if user.flag != 0:
        raise HTTPException(status_code=401, detail="此账号已{}".format(base.flag_map[user.flag]))
    check_pwd = YunAuthJWT().verify_password(plain_password=form_data.password, hashed_password=user.password)
    if check_pwd:
        now_token = from_redis_token(user.id)
        if now_token:
            cache.delete(now_token)
        info_expires = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        access_token_expires = timedelta(seconds=info_expires)
        token_key = YunAuthJWT().create_token(
            user.id, expires_delta=access_token_expires, token_type="access", jti="user", userqs=user.to_dict()
        )
        if not cache.exists(token_key):
            REDIS_TIME_OUT = settings.REDIS_TIME_OUT
            set_token = cache.set(token_key, str(user.id), REDIS_TIME_OUT)
            if set_token:
                del user_info['password']
                return {
                    'code': 200,
                    'msg': '登录成功',
                    'data': {"access_token": token_key,
                    "token_type": "bearer",
                    'user_info': user_info},
                }
            else:
                logger.debug("{} token存储失败".format(user_in.username))
                raise HTTPException(status_code=401, detail="登入失败，token存储失败")


    else:
        raise HTTPException(status_code=403, detail="密码输入错误,登陆失败")


#登出接口
@router.post("/logout",dependencies=[Depends(APIVERIFY())])
async def logout(Authorization: str = Header(...)):
    token = get_token(Authorization)
    user_id = cache.exists(token)
    if not user_id:
        raise HTTPException(status_code=404, detail="登出失败,该token不正确")
    cache.delete(token)
    return {'msg': "successful", 'code': 200}
