## 1.下载探针

登陆 [IAST平台](https://iast.huoxian.cn/login) 在**部署IAST**中下载洞态IAST的Agent，将dongtai_agent_python.tar.gz文件放入WEB服务器（中间件）所在机器上

注意，`curl url&projectName=<Demo Project>` 为可更改参数，`<projectName>`与创建的项目名称保持一致，agent将自动关联至项目；
若下载时未配置`<projectName>`，可配置系统环境变量projectName，重启项目，同样生效，系统环境变量`<projectName>`优先级高于下载时配置的`<projectName>`；
如果不配置该参数，需要进入项目管理中进行手工绑定。
 
## 2.安装探针
- 找到下载的探针文件，直接执行命令 
  ```shell
  pip3  install ./dongtai-python-agent.tar.gz 
  ```
  
## 3.配置探针

### 3.1 Django 

1.进入app的主目录

2.打开`app/settings.py`文件，找到`MIDDLEWARE`所在行

3.在该行的下面插入`dongtai_agent_python.middlewares.django_middleware.FireMiddleware`

4.重启app


