import signal
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(sys.modules[__name__].__file__), '..')))

from scripts.execute import Process
from usuarios.utils import Utils
from usuarios.utils import SQLite
from usuarios.utils import ssh_pids_user
from datetime import datetime, timedelta

class UserTime:
    def __init__(self, username):
        self.username = username
        self.user_id = Utils.get_id_from_user(username)
        self.start_time = self._now()
    
    @staticmethod
    def _now():
        return datetime.now()
    
    @property
    def _total_seconds(self):
        return (self._now() - self.start_time).total_seconds()
    
    @property
    def _hour(self):
        return int(self._total_seconds // 3600)
    
    @property
    def _minute(self):
        return int(self._total_seconds % 3600 // 60)
    
    @property
    def _seconds(self):
        return int(self._total_seconds % 3600 % 60)
    
    def status(self):
        return len(ssh_pids_user(self.username)) > 0

    def format(self):
        return '%02d:%02d:%02d' % (self._hour, self._minute, self._seconds)
    
    def __eq__(self, o):
        return o.username == self.username and o.user_id == self.user_id

class TimeSSH:
    def __init__(self):
        self.users = []
        self.running = False
        self.porcess = Process()
        self.porcess.save_process('ssh_time.py', os.getpid())
    
    @property
    def sqlite(self):
        return SQLite()
    
    def append_user(self, user):
        user_time = UserTime(user)
        if user_time.status() and not user_time in self.users:
            self.users.append(user_time)
    
    def remove_user(self, user):
        for idx, _user in enumerate(self.users):
            if user == _user:
                self.sqlite.update_info(user.user_id, 'time', '00:00:00')
                del self.users[idx]

    def save_info_time(self):
        for user in self.users:
            user_id = Utils.get_id_from_user(user.username)
            if user.status():
                self.sqlite.update_info(user_id, 'time', user.format())
            else:
                self.remove_user(user)
    
    def run(self):
        while True:
            for user in Utils.list_users():
                self.append_user(user)
            self.save_info_time()
    
    def close(self):
        self.running = False
        for user in self.users:
            self.remove_user(user)
            
def main():
    try:
        sshtime = TimeSSH()
        sshtime.run()
    except KeyboardInterrupt:
        sshtime.close()

if __name__ == '__main__':
    main()