# 返回结果代码
HTTP_200 = 200      # 请求正常
HTTP_400 = 400      # 登录报错
HTTP_403 = 403      # token失效，强制退出登录
HTTP_404 = 404      # 系统报错

#deleted 状态码
Roles_deleted_list = [2, 1, 0] #表示delete只能在1和0之间

#用户状态码
Users_status_list = [0, 1, 2, 3, 4]



sex_map = {
    0: "男",
    1: "女"
}


#状态码
status_false = 0
status_true = 1
flag_true = 0
flag_false = 1

#医院机构flag map
flag_map = {
    0: "正常",
    1: "冻结",
    2: "注销",
    3: "在审核",
    4: "审核未通过"
}

wash_map = {
    0: "正在脱敏",
    1: "脱敏失败",
    2: "数据集格式错误"
}

#返回状态码
StatusCodeDict = {
    200: '成功',
    201: '创建成功',
    400: '请求发送错误',
    401: '未授权(请检查账号密码是否正确)',
    402: '已存在',
    403: '没有权限',
    404: '服务器找不到所请求的资源',
    405: 'Method Not Allowed(不允许使用该方法)',
    407: '未授权(无权限操作)',
    408: 'Request Timeout(请求超时)',
    500: '服务器报错',
    501: '创建失败',
    502: '修改失败'
}

# 默认文件存放文件统一名称头
STATIC_DIR = 'media'
#文件路径
FILE_PATH = "dashboard"
# 专家头像大小不能超过HEAD_SIZE/m
HEAD_SIZE = 10

#用户操作模块
MODULES = {
    "login": "登录",
    "loginout": "退出登录",
    "user": "用户",
    "role": "角色",
    "auth": "权限",
}
TOKEN_TYPE = ["access", "refresh"]
JTI = ["user", "thirdServer"]
TOKEN_ACCESS = "access"
TOKEN_REFRESH = "refresh"
JTI_USER = "user"
JTI_SERVER = "thirdServer"
client_credential = "client_credential"


#密码加密公钥
pub = """
    -----BEGIN RSA PUBLIC KEY-----
MIGJAoGBAKz6ziZFNLwVBCjfPkiaAQNnTEM6OpYY4kkDDAEr4/8Epu+g6IEG+cTb
IYPkU3f3zOHvFLVA1AMZelRL+pOkDpYtgMmvf+swg1FAavk/k6fKliclsnDNWAdA
N/ewwfmZ70uw75nVm4RBPya8D3y8JDr7P1oBzV7hHEwb4Db7brqpAgMBAAE=
-----END RSA PUBLIC KEY-----
    """
#密码加密私钥
pri = """
    -----BEGIN RSA PRIVATE KEY-----
MIICXwIBAAKBgQCs+s4mRTS8FQQo3z5ImgEDZ0xDOjqWGOJJAwwBK+P/BKbvoOiB
BvnE2yGD5FN398zh7xS1QNQDGXpUS/qTpA6WLYDJr3/rMINRQGr5P5OnypYnJbJw
zVgHQDf3sMH5me9LsO+Z1ZuEQT8mvA98vCQ6+z9aAc1e4RxMG+A2+266qQIDAQAB
AoGARzFueSfQnXxU2vGOs9jWg+0W4TBs/mu9bmlXnn/O9Z2Xi1aBeuFBGTlLIPpv
NBgD9hUtQ7Ar0h7BT0J5trWISpKlOQTDMP+bCPAzfKA1MHInifY35Tw7Ia9KQ3Dh
4GMUvmSXE5cplIBH9H3cymKutPaDwFUGteX7ANNkZn+oO1ECRQD7O4OP1p/pcwQb
F3l9EBYtsXP8cNARkxmDYva2D8TBXBfBJi4p+1pNr2LUnAjUaGmy1qiunDYxFUzR
xnhBjOGuOptBHQI9ALBDI8qV2Y+LwBEkVp0I4rFrVy+YQO+1NtKB08hoIRBiWK7t
hx8ZbhsTY9gz2zfng6BidsyPXxnGOcgV/QJEYzSqC+eNd+riCSyo3Zi3mU2EZn/J
udbjcT1n/JaXdF9ARhYkjpFhpGGIXjpLRk0AyAz5yRGIWLN3hTKhFAlkqJ8d5YUC
PC5oTvkcwR5ZNiWNQryvxTffQiJG3Pn/5UJBamg+ek4dBqpv4X6frGy2izg2VwZ+
DxrgMdUj/m8D0NzMZQJEXtcF69PVt5ChnAQEiQfs8+zlYt03TUccR+hc6oM4wkK2
nk+Shzo0hpJAD8gU2O79TppPaygGr9yphYXs6njYu2/cEtc=
-----END RSA PRIVATE KEY-----
    """


#上传
pictures_type = [".jpg", ".jpeg", ".png", ".JPG", ".PNG", ".JPEG"]
compress_type = [".zip"]
excel_type = [".xlsx", ".xls", ".csv"]
video_type = [".mp4", ".avi"]

insert_file_path = "/home/fang/projects/meta-server/dashboard/static_vote/media"

