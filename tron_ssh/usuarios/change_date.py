from consolemenu.format.menu_color import RED, GREEN, DEFAULT
from usuarios.utils import Utils
from utils import logger
from datetime import datetime, timedelta

class Date(Utils):
    def __init__(self, title):
        super(Date, self).__init__(title)
        self.date = None
        self.fmt_date = None
        self.days = None

    def create_date(self):
        date = timedelta(days=self.days) + datetime.now()
        self.date = date.strftime('%d/%m/%Y')
        self.fmt_date = date.strftime('%Y-%m-%d')
    
    def check_days(self, days):
        try:
            days = int(days)
            if days <= 0:
                logger.error('Dias deve ser maior que zero')
                return None
            self.days = days
            self.running = False
        except:
            logger.error('Dias invalido')
            return None

    def update_date(self, username):
        cmd = 'chage -d %s %s' % (self.fmt_date, username)
        self.shell(cmd)
    
    def info(self, username, user_id):
        logger.info('Usuario ' + username)
        current_date = self.sqlite.user_info(user_id)
        if current_date[4] is None:
            current_date = f'{RED}Data nao encontrada{DEFAULT}'
        else:
            current_date = GREEN + current_date[4] + DEFAULT
        while self.running:
            days = self._user_input('Novos dias: ')
            self.check_days(days)

    def action(self, user_id):
        username = self.get_user(user_id)
        self.info(username, user_id)
        self.create_date()
        self.update_date(username)
        self.sqlite.update_info(user_id, 'date', self.date)
        logger.sucess('Data alterada para ' + self.date + ' com sucesso')
        self.running = True
        self._user_input('')

def change_date():
    date = Date('ALTERAR DATA')
    date.start()
    date.join()