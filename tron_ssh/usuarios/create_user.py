from consolemenu.format.menu_bar import create_bar, MenuBar
from consolemenu.format.menu_color import RED, GREEN, DEFAULT, WHITE, YELLOW
from datetime import datetime, timedelta
from usuarios.utils import Utils
from usuarios.utils import SQLite
from utils import logger
import os

class CreateUser:
	def __init__(self):
		super(CreateUser, self).__init__()
		self.username = None
		self.password = None
		self.limit = None
		self.date = None
		self.logger = logger
	
	def create_user_id(self):
		if SQLite.database_exits():
			data = SQLite().users_info()
			if data: return max(info[0] for info in data) + 1
		for line in open('/etc/passwd').readlines():
			if int(line.split(':')[2]) >= 900 and line.split(':')[0] != 'nobody':
				return int(line.split(':')[2]) + 1
		return 1000
	
	def verify_info_user(self, info, data):
		if not data:
			self.logger.error('%s e invalido' % info)
		elif len(data) > 12:
			self.logger.error('%s e muito grande' % info)
		elif len(data) < 3:
			self.logger.error('%s e muito pequeno' % info)
		elif not data.isalnum():
			self.logger.error('Use apenas numeros e letras')
		else:
			return data
		return None

	def _username(self):
		while not self.username:
			username = input(GREEN + 'Usuario: ' + DEFAULT)
			if username in Utils.list_users():
				self.logger.error('Usuario %s ja existe' % username)
			else:
				self.username = self.verify_info_user('Usuario', username)

	def _password(self):
		while not self.password:
			password = input(GREEN + 'Senha: ' + DEFAULT)
			self.password = self.verify_info_user('Senha', password)

	def _limit(self):
		while not self.limit:
			limit = input(GREEN + 'Limite: ' + DEFAULT)
			try:
				limit = int(limit)
				if limit <= 0:
					self.logger.error('Limite deve ser maior que zero')
				else:
					self.limit = limit
			except:
				self.logger.error('Limite invalido')
	
	def validate_date_days(self, days):
		try:
			days = int(days)
			if days <= 0:
				self.logger.error('Valor deve ser maior que zero')
			else:
				dt = datetime.now()
				td = timedelta(days=days)
				return (td + dt).strftime('%d/%m/%Y')
		except:
			self.logger.error('Valor invalido')
			return False

	def _date(self):
		while not self.date:
			days = input(GREEN + 'Dias: ' + DEFAULT)
			self.date = self.validate_date_days(days)

	def show(self):
		print('-' * 50)
		print(f'{GREEN}Conta SSH Criada!{DEFAULT}')
		print('-' * 50)
		print(f'{YELLOW}Usuario: {DEFAULT}' + self.username)
		print(f'{YELLOW}Senha: {DEFAULT}' + self.password)
		print(f'{YELLOW}Limite: {DEFAULT}%02d' % self.limit)
		print(f'{YELLOW}Expira: {DEFAULT}' + self.date)
		print(f'-' * 50)
		input()
	
	def _shell(self):
		date = self.date.split('/')
		date.reverse()
		cmd = 'useradd --no-create-home \
			--no-user-group \
			--shell /bin/false \
			--password $(echo %s | openssl passwd -1 -stdin) \
			--expiredate %s %s' % (self.password, '-'.join(date), self.username)
		os.system(cmd)
	
	def save_info(self):
		base = SQLite()
		base.append_info(self.create_user_id(), self.username,
		self.password, self.limit, self.date, '00:00:00')
		base.close()

	def get_input_user_info(self):
		self._username()
		self._password()
		self._limit()
		self._date()
		self._shell()
		self.save_info()

def create_user():
	print(create_bar('CRIAR USUARIO'))
	create = CreateUser()
	create.get_input_user_info()
	create.show()