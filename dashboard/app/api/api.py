from fastapi import APIRouter
from dashboard.app.api.endpoints import users,\
    permission, role, websitNode, login, author

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(author.router, prefix="/auth", tags=["auth"])  #授权
api_router.include_router(users.router, prefix="/journal", tags=["journal"])  #日志
api_router.include_router(role.router, prefix="/roles", tags=["roles"])  #角色
api_router.include_router(permission.router, prefix="/permissions", tags=["pers"])  #权限
api_router.include_router(websitNode.router, prefix="/node", tags=["node"])  #节点
