# Changelog

## Unreleased

* FEATURES
  * Add installed packages report for SCA [#100](https://github.com/HXSecurity/DongTai-agent-python/pull/100)
* BUGFIXES
  * Fix memory leak when use requests [#99](https://github.com/HXSecurity/DongTai-agent-python/pull/99)

## [1.2.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.2.1) - 2022-01-05

* BUGFIXES
  * Fix memory leak in fstring hook [#97](https://github.com/HXSecurity/DongTai-agent-python/pull/97)

## [1.2.0](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.2.0) - 2021-12-31

* FEATURES
  * Add `pymongo` hook rules for NoSQL injection detection [#84](https://github.com/HXSecurity/DongTai-agent-python/pull/84)
  * Add `python-ldap` and `ldap3` hook rules for LDAP injection detection [#86](https://github.com/HXSecurity/DongTai-agent-python/pull/86), [#88](https://github.com/HXSecurity/DongTai-agent-python/pull/88)
  * Use the environment variable `DEBUG=1` to enable debug mode [#92](https://github.com/HXSecurity/DongTai-agent-python/pull/92)
* BUGFIXES
  * Fix request and response header formats [#87](https://github.com/HXSecurity/DongTai-agent-python/pull/87)
  * Bypass the hook in the filter rules [#93](https://github.com/HXSecurity/DongTai-agent-python/pull/93)
* TESTING
  * When testing for vulnerabilities, separate Django and Flask project names [#94](https://github.com/HXSecurity/DongTai-agent-python/pull/94), [DockerVulspace#8](https://github.com/jinghao1/DockerVulspace/pull/8)

## [1.1.4](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.4) - 2021-12-18

* FEATURES
  * Add [funchook](https://github.com/kubo/funchook) for Python C API functions/methods
  * Add `fstring` patch
  * Add `str/bytes/bytearray` `cformat(%)` patches
  * Add `str.__new__`, `bytes.__new__`, `bytearray.__init__` patches
  * Add `pickle.load`, `pickle.loads` hook rules for Insecure Deserialization detection
  * Add some filtering rules for HTML escaping
* BUGFIXES
  * Fix `yaml.load` and `yaml.load_all` sink parameters check
* CHANGES
  * Change `yaml.load`, `yaml.unsafe_load` strategy type to Insecure Deserialization
  * For requests containing multiple sink methods, tracking is no longer stopped after the first sink method is detected
* BUILD
  * Support for C extension build under Windows
  * Add build actions on Ubuntu/macOS/Windows

## [1.1.3](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.3) - 2021-12-03

* FEATURES
  * Use the environment variable `ENGINE_NAME` to customize agent name
  * Use the environment variable `LOG_PATH` to customize log file path
  * Add `exec` hook and policy rule to detect code execution vulnerabilities
* ENHANCEMENTS
  * Code refactoring: Add scope to prevent recursive execution of the agent's own code
  * Code refactoring: Add runtime settings and replace the configuration that uses global variables
  * Code refactoring: Add request context to store tainted data
  * Performance improvements: Tainted data processing optimization
  * Performance improvements: Remove unnecessary `list` policy rules
* BUGFIXES
  * Fix `eval` exceptions with contextual variables

## [1.1.1](https://github.com/HXSecurity/DongTai-agent-python/releases/tag/v1.1.1) - 2021-11-20

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
