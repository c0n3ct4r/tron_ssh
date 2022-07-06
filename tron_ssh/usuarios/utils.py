import os, re, json
import sqlite3
import threading
from consolemenu import ConsoleMenu
from consolemenu.items import FunctionItem, MenuItem, ExitItem

def ssh_pids_user(user):
    cmd = 'bash -c \'ps -u %s 2>/dev/null\'' % user
    pids = [line.split()[0] for line in os.popen(cmd).readlines()
        if line.split()[3] == 'sshd']
    return pids

class SQLite:
    def __init__(self):
        if not os.path.exists('usuarios/database'):
            os.mkdir('usuarios/database')
        self.sql = sqlite3.connect('usuarios/database/usuarios.db')
        self.cursor = self.sql.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute(
            'CREATE TABLE IF NOT EXISTS usuarios \
            (id integer PRIMARY KEY, username text, password text, limite integer, date text, time text)'
        )
        self.sql.commit()

    def append_info(self, user_id, username, password, limit, date, time):
        self.cursor.execute('INSERT INTO usuarios VALUES (?, ?, ?, ?, ?, ?)', (
            user_id, username, password, limit, date, time
        ))
        self.sql.commit()

    def delete_info(self, user_id):
        sql = 'DELETE from usuarios where id = %d' % user_id
        self.cursor.execute(sql)
        self.sql.commit()

    def update_info(self, user_id, item, value):
        self.cursor.execute('Update usuarios set %s = ? where id = ?' % (item), (value, user_id))
        self.sql.commit()

    def user_info(self, user_id):
        sql = 'SELECT * FROM usuarios WHERE id=?'
        self.cursor.execute(sql, [(user_id)])
        info = self.cursor.fetchall()
        if info: info = info[0]
        return info
    
    def users_info(self):
        sql = 'SELECT * FROM usuarios'
        self.cursor.execute(sql)
        return self.cursor.fetchall()
    
    @staticmethod
    def database_exits():
        return os.path.isfile('usuarios/database/usuarios.db')

    def close(self):
        self.cursor.close()
        self.sql.close()

class BackItem(ExitItem):
    def __init__(self):
        super(BackItem, self).__init__('VOLTAR')

class Utils(ConsoleMenu):
    def __init__(self, title, auto=True):
        super(Utils, self).__init__(title, show_exit_option=False)
        self.running = True
        if auto: self.create_items()
    
    @property
    def sqlite(self):
        return SQLite()

    def create_items(self):
        for username in self.list_users():
            self.create_item(username)
        self.append_item(BackItem())
    
    def create_item(self, username):
        user_id = self.get_id_from_user(username)
        item = FunctionItem(username, self.action, args=(user_id,))
        item.user_id = user_id
        self.append_item(item)
    
    def get_user(self, user_id):
        return self.get_user_from_id(user_id)
    
    def action(self, user_id):
        pass
    
    def delete_item(self, user_id):
        for item in self.items[:-1]:
            if item.user_id == user_id:
                self.remove_item(item)
                self.resume()            

    def kill_user_pid(self, username):
        for pid in ssh_pids_user(username):
            os.kill(int(pid), 7)
    
    def _user_input(self, prompt):
        return input(prompt)
    
    @staticmethod
    def shell(cmd):
        bash = 'bash -c \'%s\' &>/dev/null' % cmd
        return os.system(bash)
    
    @staticmethod
    def get_id_from_user(user):
        if SQLite.database_exits():
            for info in SQLite().users_info():
                if info[1] == user:
                    return info[0]

        for line in open('/etc/passwd').readlines():
            line = line.split(':')
            if line[0] == user: return int(line[2])
        return None
    
    @staticmethod
    def get_user_from_id(user_id):
        if SQLite.database_exits():
            info = SQLite().user_info(user_id)
            if info: return info[1]

        for line in open('/etc/passwd').readlines():
            line = line.split(':')
            if int(line[2]) == user_id: return line[0]
        return None
    
    @staticmethod
    def list_users():
        users = [user.split(':')[0] for user in open('/etc/passwd').readlines()
            if user.split(':')[0] != 'nobody' and int(user.split(':')[2]) >= 1000]
        if SQLite.database_exits():
            for info in SQLite().users_info():
                if not info[1] in users:
                    users.append(info[1])
        return users