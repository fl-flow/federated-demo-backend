import hashlib


class SignatureAndVerification(object):
    """MD5签名和验签"""
    @classmethod
    def data_processing(cls, data):
        """
        :param data: 需要签名的数据，字典类型
        :return: 处理后的字符串，格式为：参数名称=参数值，并用&连接
        """
        dataList = [f"{key}={data[key]}" for key in sorted(data) if data[key]]
        return "&".join(dataList).strip()

    @classmethod
    def md5_sign(cls, data, secret_key):
        """
        MD5签名

        :param secret_key: MD5签名需要的key
        :return:

        """
        data = data +"&"+ secret_key.strip()
        md5 = hashlib.md5()
        md5.update(data.encode(encoding='UTF-8'))
        return md5.hexdigest()

    @classmethod
    def md5_verify(cls, data, secret_key, signature):
        """
        md5验签
        :param data: 接收到的数据
        :param signature: 接收到的sign
        :return: 验签结果,布尔值
        """
        if cls.md5_sign(data, secret_key) == signature:
            return True
        else:
            return False
