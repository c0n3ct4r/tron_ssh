from consolemenu import ConsoleMenu
from consolemenu.items import MenuItem, SubmenuItem, FunctionItem
from usuarios.utils import Utils
from usuarios.utils import SQLite
from usuarios.create_user import create_user
from usuarios.delete_user import delete_user
from usuarios.change_password import change_password
from usuarios.change_limit import change_limit
from usuarios.change_date import change_date
from usuarios.monitor_ssh import monitor_ssh
from scripts.execute import Process, Execute
import os

if not os.path.exists('/etc/ip'):
    from urllib.request import urlopen
    with open('/etc/ip', 'w') as e:
        e.write(urlopen('http://ipv4.icanhazip.com').read().decode().strip())
    e.close()

class Users:
    def __init__(self):
        self.run()

    @property
    def _sql(self):
        return SQLite()

    def user_exists_in_db(self, user_id):
        return self._sql.user_info(user_id)

    def run(self):
        for user in Utils.list_users():
            user_id = Utils.get_id_from_user(user)
            if not self.user_exists_in_db(user_id):
                self._sql.append_info(user_id, user, None, None, None, '00:00:00')

class CheckProcess:
    def __init__(self):
        self.scripts_name = ['limit.py', 'ssh_time.py']
        self.process = Process()
        self.exec = Execute()
        self.check_process()

    def check_process(self):
        try:
            for script_name in self.scripts_name:
                pid = self.process.process_name(script_name)
                if not pid is None:
                    if not self.process.process_exists(pid):
                        self.exec._exec(script_name)
                else:
                    self.exec._exec(script_name)
        except:
            pass

menu = ConsoleMenu('MENU', exit_option_text='SAIR')
menu.append_item(MenuItem('INSTALADOR DE PACOTES'))

submenu_2 = ConsoleMenu('GERENCIAR USUARIO', exit_option_text='VOLTAR')
submenu_2.append_item(FunctionItem('CRIAR USUARIO', create_user))
submenu_2.append_item(FunctionItem('DELETAR USUARIO', delete_user)) 
submenu_2.append_item(FunctionItem('ALTERAR SENHA', change_password))
submenu_2.append_item(FunctionItem('ALTERAR LIMITE', change_limit))
submenu_2.append_item(FunctionItem('ALTERAR DATA', change_date))
submenu_2.append_item(FunctionItem('MONITOR SSH', monitor_ssh))
submenu_2.append_item(FunctionItem('INFO. DOS USUARIOS', input))
submenu_2.append_item(FunctionItem('REMOVER EXPIRADOS', input))
submenu_2.append_item(FunctionItem('CRIAR BACKUP', input))
submenu_2.append_item(FunctionItem('RESTAURAR BACKUP', input))
submenu_item_2 = SubmenuItem('GERENCIAR USUARIOS', submenu=submenu_2)
submenu_item_2.set_menu(menu)

menu.append_item(submenu_item_2)
menu.append_item(MenuItem('GERENCIAR SERVICOS'))
menu.append_item(MenuItem('GERENCIAR PORTAS'))

if __name__ == '__main__':

    try:
        CheckProcess()
        Users()
        menu.start()
        menu.join()
    except KeyboardInterrupt:
        pass
    finally:
        print('\nVolte logo :)')