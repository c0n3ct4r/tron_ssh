import threading
import time
from .utils import SQLite
from .utils import Utils
from .utils import ssh_pids_user
from consolemenu.screen import Screen
from consolemenu.format.menu_color import RED, GREEN, DEFAULT, BGGREY, YELLOW

COLOR_NULL = RED + 'null' + DEFAULT

class InfoUser:
    def __init__(self, username):
        self.username_colored = GREEN + username + DEFAULT
        self.username = username
        self.user_id = Utils.get_id_from_user(self.username)
    
    @property
    def _sqlite(self):
        return SQLite()
    
    @property
    def limit(self):
        data = self._sqlite.user_info(self.user_id)
        if data and not data[3] is None:
            if data[3] < 100:
                return GREEN + '%02d ' % data[3] + DEFAULT
            else:
                return GREEN + '%02d' % data[3] + DEFAULT
        return COLOR_NULL
    
    @property
    def time(self):
        data = self._sqlite.user_info(self.user_id)
        if data and data[5] != '00:00:00':
            return GREEN + data[5] + DEFAULT
        else:
            return RED + data[5] + DEFAULT
    
    @property
    def status(self):
        if ssh_pids_user(self.username):
            return GREEN + 'ON' + DEFAULT
        return RED + 'OFF' + DEFAULT
    
    @property
    def total_connections(self):
        pids = ssh_pids_user(self.username)
        if len(pids) > 0:
            return f'{GREEN}%02d{DEFAULT}' % len(pids) 
        return RED + '00' + DEFAULT
    
    def _tuple_monitor(self):
        width = max(len(line) for line in Utils.list_users()) + len(f'{RED}{DEFAULT}')
        return (self.username_colored.ljust(width + 8), self.status.ljust(width + 5),
        '%s/%s'.ljust(11) % (self.total_connections, self.limit), self.time)

class InputUser(threading.Thread):
    def __init__(self):
        super(InputUser, self).__init__()
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            if input().lower() == 'q':
                self.running = False

class Formatter:
    def __init__(self):
        self.screen = Screen()
        self.__style_colum = '-'
        self.__style_bar = '='
        self.__text = ' %s %s %s %s\n'
        self.input = InputUser()
        self.input.start()
    
    def formatter(self):
        content = f'{RED}{self.__style_bar}{DEFAULT}' * 50 + '\n'
        content += f'{BGGREY} {GREEN}USUARIO       STATUS       CONEXAO       TEMPO   {DEFAULT}\n'
        content += f'{RED}{self.__style_bar}{DEFAULT}' * 50 + '\n'
        for user in Utils.list_users():
            info = InfoUser(user)
            content += self.__text % (info._tuple_monitor())
            content += f'{RED}{self.__style_colum}{DEFAULT}' * 50 + '\n'
        content += f'\n{YELLOW}DIGITE Q E DE ENTER PRA SAIR {DEFAULT}'
        return content

    def show(self):
        while self.input.running:
            self.screen.printf(self.formatter())
            time.sleep(1)
            self.screen.clear()

def monitor_ssh():
    formatter = Formatter()
    formatter.show()
