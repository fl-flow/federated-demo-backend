### federated-demo-backend项目

### 技术栈
- python+fastapi+mysql+redis+docker

### 目前功能
- 用户模块：
	注册、
	登录、
	审核、
	退出、
	用户管理、
- 角色模块：
	crud
- 权限功能：
	导出、
	crud
- 授权功能：
	申请、
	审核
- 站点功能：
	上传、
	导出

### 运行环境
- 执行 pip install -r requirements.txt
- 修改config.py文件中的中间件配置参数(mysql、redis) 

### 项目部署
1. 通过修改.env环境变量，适配对应服务
2. docker-compose up -d
