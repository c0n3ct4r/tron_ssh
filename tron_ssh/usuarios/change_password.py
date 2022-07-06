from consolemenu.format.menu_color import RED, GREEN, DEFAULT
from utils import logger
from usuarios.utils import Utils

class Password(Utils):
    def __init__(self, title):
        super(Password, self).__init__(title)
        self.password = None
    
    def update(self, user_id):
        self.sqlite.update_info(user_id, 'password', self.password)
        self.sqlite.close()
    
    def check_password(self, password):
        if len(password) > 12:
            logger.error('Senha muito grande')
        elif len(password) < 3:
            logger.error('Senha muito pequena')
        elif not password.isalnum():
            logger.error('Use apenas numeros e letras')
        else:
            self.password = password
            self.running = False

    def info(self, username, user_id):
        logger.info('Usuario: ' + username) 
        current_password = self.sqlite.user_info(user_id)[2]
        if current_password is None:
            current_password = f'{RED}Senha nao encontrada{DEFAULT}'
        else:
            current_password = GREEN + current_password + DEFAULT
        logger.info('Senha atual: ' + current_password)
        while self.running:
            password = self._user_input('Nova senha: ')
            self.check_password(password)
    
    def action(self, user_id):
        self.info(self.get_user(user_id), user_id)
        self.update(user_id)
        logger.success('Senha alterada com sucesso')
        self.running = True
        self._user_input('')

def change_password():
    menu = Password('ALTERAR SENHA')
    menu.start()
    menu.join()