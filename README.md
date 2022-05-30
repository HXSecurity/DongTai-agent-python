## DongTai-agent-python

[![dongtai-project](https://img.shields.io/github/v/release/HXSecurity/DongTai?label=DongTai)](https://github.com/HXSecurity/DongTai/releases)
[![dongtai--agent--python](https://img.shields.io/github/v/release/HXSecurity/DongTai-agent-python?label=DongTai-agent-python)](https://github.com/HXSecurity/DongTai-agent-python/releases)

- [中文版本(Chinese version)](README.ZH_CN.md)

## Project Introduction

DongTai-agent-python is DongTai IAST's data acquisition tool for Python applications. In a Python application, the required data is collected through patching methods and functions, sent to the DongTai OpenAPI service, and then the cloud engine processes the data to determine if there are security vulnerabilities.

DongTai-agent-python

- `dongtai_agent_python/api/` Report the collected data to the DongTai OpenAPI service.
- `dongtai_agent_python/assess/` Hook python methods according to the cloud strategy.
- `dongtai_agent_python/assess_ext/` Hook cpython underlying methods according to cloud strategy.
- `dongtai_agent_python/cli/` Control the hot update of the agent version.
- `dongtai_agent_python/context/` Request context and context tracker.
- `dongtai_agent_python/middleware/` Used to access different python frameworks, currently supports Django and Flask,
  both of which are introduced in the form of middleware.
- `dongtai_agent_python/policy/` Strategy rules and tainted data processing.
- `dongtai_agent_python/setting/` Agent configuration.
- `dongtai_agent_python/config.json` For configuration DongTai OpenAPI Url, Token, Project Name.

## Application Scenarios

- DevOps
- Security test the application before it goes online
- Third-party Component Management
- Code audit
- 0day digging

## Requirements

* Python: >=3.6
* CPython
* Compiling Dependencies (Agent version >= 1.1.4)
  * gcc (Linux/macOS)
  * make (Linux/macOS)
  * cmake: >= 3.6
  * Visual Studio (Windows)
  * bash (Alpine Linux)	
  * libc-dev (Alpine Linux)
  * linux-headers (Alpine Linux)
* Web Framework
  * Django: 3.0-3.2, 4.0
  * Flask: 1.0-1.2, 2.0
* Python packages
  * psutil: >= 5.8.0
  * requests: >= 2.25.1
  * pip: >= 19.2.3

## Quick Start

Please refer to the [Quick Start](https://doc.dongtai.io/).

## Quick Development

1. Fork the [DongTai-agent-python](https://github.com/HXSecurity/DongTai-agent-python) , clone your fork:
    ```
    git clone https://github.com/<your-username>/DongTai-agent-python
    ```
2. Write code to your needs.
3. Modify the configuration file `dongtai_agent_python/config.json`
   * iast.server.token: "3d6bb430bc3e0b20dcc2d00000000000000a"
   * iast.server.url: "https://iast-test.huoxian.cn/openapi"
   * project.name: "DemoProjectName"

    > URL and token from the hole state IAST-web page (eg: https://iast-test.huoxian.cn/deploy) > python-agent deployment page,Obtained from the shell command of downloading agent，Replace the url domain name and token respectively

4. The project is packaged and executed in the root directory of the agent project
    ```shell
    python3 setup.py sdist
    ```
5. Install the agent \
   After packaging, the dist directory will be generated, and the installation package will be found in the dist
   directory, Put the dongtai_agent_python.tar.gz installation package on the machine where the Web-server is
   located，Execute pip installation
    ```shell
    pip3 install ./dongtai-python-agent.tar.gz 
    ```

## Project access Agent

### Agent Configuration

#### Environment Variables

* DEBUG mode: `DEBUG=1`
* Auto Create Project: `AUTO_CREATE_PROJECT=1`
* Project Name: `PROJECT_NAME=Demo`
* Project Version: `PROJECT_VERSION=v1.0`
* Agent Name: `ENGINE_NAME=test-flask`
* Log Path: `LOG_PATH=/tmp/dongtai-agent-python.log`

You can also configure the value in `dongtai_agent_python/config.json`

* `debug`
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
