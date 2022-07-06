from .utils import Utils
from usuarios.utils import SQLite
from utils import logger

class Delete(Utils):
    def __init__(self, title):
        super(Delete, self).__init__(title)
    
    @property
    def sqlite(self):
        return SQLite()
    
    def confirm_action(self):
        return self._user_input('Voce deseja deletar? (s/n): ').lower() == 's'
    
    def delete_user(self, username, user_id):
        self.sqlite.delete_info(user_id)
        self.kill_user_pid(username)
        self.shell('userdel --force %s &>/dev/null' % username)

    def action(self, user_id):
        username = self.get_user(user_id)
        logger.info('Usuario: ' + username)
        if not self.confirm_action(): return
        logger.info('Deletando usuario...')
        self.delete_user(username, user_id)
        self.delete_item(user_id)
        logger.success('Usuario deletado com sucesso')
        input()            

def delete_user():
    menu = Delete('DELETAR USUARIOS')
    menu.start()
    menu.join()
