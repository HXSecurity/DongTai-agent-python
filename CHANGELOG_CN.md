# 升级日志

## 尚未发布

* 功能
  * 增加 [funchook](https://github.com/kubo/funchook) 用于 Python C API 相关的函数/方法
  * 增加 `fstring` hook
  * 增加 `str/bytes/bytearray` `cformat(%)` hook

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
