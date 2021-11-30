import json
import os


class Config(object):
    def __init__(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(base_dir, '../config.json')
        with open(file_path, 'rb') as config:
            data = config.read()
            self.config = json.loads(data)

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
