## DongTai-agent-python

[![dongtai-project](https://img.shields.io/badge/DongTai-v1.1.1-blue)](https://github.com/HXSecurity/DongTai)
[![dongtai--agent--python](https://img.shields.io/badge/DongTai--agent--python-v1.1.1-blue)](https://github.com/HXSecurity/DongTai-agent-python)

[![django-project](https://img.shields.io/badge/Supported%20versions%20of%20Django-3.0.x,3.1.x,3.2.x-blue)](https://www.djangoproject.com/)
[![flask-project](https://img.shields.io/badge/Supported%20versions%20of%20Flask-1.0.x,1.1.x,1.2.x-blue)](https://palletsprojects.com/p/flask/)

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

Please refer to the [Quick Start](https://doc.dongtai.io/en/02_start/index.html).

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
4. Install the agent \
   After packaging, the dist directory will be generated, and the installation package will be found in the dist directory, Put the dongtai_agent_python.tar.gz installation package on the machine where the Web-server is located，Execute pip installation 
 
      ```shell
      pip3  install ./dongtai-python-agent.tar.gz 
      ```
  
## Project access Agent

### Agent Configuration

#### Environment Variables

* Auto Create Project: `AUTO_CREATE_PROJECT=1`
* Project Name: `PROJECT_NAME=Demo`
* Project Version: `PROJECT_VERSION=v1.0`
* Agent Name: `ENGINE_NAME=test-flask`
* Log Path: `LOG_PATH=/tmp/dongtai-agent-python.log`

You can also configure the value in `dongtai_agent_python/config.json`
  * `project.name`
  * `project.version`
  * `engine.name`
  * `log.log_path`

> **Note: The priority of the system environment variable is higher than the configuration file**

### Django 

1. Enter the main directory of the app
2. Open the `app/settings.py` file and find the line of `MIDDLEWARE`
3. Insert below the line `dongtai_agent_python.middlewares.django_middleware.FireMiddleware`
4. Restart app

### Flask

1. Modify the entry file of the project (such as app.py) and add the following content
    ```python
    
    app = Flask(__name__)

    from dongtai_agent_python.middlewares.flask_middleware import AgentMiddleware
    app.wsgi_app = AgentMiddleware(app.wsgi_app, app)
    
    if __name__ == '__main__':
        app.run()
    ```
2. Restart app

<img src="https://static.scarf.sh/a.png?x-pxid=e8ec5bbb-2869-4a6d-876d-f2e66bf408f2" />
