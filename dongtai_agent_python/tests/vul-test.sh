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
    failed "response error"
  fi
  echo $body
  echo
}

api_get() {
  local API_PATH=$1
  local QUERY=$2
  local FW=$3

  # shellcheck disable=SC2154
  if [[ "${FW}z" -eq "z" ]]; then
    echo "=========================== GET /api/${FRAMEWORK}/$API_PATH"
    echo
    curl_with_code  "${HOST}/api/${FW}/${API_PATH}?_r=${RUN_ID}&${QUERY}"
    echo
  else
    for FRAMEWORK in "${FRAMEWORKS[@]}"; do
      echo "=========================== GET /api/${FRAMEWORK}/$API_PATH"
      echo
      curl_with_code  "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}&${QUERY}"
      echo
    done
  fi
}

api_post() {
  local API_PATH=$1
  local DATA=$2
  local FW=$3

  if [[ "${FW}z" -eq "z" ]]; then
    echo "=========================== POST /api/${FRAMEWORK}/$API_PATH"
    echo
    curl_with_code "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}" -X POST --data-raw $DATA
    echo
  else
    for FRAMEWORK in "${FRAMEWORKS[@]}"; do
      echo "=========================== POST /api/${FRAMEWORK}/$API_PATH"
      echo
      curl_with_code "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}" -X POST --data-raw $DATA
      echo
    done
  fi
}

headline "exec-command"
api_post "demo/exec_post_popen" "code=ls"
api_post "demo/exec_post_subprocess" "cmd=cat&name=%2Fetc%2Fpasswd"
api_post "demo/cmd_exec" "cmd=whoami"
api_post "demo/exec_post_e" "code=whoami"

headline "exec-code"
api_post "demo/eval_post_e" "code=__import__%28%27os%27%29.system%28%27whoami%27%29"
api_post "demo/yaml_post_e" "code=whoami"

headline "path-traversal"
api_get "demo/get_open" "name=Data**"
api_post "demo/post_open" "name=.%2Ffile%2Fdata.json"

headline "sql-injection"
api_post "demo/postgresql_post_many" "id=1000&name=song&phone1=13300000000" django
api_post "demo/postgresql_post_many" "id=2000&name=song&phone1=13300000000" flask
api_post "demo/postgresql_post_excute" "name=song"
api_post "demo/mysql_post_many" "name=song&phone1=13300000000"
api_post "demo/mysql_post_exec" "name=song"
api_post "demo/sqlite3_post_executemany_sql" "phone1=13300000000"
api_post "demo/sqlite3_post_executescript" "name=song&phone1=13300000000"
api_post "demo/sqlite3_post" "name=song"

headline "xss"
api_get "demo/xss_return" "content=alert"
api_get "demo/xss_template" "content=alert"
api_get "demo/xss_template_string" "content=alert"

headline "xxe"
cat > $XXE_PAYLOAD <<- EOM
<?xml version="1.0" encoding="utf-8"?>
 <!DOCTYPE Anything [
 <!ENTITY xxe SYSTEM "file:///etc/passwd">
 ]>
 <user>
  <username>&xxe;</username>
  <password>
    yzx
  </password>
 </user>
EOM
api_post "demo/xxe_login" '$XXE_PAYLOAD'

headline "ssrf"
api_get "demo/urllib_ssrf" "url=https://www.huoxian.cn/"
api_get "demo/request_ssrf" "url=https://www.huoxian.cn/"
