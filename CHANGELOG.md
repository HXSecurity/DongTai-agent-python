# Changelog

## Unreleased

* FEATURES
  * Agent pause/start by DongTai server
  * Agent pause/start based on system resource usage
  * Use environment variable `AUTO_CREATE_PROJECT=1` for auto create project
  * Report Agent startup time
* BUGFIXES
  * Fix report data parameter`className` to fully named class name
  * Fix report data request/response body format
* BUILD
  * Auto upload package to Aliyun OSS by Github actions

## [1.0.6](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.0.6) - 2021-10-26

* Auto update on start with `dongtai-cli`
* Pull policy rules from openapi
* Change report data parameter 
* Asynchronous report data
* Add data pending report count
* Fix agent name format
* Fix environment value get on windows
