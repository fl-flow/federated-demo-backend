from typing import Union
from loguru import logger
from fastapi import Request, status
from pydantic import ValidationError
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

#不符合传参规则错误 统一处理
async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, ValidationError],):
    """pydantic错误处理"""
    msg = exc.errors()[0].get('msg')
    type = exc.errors()[0].get('type')
    try:
        err_field = ''
        for x in exc.errors():
            err_field += x['loc'][1] + ','
        err = '({}) '.format(err_field[0:-1]) + msg
        err_design = '({}) '.format(err_field[0:-1]) + '字段错误，请重新填写'
        if type == "value_error":
            msg = err
        else:
            msg = err_design
        logger.debug(msg)
        return JSONResponse(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content= {"code": status.HTTP_422_UNPROCESSABLE_ENTITY,'msg': msg})
    except IndexError:
        err = '{} '.format(msg)
        logger.debug(err)
        return JSONResponse(status_code= status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content= {"code": status.HTTP_422_UNPROCESSABLE_ENTITY,'msg': err})
    except TypeError:
        err = '{} '.format(msg)
        logger.debug(err)
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content={"code": status.HTTP_422_UNPROCESSABLE_ENTITY, 'msg': "请求体格式错误"})

#正常错误返回 统一处理
async def http_error_handler(request: Request, exc: Union[HTTPException, RequestValidationError]) -> JSONResponse:
    """全局错误处理"""
    code= exc.status_code
    msg= exc.detail
    logger.debug(msg)
    return JSONResponse(content={"code":code,'msg':msg})


#全局捕获
# @app.exception_handler(Exception)
async def exception_callback(request: Request, exc: Exception):
    route = str(request.url).split('?')[0].split('/')[3:]
    api = '/' + ('/').join(route)
    msg = f"此接口执行错误: {request.method} {api}, Detail: {exc}"
    content = {"code": status.HTTP_500_INTERNAL_SERVER_ERROR, "msg": msg}
    logger.debug(content)
    return JSONResponse(status_code=500, content=content)
