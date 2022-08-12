"""
模型基类
"""
from datetime import datetime
from sqlalchemy import Column, DateTime


#时间基类
class BaseTimeModel(object):
    createTime = Column(DateTime, default=datetime.now, nullable=False)  # 记录的创建时间
    updateTime = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间
    def to_dict(self, exclude=[],reverse=True, time_=True):
        """
        1.reverse=True: not in exclude：输出去除该列表里面的字段
        2.reverse=False: in exclude：输出只有该列表里面的字段
        """
        if reverse:
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude }
        else:
            if time_:
                exclude = exclude + ['createTime', 'updateTime']
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in exclude }
        if 'createTime' in data:
            data['createTime'] = data['createTime'].strftime("%Y-%m-%d %H:%M:%S") if data['createTime'] else ''
        if 'updateTime' in data:
            data['updateTime'] = data['updateTime'].strftime("%Y-%m-%d %H:%M:%S") if data['updateTime'] else ''
        return data


class BaseDictModel(object):

    def to_dict(self, exclude=[],reverse=True):
        """
        1.reverse=True: not in exclude：输出去除该列表里面的字段
        2.reverse=False: in exclude：输出只有该列表里面的字段
        """
        if reverse:
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name not in exclude }
        else:
            data = {c.name: getattr(self, c.name) for c in self.__table__.columns if c.name in exclude }
        if 'createTime' in data:
            data['createTime'] = data['createTime'].strftime("%Y-%m-%d %H:%M:%S") if data['createTime'] else ''
        if 'updateTime' in data:
            data['updateTime'] = data['updateTime'].strftime("%Y-%m-%d %H:%M:%S") if data['updateTime'] else ''
        return data