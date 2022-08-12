from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status, Request, Header
from jose import jwt
from datetime import datetime
from pydantic import ValidationError
from sqlalchemy.orm import Session
from dashboard.app.resources import strings as base
from dashboard.app import crud, models, schemas
from dashboard.app.core.config import settings
from dashboard.db.database import get_db, cache
from dashboard.app.core.security import YunAuthJWT
from dashboard.doc.permissions_key import UsersPermissions
from dashboard.app.common.utils import get_authorization_scheme_param

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


#云平台
#关于验证、权限类
class APIVERIFY(object):
    def __init__(self, fixed_content: str=None):
        self.fixed_content = fixed_content

    def _verify_expire_time_in_token(self, token: str):
        """验证token过期"""
        playload = YunAuthJWT().analysis_token(token=token)
        if datetime.now().timestamp() > playload['exp']-28800:
            cache.delete(token)
            return None
        return True

    def _get_token_type_jti(self, token: str):
        """获取token类型"""
        playload = YunAuthJWT().analysis_token(token=token)
        return playload['type'], playload['jti']


    async def __call__(self, request: Request, Authorization: str = Header(None), db: Session = Depends(get_db)):
        """
        token验证+权限验证+Cookies验证
        TODO:
        目前权限方式未定
        """
        if not Authorization:
            raise HTTPException(status_code=404, detail="Authorization为空")
        t_type, token = get_authorization_scheme_param(Authorization)
        if not token:
            raise HTTPException(status_code=404, detail="token为空,请登入")
        else:
            if not cache.exists(token):
                raise HTTPException(status_code=401, detail="token已失效,请登入")  # 令牌头无效(redis过期,或者被强制下线)
            verify_token_result = self._verify_expire_time_in_token(token=token)
            if verify_token_result == None:
                raise HTTPException(status_code=401, detail="此token已过期,请登入")  # 令牌头过期(配置时间过期)
            token_type, token_jti = self._get_token_type_jti(token=token)
            if token_type == base.TOKEN_REFRESH:
                raise HTTPException(status_code=401, detail="无效token")  # refresh token 无权访问接口
            token_key = cache.get(token)
            if token_key == None:
                raise HTTPException(status_code=401, detail="用户已失效,请登入")
            #验证用户
            if token_jti == base.JTI_USER:
                user_id = token_key
                user_obj = crud.user.get(db, user_id)
                if not user_obj:
                    raise HTTPException(status_code=401, detail="此token下的用户已失效,请登入")  # 令牌头无效
                if user_obj.flag != 0:
                    raise HTTPException(status_code=401, detail="已{}".format(base.flag_map[user_obj.flag]))
                if user_obj.superuser:
                    return True
                else:
                    if self.fixed_content:
                        if token_jti == base.JTI_USER:
                            if user_obj.superuser:
                                return True
                            loginOrg_msg = crud.user.get_user_roles(db, user_obj)
                            pers_list = loginOrg_msg['permissionsList']
                            if pers_list:
                                if self.fixed_content in pers_list:
                                    return True
                                else:
                                    try:
                                        hint = UsersPermissions[self.fixed_content]
                                    except KeyError:
                                        hint = self.fixed_content
                                    raise HTTPException(status_code=407, detail="无'{}'操作权限".format(hint))
                            raise HTTPException(status_code=407, detail="请添加操作权限")


#管理页面
#关于验证、权限类
class APIVERIFYSUPER(object):
    def __init__(self):
        pass

    def _verify_expire_time_in_token(self, token: str):
        """验证token过期"""
        playload = YunAuthJWT().analysis_token(token= token)
        #playload['exp']为时间戳格式
        if datetime.now().timestamp() > playload['exp']:
            return None
        return True

    async def __call__(self, request: Request, Authorization: str = Header(None), db: Session = Depends(get_db)):
        t_type, token = get_authorization_scheme_param(Authorization)
        if not token:
            raise HTTPException(status_code=404, detail="token为空,请登入")
        else:
            if not cache.exists(token):
                raise HTTPException(status_code=401, detail="token已失效,请登入")  # 令牌头无效
            verify_token_result = self._verify_expire_time_in_token(token= token)
            if verify_token_result == None:
                raise HTTPException(status_code=401, detail="此token已过期,请登入")  # 令牌头过期(配置时间过期)
            user_id = cache.get(token)
            user_obj = db.query(models.Users).filter_by(id=int(user_id)).first()
            if not user_obj:
                raise HTTPException(status_code=401, detail="此token下的用户已失效,请登入")  # 令牌头无效
            if user_obj.flag != 0:
                raise HTTPException(status_code=401, detail="此账号已{}".format(base.flag_map[user_obj.flag]))
            if not user_obj.superuser:
                raise HTTPException(status_code=407, detail="未授权此操作")  # 不是超级管理员
