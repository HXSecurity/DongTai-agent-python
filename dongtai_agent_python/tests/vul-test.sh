#!/bin/bash

HOST=$1

if [ -z ${HOST} ]; then
  echo -e "api host required!"
  echo -e "Usage: $( basename $0 ) <api host>"
  exit 1
fi

# exec-command
curl "${HOST}/api/demo/exec_post_popen" -X POST --data-raw 'code=ls'
curl "${HOST}/api/demo/exec_post_subprocess" -X POST --data-raw 'cmd=cat&name=%2Fetc%2Fpasswd'
curl "${HOST}/api/demo/cmd_exec" -X POST --data-raw 'cmd=whoami'
curl "${HOST}/api/demo/exec_post_e" -X POST --data-raw 'code=whoami'
# exec-code
curl "${HOST}/api/demo/eval_post_e" -X POST --data-raw 'code=__import__%28%27os%27%29.system%28%27whoami%27%29'
curl "${HOST}/api/demo/yaml_post_e" -X POST --data-raw 'code=whoami'
# path-traversal
curl "${HOST}/api/demo/get_open?name=Data"
curl "${HOST}/api/demo/post_open" -X POST --data-raw 'name=.%2Ffile%2Fdata.json'
# sql-injection
curl "${HOST}/api/demo/postgresql_post_many" -X POST --data-raw 'id=100&name=song&phone1=13300000000'
curl "${HOST}/api/demo/postgresql_post_excute" -X POST --data-raw 'name=song'
curl "${HOST}/api/demo/mysql_post_many" -X POST --data-raw 'name=song&phone1=13300000000'
curl "${HOST}/api/demo/mysql_post_exec" -X POST --data-raw 'name=song'
curl "${HOST}/api/demo/sqlite3_post_executemany_sql" -X POST --data-raw 'phone1=13300000000'
curl "${HOST}/api/demo/sqlite3_post_executescript" -X POST --data-raw 'name=song&phone1=13300000000'
curl "${HOST}/api/demo/sqlite3_post" -X POST --data-raw 'name=song'

