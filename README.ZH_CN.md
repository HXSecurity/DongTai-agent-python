## DongTai-agent-python

[![django-project](https://img.shields.io/badge/django%20versions-3.2.8-blue)](https://www.djangoproject.com/)
[![dongtai-project](https://img.shields.io/badge/dongtai%20versions-beta-green)](https://github.com/huoxianclub/dongtai)
[![dongtai--agent--python](https://img.shields.io/badge/dongtai--agent--python-v1.0.6-lightgrey)](https://github.com/huoxianclub/dongtai-web)

- [English document](README.md)

## 1.项目介绍
DongTai-agent-python 是 **洞态IAST** 针对 Python 应用开发的数据采集端。在添加 iast-agent 代理的 Python 应用中，通过改写类字节码的方式采集所需数据，然后将数据发送至 DongTai-openapi 服务，再由云端引擎处理数据判断是否存在安全漏洞。

DongTai-agent-python  

- `dongtai_agent_python/config.json`用于配置DongTai-openapi服务地址、Token、项目名称。
- `dongtai_agent_python/cli`控制agent版本的热更新。
- `dongtai_agent_python/middleware/`用于接入不同的python框架，目前支持Django、Flask,均以中间件方式引入。
- `dongtai_agent_python/assess/`根据云端策略hook python 底层方法。
- `dongtai_agent_python/report/`将agent采集数据上报至DongTai-openapi服务。


## 2.应用场景

- DevOps流程
- 上线前安全测试
- 第三方组件管理
- 代码审计
- 0 Day挖掘


## 3.快速上手

### 快速使用

请参考：[快速开始](https://hxsecurity.github.io/DongTai-Doc/#/doc/tutorial/quickstart)

### 快速开发

1. Fork [DongTai-agent-python](https://github.com/HXSecurity/DongTai-agent-python) 项目到自己的github仓库并 clone 项目：

   ```shell
   git clone https://github.com/<your-username>/DongTai-agent-python
   ```

2. 根据需求编写代码

3. 项目打包，在agent项目根目录执行
     ```shell
     python3 setup.py sdist
     ```

4. 安装探针<br>
   打包后会生成dist目录，在dist目录下找到安装包，将dongtai_agent_python.tar.gz安装包放入Web服务器所在机器上，执行pip安装
 
      ```shell
      pip3  install ./dongtai-python-agent.tar.gz 
      ```
  
## 4.项目接入探针

#### Django 

1.进入app的主目录

2.打开`app/settings.py`文件，找到`MIDDLEWARE`所在行

3.在该行的下面插入`dongtai_agent_python.middlewares.django_middleware.FireMiddleware`

4.重启app

#### Flask
1.修改项目的入口文件(如 app.py), 增加如下内容
     
    from dongtai_agent_python.middlewares.flask_middleware import AgentMiddleware
    
    app = Flask(__name__)  
    app.wsgi_app = AgentMiddleware(app.wsgi_app, app) 
    
    if __name__ == '__main__':
        app.run()  
        
2.重启app
     
        
注意，`dongtai_agent_python/config.json`中的`project.name`需要与iast-web页面中创建的项目名称保持一致，agent将自动关联至项目；
若未配置`project.name`，可配置系统环境变量`projectName`，重启项目，同样生效，系统环境变量`projectName`优先级高于配置文件中的`project.name`； 


