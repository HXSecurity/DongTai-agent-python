import os, sys, subprocess, json, string, random, requests
from subprocess import Popen, PIPE
from dongtai_agent_python.cli import command, usage, log_message


@command('run', '...',
         """Executes the command with agent upgrade at startup""")
def run(args):
    if len(args) == 0:
        usage('run')
        sys.exit(1)

    config_data = get_config()
    if not isinstance(config_data, dict):
        sys.exit(1)

    try:
        update(config_data)
    except Exception as e:
        log_message("agent update failed: " + str(e))
        sys.exit(1)

    cmd_path = args[0]

    if not os.path.dirname(cmd_path):
        search_path = os.environ.get('PATH', '').split(os.path.pathsep)
        for path in search_path:
            path = os.path.join(path, cmd_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                cmd_path = path
                break

    os.execl(cmd_path, *args)


def get_config():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, './config.json')
    with open(file_path, 'rb') as config:
        config_data = json.loads(config.read())
        config.close()

    if not config_data.get("iast", {}).get("server", {}).get("url", ""):
        log_message("agent config server url invalid")
        return None
    return config_data


def get_project_name(config_data):
    server_env = dict(os.environ)
    project_name = config_data.get("project", {}).get("name", "Demo Project")
    if isinstance(server_env, dict):
        if server_env.get("projectName", ""):
            project_name = server_env.get("projectName", "")
        elif server_env.get("PROJECTNAME", ""):
            # windows always upper case env key
            project_name = server_env.get("PROJECTNAME", "")
    return project_name


def update(config_data):
    headers = {
        "Authorization": "Token " + config_data.get("iast", {}).get("server", {}).get("token", ""),
        "user-agent": "DongTaiIAST-Agent",
        'content-encoding': 'gzip',
        'content-type': "application/json"
    }

    url = config_data.get("iast", {}).get("server", {}).get("url", "") + "/api/v1/agent/download"
    params = {
        "url": url,
        "language": "python",
        "projectName": get_project_name(config_data),
    }

    dir = os.path.dirname(__file__)
    rnd = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    filename = dir + os.sep + "dongtai-agent-python-" + rnd + ".tar.gz"
    resp = requests.get(url, params, timeout=60, headers=headers)
    with open(filename, "wb") as f:
        f.write(resp.content)
        f.close()

    ret = run_command([sys.executable, "-m", "pip", "install", filename])
    if ret['code'] != 0:
        ret = run_command([sys.executable, "-m", "pip", "install", "--user", filename])
        if ret['code'] != 0:
            os.remove(filename)
            raise Exception('pip install failed, ' + ret['error'].decode("utf-8"))
    os.remove(filename)

    old_engine_version = config_data.get("engine", {}).get("version", "")
    new_config = get_config()
    new_engine_version = new_config.get("engine", {}).get("version", "")
    if old_engine_version == new_engine_version:
        save_config_data(config_data)
        log_message("agent version is not outdated: " + old_engine_version)
        return

    config_data["engine"]["version"] = new_engine_version
    save_config_data(config_data)
    log_message("upgrade agent from %s to %s success" % (old_engine_version, new_engine_version))


def run_command(args):
    p = Popen(args, stdout=PIPE, stderr=PIPE)
    output = p.communicate()
    return {
        'code': p.returncode,
        'output': output[0],
        'error': output[1]
    }


def save_config_data(config_data):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, './config.json')
    with open(file_path, 'w', newline='\n') as config:
        json.dump(config_data, config, indent=2)
