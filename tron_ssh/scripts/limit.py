import threading
import signal
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), '..')))

from scripts.execute import Process
from usuarios.utils import ssh_pids_user
from usuarios.utils import Utils
from usuarios.utils import SQLite
from utils import logger

class Limit:
    def __init__(self, username):
        self.porcess = Process()
        self.username = username
        self.user_id = Utils.get_id_from_user(username)
        self.porcess.save_process('limit.py', os.getpid())
    
    @property
    def sqlite(self):
        return SQLite()

    @property
    def limit(self):
        info = self.sqlite.user_info(self.user_id)
        if info: return info[3]
        return None
    
    def kill_pid_user(self, pids):
        logger.info('Parando %02d conexoes' % len(pids))
        for pid in pids:
            self.porcess.kill_process(int(pid), signal.SIGTERM)
    
    def run(self):
        if not self.limit is None:
            index = len(ssh_pids_user(self.username)) - self.limit
            if index > 0:
                logger.warn('Usuario %s ultrapassou o limite' % self.username)
                self.kill_pid_user(ssh_pids_user(self.username)[-index:])
    
def main():
    while True:
        for user in Utils.list_users():
            limit = Limit(user)
            limit.run()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass