# Changelog

## [1.1.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.1) - 2021-11-19

* FEATURES
  * Add agent auditing on startup
  * Use environment variable `PROJECT_VERSION` for auto create project version
* ENHANCEMENTS
  * Add Django template hook rule for XSS detection
  * Add old version werkzeug request body hook rule
  * Add Django route match hook rule
* BUGFIXES
  * Fix SQL injection sink arguments processing
  * Fix the duplicate agent name caused by using the same configuration file under multiple frameworks
  * Fix the problem that Django response body is getting empty
  * Fix object hash generation method to avoid duplicate hashes
  * Fix the problem of method pooling under multiple threads
  * Fix the case that some methods return values from their own parameters
  * Fix old version werkzeug compatibility

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
