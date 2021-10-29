#!/bin/bash

HOST=$1
RUN_ID=$2
if [ -z ${HOST} ]; then
  echo -e "api host required!"
  echo -e "Usage: $( basename $0 ) <api host>"
  exit 1
fi

# exec-command
curl "${HOST}/api/demo/exec_post_popen?_r=${RUN_ID}" -X POST --data-raw 'code=ls'
echo
curl "${HOST}/api/demo/exec_post_subprocess?_r=${RUN_ID}" -X POST --data-raw 'cmd=cat&name=%2Fetc%2Fpasswd'
echo
curl "${HOST}/api/demo/cmd_exec?_r=${RUN_ID}" -X POST --data-raw 'cmd=whoami'
echo
curl "${HOST}/api/demo/exec_post_e?_r=${RUN_ID}" -X POST --data-raw 'code=whoami'
echo
# exec-code
curl "${HOST}/api/demo/eval_post_e?_r=${RUN_ID}" -X POST --data-raw 'code=__import__%28%27os%27%29.system%28%27whoami%27%29'
echo
curl "${HOST}/api/demo/yaml_post_e?_r=${RUN_ID}" -X POST --data-raw 'code=whoami'
echo
# path-traversal
curl "${HOST}/api/demo/get_open?name=Data**&_r=${RUN_ID}"
echo
curl "${HOST}/api/demo/post_open?_r=${RUN_ID}" -X POST --data-raw 'name=.%2Ffile%2Fdata.json'
echo
# sql-injection
curl "${HOST}/api/demo/postgresql_post_many?_r=${RUN_ID}" -X POST --data-raw 'id=100&name=song&phone1=13300000000'
echo
curl "${HOST}/api/demo/postgresql_post_excute?_r=${RUN_ID}" -X POST --data-raw 'name=song'
echo
curl "${HOST}/api/demo/mysql_post_many?_r=${RUN_ID}" -X POST --data-raw 'name=song&phone1=13300000000'
echo
curl "${HOST}/api/demo/mysql_post_exec?_r=${RUN_ID}" -X POST --data-raw 'name=song'
echo
curl "${HOST}/api/demo/sqlite3_post_executemany_sql?_r=${RUN_ID}" -X POST --data-raw 'phone1=13300000000'
echo
curl "${HOST}/api/demo/sqlite3_post_executescript?_r=${RUN_ID}" -X POST --data-raw 'name=song&phone1=13300000000'
echo
curl "${HOST}/api/demo/sqlite3_post?_r=${RUN_ID}" -X POST --data-raw 'name=song'
echo
