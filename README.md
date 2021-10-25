## DongTai-agent-python

[![django-project](https://img.shields.io/badge/django%20versions-3.2.8-blue)](https://www.djangoproject.com/)
[![dongtai-project](https://img.shields.io/badge/dongtai%20versions-beta-green)](https://github.com/huoxianclub/dongtai)
[![dongtai--agent--python](https://img.shields.io/badge/dongtai--agent--python-v1.0.6-lightgrey)](https://github.com/huoxianclub/dongtai-web)

- [中文版本(Chinese version)](README.ZH_CN.md)

## Project Introduction

Dongtai-agent-python is DongTai Iast's data acquisition tool for Python applications. In a Python application with the iast agent added, the required data is collected by rewriting class bytecode, and then the data is sent to dongtai-OpenAPI service, and then the cloud engine processes the data to determine whether there are security holes.

DongTai-agent-python  

- `dongtai_agent_python/config.json` For configuration DongTai-openapi Url、Token、Web-ProjectName。
- `dongtai_agent_python/cli` Control the hot update of the agent version。
- `dongtai_agent_python/middleware/` Used to access different python frameworks, currently supports Django and Flask, both of which are introduced in the form of middleware。
- `dongtai_agent_python/assess/` Hook the underlying method of python according to the cloud strategy。
- `dongtai_agent_python/report/` Report the collected data of the agent to the DongTai-openapi service。

## Application Scenarios

- DevOps
- Security test the application before it goes online
- Third-party Component Management
- Code audit
- 0 Day digging

## Quick Start

Please refer to the [Quick Start](https://hxsecurity.github.io/DongTai-Doc/#/doc/tutorial/quickstart).

## Quick Development

1. Fork the [DongTai-agent-python](https://github.com/HXSecurity/DongTai-agent-python) , clone your fork:

   ```
   git clone https://github.com/<your-username>/DongTai-agent-python
   ```

2. Write code to your needs.

3. The project is packaged and executed in the root directory of the agent project
     ```shell
     python3 setup.py sdist
     ```

4. Install the agent <br>
   After packaging, the dist directory will be generated, and the installation package will be found in the dist directory, Put the dongtai_agent_python.tar.gz installation package on the machine where the Web-server is located，Execute pip installation 
 
      ```shell
      pip3  install ./dongtai-python-agent.tar.gz 
      ```
  
## 4.Project access Agent

#### Django 

1.Enter the main directory of the app

2.Open the `app/settings.py` file and find the line of `MIDDLEWARE`

3.Insert below the line `dongtai_agent_python.middlewares.django_middleware.FireMiddleware`

4.Restart app

#### Flask
1.Modify the entry file of the project (such as app.py) and add the following content
     
    from dongtai_agent_python.middlewares.flask_middleware import AgentMiddleware
    
    app = Flask(__name__)  
    app.wsgi_app = AgentMiddleware(app.wsgi_app, app) 
    
    if __name__ == '__main__':
        app.run()  
        
2.Restart app
     
        
Note that the `project.name` in `dongtai_agent_python/config.json` needs to be consistent with the project name created in the iast-web page, The agent will be automatically linked to the project;
If `project.name` is not configured, you can configure the system environment variable `projectName`, restart the project, the same will take effect, The priority of the system environment variable `projectName` is higher than the `project.name` in the configuration file;