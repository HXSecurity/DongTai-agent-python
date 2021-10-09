# -*- coding: utf-8 -*-
import os, json
global _global_dt_dict
from typing import IO


_global_dt_dict = {
    "dt_open_pool": True,
    "have_hooked": [],
    "upload_pool": False,
    "hook_exit": False,
    "policy": {},
    "req_count": 0
}


def _init():  # 初始化
    global _global_dt_dict


def dt_set_value(key, value):
    # 定义一个全局变量
    global _global_dt_dict
    _global_dt_dict[key] = value
    # print(_global_dt_dict)


def dt_get_value(key):
    global _global_dt_dict
    # 获得一个全局变量，不存在则提示读取对应变量失败
    try:
        return _global_dt_dict[key]
    except Exception as e:
        print('读取'+key+'失败\r\n')
        return ""


def get_config_data():
    # global dt_global_var
    dt_set_value("dt_open_pool",False)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, './config.json')
    config_data = {}
    with open(file_path, 'rb') as config:
        data = config.read()
        config_data = json.loads(data)
    dt_set_value("config_data", config_data)
    dt_set_value("dt_open_pool", True)
    return config_data