## DongTai-agent-python

[![dongtai-project](https://img.shields.io/github/v/release/HXSecurity/DongTai?label=DongTai)](https://github.com/HXSecurity/DongTai/releases)
[![dongtai--agent--python](https://img.shields.io/github/v/release/HXSecurity/DongTai-agent-python?label=DongTai-agent-python)](https://github.com/HXSecurity/DongTai-agent-python/releases)

- [English document](README.md)

## 项目介绍

DongTai-agent-python 是 **洞态IAST** 针对 Python 应用开发的数据采集端。在添加 iast-agent 代理的 Python 应用中，通过改写类字节码的方式采集所需数据，然后将数据发送至
DongTai-openapi 服务，再由云端引擎处理数据判断是否存在安全漏洞。

DongTai-agent-python

- `dongtai_agent_python/config.json`用于配置DongTai-openapi服务地址、Token、项目名称。
- `dongtai_agent_python/cli`控制agent版本的热更新。
- `dongtai_agent_python/middleware/`用于接入不同的python框架，目前支持Django、Flask,均以中间件方式引入。
- `dongtai_agent_python/assess/`根据云端策略hook python 底层方法。
- `dongtai_agent_python/report/`将agent采集数据上报至DongTai-openapi服务。

## 应用场景

- DevOps流程
- 上线前安全测试
- 第三方组件管理
- 代码审计
- 0 Day挖掘

## 系统依赖

* Python: >=3.6
* CPython
* 编译依赖 (Agent 版本 >= 1.1.4)
  * gcc (Linux/macOS)
  * make (Linux/macOS)
  * cmake >= 3.6
  * Visual Studio (Windows)
* Web 框架
  * Django: 3.0-3.2, 4.0
  * Flask: 1.0-1.2, 2.0
* Python 依赖包
  * psutil: >= 5.8.0
  * requests: >= 2.25.1
  * pip: >= 19.2.3

## 快速上手

### 快速使用

请参考：[快速开始](https://doc.dongtai.io/02_start/index.html)

### 快速开发

1. Fork [DongTai-agent-python](https://github.com/HXSecurity/DongTai-agent-python) 项目到自己的 github 仓库并 clone 项目：
    ```shell
    git clone https://github.com/<your-username>/DongTai-agent-python
    ```
2. 根据需求编写代码
3. 修改配置文件 `dongtai_agent_python/config.json`
    * iast.server.token: "3d6bb430bc3e0b20dcc2d00000000000000a"
    * iast.server.url: "https://iast-test.huoxian.cn/openapi"
    * project.name: "DemoProjectName"
   > url 与 token 从洞态 IAST-web 页面(eg: https://iast-test.huoxian.cn/deploy) > python-agent 部署页面,下载 agent 的 shell 命令中获取，分别替换 url 域名与 token
4. 项目打包，在agent项目根目录执行
    ```shell
    python3 setup.py sdist
    ```
5. 安装探针 \
   打包后会生成 dist 目录，在 dist 目录下找到安装包，将 dongtai_agent_python.tar.gz 安装包放入 Web 服务器所在机器上，执行 pip 安装
    ```shell
    pip3 install ./dongtai-python-agent.tar.gz 
    ```

## 项目接入探针

### 探针配置

#### 环境变量

* 开启调试: `DEBUG=1`
* 自动创建项目: `AUTO_CREATE_PROJECT=1`
* 项目名称: `PROJECT_NAME=Demo`
* 项目版本: `PROJECT_VERSION=v1.0`
* Agent 名称: `ENGINE_NAME=test-flask`
* 日志文件路径: `LOG_PATH=/tmp/dongtai-agent-python.log`

也可以配置 `dongtai_agent_python/config.json` 中相关的配置项，同样生效

* `debug`
* `project.name`
* `project.version`
* `engine.name`
* `log.log_path`

> **注意: 环境变量的配置优先级高于配置文件**

### Django

1. 进入app的主目录
2. 打开 `app/settings.py` 文件，找到 `MIDDLEWARE` 所在行
3. 在该行的下面插入 `dongtai_agent_python.middlewares.django_middleware.FireMiddleware`
4. 重启 app

### Flask

1. 修改项目的入口文件(如 app.py), 增加如下内容
    ```python
    app = Flask(__name__)

    from dongtai_agent_python.middlewares.flask_middleware import AgentMiddleware
    app.wsgi_app = AgentMiddleware(app.wsgi_app, app)

    if __name__ == '__main__':
        app.run()
    ```
2. 重启app
