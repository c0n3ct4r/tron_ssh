from consolemenu.format.menu_color import RED, GREEN, DEFAULT
from utils import logger
from usuarios.utils import Utils

class Limit(Utils):
    def __init__(self, title):
        super(Limit, self).__init__(title)
        self.limit = None
    
    def check_limit(self, limit):
        try:
            limit = int(limit)
            if limit <= 0:
                logger.error('Limite deve ser maior que zero')
                return None
            self.limit = limit
            self.running = False
        except:
            logger.error('Limite invalido')
            return None
    
    def info(self, user_id):
        username = self.get_user_from_id(user_id)
        current_limit = self.sqlite.user_info(user_id)[3]
        logger.info('Usuario: ' + username)
        if current_limit is None:
            current_limit = f'{RED}Limite nao encontrado{DEFAULT}'
        else:
            current_limit = f'{GREEN}%02d{DEFAULT}' % current_limit
        logger.info('Limite atual: ' + current_limit)
        while self.running:
            limit = self._user_input('Novo limite: ')
            self.check_limit(limit)
    
    def action(self, user_id):
        self.info(user_id)
        self.sqlite.update_info(user_id, 'limite', self.limit)
        logger.success('Limite alterado com sucesso')
        self.running = True
        self._user_input('')

def change_limit():
    limit = Limit('ALTERAR LIMITE')
    limit.start()
    limit.join()