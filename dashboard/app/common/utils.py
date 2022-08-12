import os
import rsa
import random
import uuid, time
from typing import Tuple
from zipfile import ZipFile
from fastapi import Request, HTTPException
from dashboard.db.database import cache
from dashboard.app.core.security import YunAuthJWT
from dashboard.app.resources import strings as base



yunauth = YunAuthJWT()


#处理对象中有时间类型的datetime转换成str ‘2020-01-01 12:12:12’
def change_datetime_format(obj):
    if 'createTime' in obj:
        if isinstance(obj['create_time'], str) and obj['create_time']:
            timestamps = obj['create_time'].split('T')
            obj['create_time'] = ''.join(timestamps[0]) + ' ' + timestamps[1]

    if 'updateTime' in obj:
        if isinstance(obj['update_time'], str) and obj['update_time']:
            timestamps = obj['update_time'].split('T')
            obj['update_time'] = ''.join(timestamps[0]) + ' ' + timestamps[1]

    return obj


#将模型形式的list转成[{},{}]
def return_data_type(queryset):
    if queryset:
        if hasattr(queryset[0], "to_dict"):
            return {"list": [v.to_dict() for v in queryset]}
        else:
            return {"list": [v for v in queryset]}
    else:
        return {"list": []}


#获取uuid
def get_uuid():
    uid = str(uuid.uuid4())
    u_id = ''.join(uid.split('-'))
    return u_id



def from_redis_token(kw: str):
    res = cache.scan_iter("*")
    for i in res:
        key = cache.get(i)
        if key.decode(encoding='UTF-8') == str(kw):
            if isinstance(i, bytes):
                return i.decode(encoding='UTF-8',errors='strict')

#-------------------------***第三方***-------------------------
#随机获得key
def get_appId():
    str1 = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM'
    code = ''
    for i in range(4):
        num = random.randint(0, len(str1) - 1)
        code += str1[num]
    return code


def get_authorization_scheme_param(authorization_header_value: str) -> Tuple[str, str]:
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return scheme, param

def get_token(authorization_header_value: str):
    if not authorization_header_value:
        return "", ""
    scheme, _, param = authorization_header_value.partition(" ")
    return param


#存储图片
class CustUploadFile():
    @staticmethod
    def upload(file, file_read, save_path=None, p_name=None):
        """
        file: 源文件
        file_read: 读取的文件内容
        save_path: 文件存储地址
        p_name: 文件保存的名字头-> file_1632478231.txt
        """
        # 判断文件夹是否定义
        if not ('STATIC_DIR' in vars(base)) and not ('FILE_PATH' in vars(base)):
            raise HTTPException(status_code=403, detail="请在配置中添加文件存储路径")
        # 文件大小
        if (file.spool_max_size / 1024 / 1024) > base.HEAD_SIZE:
            raise HTTPException(status_code=403, detail='上传的文件不能大于{}m'.format(base.HEAD_SIZE))

        name = p_name+'_' if p_name else 'file_'
        # file_read = file.file.read()
        # 插入表的字段的路径
        file_name = name + str(time.time()).split('.')[0] + str(random.randrange(1, 999, 3)) + '.' + \
                    file.filename.split('.')[len(file.filename.split('.')) - 1]

        insert_file_path_no = base.insert_file_path + save_path
        insert_file_path = insert_file_path_no + '/'+file_name
        file_path = save_path+'/'+file_name
        isExists = os.path.exists(insert_file_path_no)
        if not isExists:  # 路径不存在，即文件名不存在
            os.makedirs(insert_file_path_no)
        try:
            with open(insert_file_path, 'wb') as f:
                f.write(file_read)
        except:
            raise HTTPException(status_code=500, detail="上传失败")
        return (file_path).replace('\\', '/')



#公钥加密
def encrypt(mess):
    publickey = rsa.PublicKey.load_pkcs1(base.pub)
    info = rsa.encrypt(mess.encode('utf-8'), publickey)
    return info


#将目标文件写入已存在的压缩包中
def zipCompress(srcfile, desZipfile, in_name, moudle):
    """
    srcfile: 要被塞入压缩包的目标文件路径
    desZipfile: 压缩包文件路径
    in_name: 放入到压缩包内的名字
    """
    fp = ZipFile(desZipfile, mode=moudle)  # 以追加模式打开或创建zip文件
    with open(srcfile,'rb') as f:
        data = f.read()
        fp.writestr(in_name, data)  # 写入文件
        # fp.write(srcfile, "1.zip")
    fp.close()