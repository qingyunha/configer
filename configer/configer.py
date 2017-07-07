import os
import time
import json
import logging

import yaml

logger = logging.getLogger("Configer")

class ConfigerError(Exception): pass

class ConfigFileNotFind(ConfigerError): pass

class ConfigSetError(ConfigerError): pass

class ConfigUnSupportType(ConfigerError): pass



class Configer:

    support_exts = ['json', 'yaml']

    def __init__(self):
        self.key_delim = "."

        # about configure file
        self.paths = ["."]
        self.name = "config"
        self.type = None

        self.config = {}
        self.override = {}
        self.defaults = {}
        self.envs = {}
        self.env_prefix = None

        self.onchange = None

    def read(self):
        filename = self.get_file()
        _type = self.get_type()
        logger.debug("read %s config file", _type)
        if _type not in self.support_exts:
            raise ConfigUnSupportType()
        with open(filename, 'rb') as f:
            self.config = self.load(f, _type)

    def get_file(self):
        f = self.find_file()
        if not f:
            raise ConfigFileNotFind()
        return f

    def find_file(self):
        for d in self.paths:
            f = self.search_in_path(d)
            if f:
                return f

    def search_in_path(self, d):
        for ext in self.support_exts:
            f = os.path.join(d, self.name+'.'+ext)
            if os.path.exists(f):
                return f

    def get_type(self):
        if self.type:
            return self.type
        f = self.get_file()
        _, ext = os.path.splitext(f)
        return ext[1:]

    def set_type(self, _type):
        self.type = _type

    def load(self, f, _type):
        if _type == 'json':
            return json.load(f)
        if _type == 'yaml':
            return yaml.load(f)

    def bind_env(self, key, env_var=None):
        if env_var:
            self.envs[key] = env_var
        else:
            self.envs[key] = key

    def get_env(self, key):
        if self.env_prefix:
            key = self.env_prefix + key
        return os.getenv(key)

    def set_env_prefix(self, prefix):
        self.env_prefix = prefix
            
    def get(self, keys):
        keypaths = keys.split(self.key_delim)
        v = self.search_vaule(keypaths, self.override)
        logger.debug("get %s from override: %s", keypaths, v)
        if v: return v

        if len(keypaths) == 1 and keys in self.envs:
            v = self.get_env(keys)
            logger.debug("get %s from ENV: %s", keypaths, v)
            if v: return v

        v = self.search_vaule(keypaths, self.config)
        logger.debug("get %s from config: %s", keypaths, v)
        if v: return v

        v = self.search_vaule(keypaths, self.defaults)
        logger.debug("get %s from defaults: %s", keypaths, v)
        if v: return v

    def search_vaule(self, keypaths, _dict):
        v = _dict
        for k in keypaths:
            try:
                v = v.get(k, None)
                if not v:
                    return
            except ValueError:
                return
        return v

    def set(self, keys, value):
        self.set_value(keys, value, self.override)

    def set_default(self, keys, value):
        self.set_value(keys, value, self.defaults)

    def set_value(self, keys, value, _dict):
        keypaths = keys.split(self.key_delim)
        v = _dict
        for k in keypaths[:-1]:
            r = v.get(k, {})
            if not isinstance(r, dict):
                raise ConfigSetError()
            if r == {}:
                v[k] = r
            v = r
        v[keypaths[-1]] = value

    def add_path(self, path):
        self.paths.insert(0, path)

    def set_name(self, name):
        self.name = name

    def reset(self):
        self.key_delim = "."
        self.file = ""
        self.paths = ["."]
        self.name = "config"
        self.type = None

        self.config = {}
        self.override = {}
        self.defaults = {}
        self.envs = {}
        self.env_prefix = None

    def watch_config(self, onchange=None, m='thread'):
        """m: thread or gevent."""
        self.onchange = onchange
        if m == 'thread':
            from threading import Thread
            t = Thread(target=self.watch_change)
            t.daemon = True
            t.start()
        elif m == 'gevent':
            import gevent.monkey
            gevent.monkey.patch_time()
            gevent.spawn(self.watch_change)

    def watch_change(self):
        old_mtime = None
        old_f = None
        while True:
            logging.debug("watch change....")
            time.sleep(1)
            try:
                f = self.get_file()
            except ConfigFileNotFind:
                continue
            # filename change
            if old_f != f:
                old_f = f
                try:
                    self.read()
                    if self.onchange:
                        self.onchange()
                except ConfigerError as e:
                    logging.warning(e)
                except Exception as e:
                    logging.warning(e)
                continue
            # mtime change
            try:
                mtime = os.stat(f).st_mtime
            except OSError as e:
                logging.warning(e)
                continue
            if old_mtime is None:
                old_mtime = mtime
                continue
            if mtime > old_mtime:
                old_mtime = mtime
                try:
                    self.read()
                    if self.onchange:
                        self.onchange()
                except ConfigerError as e:
                    logging.warning(e)
                except Exception as e:
                    logging.warning(e)

C = Configer()
