import secrets
from functools import lru_cache
from typing import List, Union, Optional, Dict, Any
from pydantic import BaseSettings, validator, AnyHttpUrl, PostgresDsn


class Settings(BaseSettings):
    """配置类"""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "research"
    DELETE_TIMEOUT_DAY: int = 10  # 记录删除时间/天
    SIGN_RESET_TIME: int = 30  # 签名可再次修改时间/天\
    ZIP_IN_FILES_NAME: int = 150 #上传压缩包内文件名称长度不超过限制
    EXPIRE_DATASET_TIME: int = 10 #数据集下载过期时间

    # token相关
    ALGORITHM: str = "HS256"  # 加密算法
    SECRET_KEY: str = secrets.token_urlsafe(32)  # 随机生成的base64位字符串
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600 * 24 * 3  # token的时效 3 天 = 3600 * 24 * 3
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 3600 * 24 * 7  # token的时效 7 天 = 3600 * 24 * 7
    FIXED_SECRET_KEY: str = "JrK6vcHGNANDyr02gph8bALGeWygps2YcyCNDQInEAg"

    # redis
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 10
    REDIS_TIME_OUT: int = 86400  # 缓存时间默认24小时
    REDIS_TIME_OUT_FOR_THIRD = 259200  # 第三方时间默认3x24小时

    # mysql
    MYSQL_HOST: str = "127.0.0.1"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "datament"
    MYSQL_USER: str = "root"
    MYSQL_PWD: str = "root"

    # 跨域设置
    ORIGINS: List[str] = [
        "*",
    ]

    # es配置
    INDEX_NAME: str = "1022_research"
    INDEX_TYPE: str = "pj_type"
    # ES_IP: str = "127.0.0.1"
    ES_IP: str = "172.16.10.184"
    ES_PORT: str = 9200
    LOG_ENABLED = True  # 是否开启log
    LOG_TO_FILE = False  # 是否存储到文件
    LOG_TO_CONSOLE = True  # 是否输出到控制台
    LOG_TO_ES = False  # 是否输出到es
    APP_ENVIRONMENT = 'dev'  # 运行环境，如测试环境还是生产环境

    # log配置
    LOG_PATH = '../logs/debug_{time}.log'  # 日志文件路径
    ROTATION: str = "100 MB"  # log文件大小
    COMPRESSION: str = "zip"  # log文件生成类型
    RETENTION: str = "15 days"  # log文件过期时间
    LEVEL: str = "DEBUG"


    # 定时任务配置
    CRON_STRING = "1 10 0"   # 每日几点几分几秒, 每天1点10分0秒运行

    # 跨域
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(
            cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        env_file = "/home/fang/projects/pj-hi-research-server/dashboard/app/core/.env"
        env_file_encoding = 'utf-8'


@lru_cache()
def config_settings():
    settings = Settings()
    return settings


settings = config_settings()
