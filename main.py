import os
from fastapi import FastAPI, applications
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.exceptions import RequestValidationError
from dashboard.app.api.api import api_router
from dashboard.app.core.config import settings
from dashboard.db.database import Base, engine
from dashboard.app.resources import strings as base
from dashboard.errors.http_error import http_error_handler, validation_exception_handler, exception_callback


def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(*args,**kwargs,swagger_js_url="https://unpkg.com/swagger-ui-dist@3.29/swagger-ui-bundle.js",swagger_css_url="https://unpkg.com/swagger-ui-dist@3.29/swagger-ui.css")

applications.get_swagger_ui_html = swagger_monkey_patch

app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

#上传的源文件压缩包
if not os.path.exists(base.insert_file_path):
    os.makedirs(base.insert_file_path)
app.mount(settings.API_V1_STR+"/static", StaticFiles(directory=base.insert_file_path), name="zip")


#创建所有数据模型
Base.metadata.create_all(bind=engine)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_exception_handler(HTTPException, http_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, exception_callback)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=10090, debug=False)
