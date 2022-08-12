FROM python:3.7.6-slim-stretch

#复制代码文件到容器
COPY .  /home/projects/hi-management-server

#设置diamante工作目录
WORKDIR /home/projects/hi-management-server

# ENV DEBIAN_FRONTEND noninteractive
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone
# RUN apt-get update && apt-get install -y vim
RUN python -m pip install --upgrade pip && pip install uvloop && pip install httptools
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir -r /home/projects/hi-management-server/requirements.txt

# # 安装vim
RUN apt-get update
RUN apt-get install -y vim

#EXPOSE 8090
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8090"]
#CMD gunicorn main:app –preload -b 0.0.0.0:8090 -w 12 --threads 2 --worker-connections 2048 --backlog 2048 -k uvicorn.workers.UvicornWorker --log-level error --log-file /home/projects/hi-management-server/dashboard/logs/error.log
