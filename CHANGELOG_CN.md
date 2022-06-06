# 升级日志

## [1.4.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.4.0)  - 2022-06-06

* 变更
  * 更改组件包的名称格式和签名 [#118](https://github.com/HXSecurity/DongTai-agent-python/pull/118)

## [1.3.2](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.3.2)  - 2022-03-09

* 功能
  * 增加 str/bytes/bytearray 拼接(+) hook [#106](https://github.com/HXSecurity/DongTai-agent-python/pull/106)

## [1.3.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.3.1)  - 2022-02-23

* 功能
  * 增加弱加密算法漏洞检测 [#107](https://github.com/HXSecurity/DongTai-agent-python/pull/107)
  * 增加正则表达式DOS攻击检测 [#111](https://github.com/HXSecurity/DongTai-agent-python/pull/111)
  * 兼容 v2版本污点数据上报API [#116](https://github.com/HXSecurity/DongTai-agent-python/pull/116)
* 修复
  * 修复使用 gevent patch 时导致的异常 [#105](https://github.com/HXSecurity/DongTai-agent-python/pull/105)
  * 修复 Django 3.1、3.2 响应头解析错误 [#108](https://github.com/HXSecurity/DongTai-agent-python/pull/108)
  * 增加 alpine linux 下编译时需要的软件包文档说明 [#115](https://github.com/HXSecurity/DongTai-agent-python/pull/115)
* 变更
  * 性能优化 [#116](https://github.com/HXSecurity/DongTai-agent-python/pull/116)
  * 代码清理 [#110](https://github.com/HXSecurity/DongTai-agent-python/pull/110)
* 构建
  * github action 运行时自动触发 openapi 拉取最新的 agent 包 [#113](https://github.com/HXSecurity/DongTai-agent-python/pull/113)

## [1.3.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.3.0)  - 2022-01-07

* 功能
  * 组件管理: 上报已安装的软件包 [#100](https://github.com/HXSecurity/DongTai-agent-python/pull/100)
* 修复
  * 修复使用 requests 的内存泄漏 [#99](https://github.com/HXSecurity/DongTai-agent-python/pull/99)

## [1.2.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.2.1) - 2022-01-05

* 修复
  * 修复 fstring hook 的内存泄漏 [#97](https://github.com/HXSecurity/DongTai-agent-python/pull/97)

## [1.2.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.2.0) - 2021-12-31

* 功能
  * 增加 `pymongo` 策略规则以检测 NoSQL 注入漏洞 [#84](https://github.com/HXSecurity/DongTai-agent-python/pull/84)
  * 增加 `python-ldap` and `ldap3` 策略规则以检测 LDAP 注入漏洞 [#86](https://github.com/HXSecurity/DongTai-agent-python/pull/86), [#88](https://github.com/HXSecurity/DongTai-agent-python/pull/88)
  * 使用环境变量 `DEBUG=1` 开启 DEBUG 模式 [#92](https://github.com/HXSecurity/DongTai-agent-python/pull/92)
* 修复
  * 修复请求头和响应头格式 [#87](https://github.com/HXSecurity/DongTai-agent-python/pull/87)
  * 绕过过滤规则中的 hook [#93](https://github.com/HXSecurity/DongTai-agent-python/pull/93)
* 测试
  * 靶场测试时, 将 Django 和 Flask 的项目名称分开 [#94](https://github.com/HXSecurity/DongTai-agent-python/pull/94), [DockerVulspace#8](https://github.com/jinghao1/DockerVulspace/pull/8)

## [1.1.4](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.4) - 2021-12-18

* 功能
  * 增加 [funchook](https://github.com/kubo/funchook) 用于 Python C API 相关的函数/方法
  * 增加 `fstring` 方法改写
  * 增加 `str/bytes/bytearray` `cformat(%)` 方法改写
  * 增加 `str.__new__`, `bytes.__new__`, `bytearray.__init__` 方法改写
  * 增加 `pickle.load`, `pickle.loads` 策略规则以检测不安全的反序列化漏洞
  * 为 HTML 转义添加一些过滤规则
* 修复
  * 修复 `yaml.load` 以及 `yaml.load_all` 危险参数检查
* 变更
  * 修改 `yaml.load`, `yaml.unsafe_load` 策略类型为不安全的反序列化
  * 对于包含多个危险方法的请求, 在检测到第一个危险方法后不再停止跟踪
* 构建
  * 支持 Windows 下 C 语言扩展构建
  * 添加 Ubuntu/MacOS/Windows 上的构建动作

## [1.1.3](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.3) - 2021-12-03

* 功能
  * 使用环境变量 `ENGINE_NAME` 自定义 Agent 名称
  * 使用环境变量 `LOG_PATH` 自定义日志文件路径
  * 增加 `exec` 策略规则以检测代码执行漏洞
* 改进
  * 代码重构: 增加作用范围用于防止递归执行 Agent 自身的代码
  * 代码重构: 增加运行时设置并替换使用全局变量的配置
  * 代码重构: 增加请求上下文以存储污点数据
  * 性能改进: 污点数据处理优化
  * 性能改进: 移除不必要的 `list` 策略规则
* 修复
  * 修复带有上下文变量的 `eval` 异常

## [1.1.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.1) - 2021-11-20

* 功能
  * 增加 Agent 启动时审核功能
  * 使用环境变量 `PROJECT_VERSION` 自动创建项目版本
* 改进
  * 增加 Django 模板策略规则用以检测 XSS
  * 增加旧版本 werkzeug 请求体策略规则
  * 增加 Django 路由匹配策略规则
* 修复
  * 修复 SQL 注入危险参数处理
  * 修复在多个框架下使用相同的配置文件导致的 Agent 名称重复问题
  * 修复 Django 请求体获取为空的问题
  * 修复对象哈希值生成方法，以避免重复哈希值
  * 修复多线程下方法池异常的问题
  * 修正某些方法以自身参数作为返回值的情况
  * 修复旧版本 werkzeug 兼容性

## [1.1.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.0) - 2021-11-05

* 功能
  * Agent 服务端启停
  * Agent 根据 CPU 阈值启停
  * 使用环境变量 `AUTO_CREATE_PROJECT=1` 在首次使用 Agent 时自动创建项目
  * 上报服务启动时间
  * 增加 XSS 检测
  * 增加 XXE 检测
  * 增加 SSRF 检测
* 修复
  * 修复上报数据参数 `className` 为完整的类名
  * 修复上报的请求体和响应体格式
  * 修复流式响应处理
  * 修复响应体处理
  * 修复 Django 请求表单数据处理
  * 修复污点数据的 `kwargs` 参数
  * 修复方法池中的无效的污点数据
  * 修复无效的污点数据过滤
* 构建
  * 代码提交时自动打包上传
  * 代码提交时自动执行靶场测试脚本
* 测试
  * 增加靶场测试脚本

## [1.0.6](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.0.6) - 2021-10-26

* 增加启动脚本 `dongtai-cli`, 使用脚本启动时 agent 会自动更新
* 从 openapi 拉取策略规则
* 修改数据上报参数
* 污点数据异步上报
* 心跳增加等待上报计数
* 修复 agent 名字格式化
* 修复 windows 环境变量读取
