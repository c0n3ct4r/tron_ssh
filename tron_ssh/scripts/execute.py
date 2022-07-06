import subprocess
import os
import json
import errno

class Process:
    FILE_JSON = os.path.abspath('scripts/process.json')

    @staticmethod
    def info_json():
        data = open(Process.FILE_JSON).read()
        return json.loads(data)
    
    def save_json(self, info):
        wfile = open(Process.FILE_JSON, 'w')
        wfile.write(json.dumps(info, indent=4))
        wfile.close()
    
    @property
    def process_names(self):
        return list(self.info_json().keys())

    def process_name(self, name):
        return self.info_json().get(name, None)
    
    def process_exists(self, pid):
        try:
            os.kill(pid, 0)
        except OSError as e:
            return e.errno == errno.EPERM
        else:
            return True
    
    def kill_process(self, pid, sig):
        os.kill(pid, sig)
    
    def remove_process(self, process_name):
        info = self.info_json()
        del info[process_name]
        self.save_json(info)
    
    def save_process(self, process_name, pid):
        info = self.info_json()
        info[process_name] = pid
        self.save_json(info)

class Execute:
    def __init__(self):
        self.dir_scripts = os.path.abspath('scripts')

    def name_scripts(self):
        return Process.info_json()['scripts_names']

    def _exec(self, name_script):
        os.system('nohup python3 ' + os.path.join(self.dir_scripts, name_script) + '&>/dev/null &')
    
    
    
