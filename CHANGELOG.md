# Changelog

## Unreleased

* BUGFIXES
  * Fix SQL injection sink arguments processing

## [1.1.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.0) - 2021-11-05

* FEATURES
  * Agent pause/start by DongTai server
  * Agent pause/start based on system resource usage
  * Use environment variable `AUTO_CREATE_PROJECT=1` for auto create project
  * Report Agent startup time
  * Add Reflected XSS detection
  * Add XXE detection
  * Add SSRF detection
* BUGFIXES
  * Fix report data parameter`className` to fully named class name
  * Fix report data request/response body format
  * Fix streaming response processing
  * Fix response body processing
  * Fix Django request form data processing
  * Fix missing `kwargs` parameter for taint data
  * Fix invalid tainted data in method pool
  * Fix incorrect filter of tainted data
* BUILD
  * Auto upload package to Aliyun OSS by Github actions
  * Add vulnerability testing Github actions
* TESTING
  * Add vulnerability testing script

## [1.0.6](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.0.6) - 2021-10-26

* Auto update on start with `dongtai-cli`
* Pull policy rules from openapi
* Change report data parameter 
* Asynchronous report data
* Add data pending report count
* Fix agent name format
* Fix environment value get on windows
