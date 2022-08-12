from sqlalchemy import Column, Integer, String, BIGINT, Text
from dashboard.db import Base
from .abstract_models import BaseTimeModel



#用户表
class Users(BaseTimeModel, Base):
    __tablename__ = 'UsersPy'
    id = Column(Integer, primary_key=True, index=True)
    realName = Column(String(32), index=True, nullable=False, comment="姓名")
    gender = Column(String(32), index=True, nullable=True, comment="性别")
    userEmail = Column(String(50), nullable=True, comment="邮箱")
    password = Column(Text, nullable=False, comment="密码")
    superuser = Column(Integer, default=False, nullable=False, comment="是否是超级管理员")
    phoneNumber = Column(String(32), unique=True, index=True, nullable=False, comment="账号")
    expertImage = Column(String(500),  comment="头像")
    flag = Column(Integer, nullable=False, default=3) #flag 0 代表正常。 1 代表冻结。2代表移除 >0不能登入。 3:待审核, 4: 审核未通过
    ownerUser = Column(Integer, nullable=False, comment="创建者用户id")
    sourceFrom = Column(Integer, nullable=False, default=1) #普通注册:1; 钉钉:2; 微信:3;
    uniqueId = Column(String(200), nullable=True) #其他方式注册的唯一值; 钉钉: unionid; .....


#**************************角色权限配置**************************

#角色配置表
class Roles(BaseTimeModel, Base):
    __tablename__ = 'Roles'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(32), nullable=False, comment="角色名称")

#权限配置表
class Permissions(BaseTimeModel, Base):
    __tablename__ = 'Permissions'
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(32), unique=True, nullable=False, comment="权限key")
    title = Column(String(32), unique=True, nullable=False, comment="权限名称")


#角色、权限关系表
class RolesPermission(BaseTimeModel, Base):
    __tablename__ = 'RolesPermission'
    roleId = Column(Integer, nullable=False, primary_key=True, comment="角色id")
    permissionId = Column(Integer, nullable=False, primary_key=True, comment="权限id")


#角色用户
class UsersRoles(BaseTimeModel, Base):
    __tablename__ = 'UsersRoles'
    userId = Column(Integer, nullable=False, primary_key=True, comment="用户id")
    roleId = Column(Integer, nullable=False, primary_key=True, comment="角色id")

#**************************机构**************************

#站点
class WebsitNode(BaseTimeModel, Base):
    __tablename__ = 'WebsitNode'
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(64),unique=True, nullable=False, comment="code")
    nodeName = Column(String(64), unique=True, nullable=False, comment="站点名称")
    nodeHost = Column(String(64), nullable=False, comment="站点地址")
    nodePort = Column(String(64), nullable=False, comment="站点端口")
    appKey = Column(String(64), nullable=True)
    brif = Column(String(200), nullable=True, comment="简介")
    flag = Column(Integer, nullable=False, default=0) #0:正常; 1 代表冻结; 2代表注销


#用户操作记录模块
class UsersRecords(BaseTimeModel, Base):
    __tablename__ = 'UsersRecords'
    id = Column(BIGINT, nullable=False, primary_key=True)
    userId = Column(Integer, nullable=False, comment="用户外键")
    userName = Column(String(16), nullable=False, comment="用户姓名")
    phoneNumber = Column(String(16), nullable=False, comment="手机号码")
    path = Column(String(100), nullable=False, comment="用户操作路由")
    methodType = Column(String(32), nullable=False, comment="用户操作method")
    module = Column(String(32), nullable=False, comment="用户操作模块")
    orgCode = Column(String(32), nullable=True, comment="站点")
    returnResult = Column(String(32), nullable=True, comment="返回结果httpcode")
    remark = Column(Text, nullable=True, comment="备注")


#验证鉴权表
class Authentication(BaseTimeModel, Base):
    __tablename__ = 'authentication'

    id = Column(Integer, primary_key=True, index=True)
    appKey = Column(String(64), index=True, nullable=False)
    appSecret = Column(String(128),
                        index=True,
                        nullable=False)
    remarks = Column(String(100), comment="备注")