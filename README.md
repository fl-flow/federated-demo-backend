### federated-demo-backend项目

### 技术栈
- python3.7.6+fastapi+mysql+redis+docker

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
- 本地启动: uvicorn main:app --host 0.0.0.0 --port 10090 --reload

### 项目部署
1. 通过修改.env环境变量，适配对应服务
2. docker-compose up -d

### 接口文档
- 将openapi.json文件导入postman等工具