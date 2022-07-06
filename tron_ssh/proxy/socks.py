#!/usr/bin/env python3
import ssl
import socket
import select
import threading
import random
import logging
import os

logger = logging.getLogger(__name__)

class Connection:
	def __init__(self):
		self.ssl = False
		self.conn = None
		self.tls_in_buff = ssl.MemoryBIO()
		self.tls_out_buff = ssl.MemoryBIO()
		ctx = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
		ctx.load_cert_chain(certfile='cert.pem', keyfile='cert.pem')
		self.tls_obj = ctx.wrap_bio(self.tls_in_buff, self.tls_out_buff, server_side=True)

	def send(self, data):
		if self.ssl:
			self.tls_obj.write(data)
			self.conn.sendall(self.tls_out_buff.read())
		else:
			self.conn.sendall(data)

	def recv(self, bufsiz=8192):
		try:
			data = self.conn.recv(bufsiz)
			if not data: return None
			if self.ssl:
				self.tls_in_buff.write(data)
				return self.tls_obj.read()
			else:
				return data
		except:
			return None

	def do_tls_handshake(self, data):
		self.tls_in_buff.write(data)
		try:
			self.tls_obj.do_handshake()
		except ssl.SSLWantReadError:
			data = self.tls_out_buff.read()
			self.conn.send(data)
		self.tls_in_buff.write(self.conn.recv(8192))
		self.tls_obj.do_handshake()
		self.conn.send(self.tls_out_buff.read())

	def close(self):
		if self.conn: self.conn.close()


class Client(Connection):
	def __init__(self, client, addr):
		super(Client, self).__init__()
		self.conn = client
		self.addr = addr

class Server(Connection):
	def __init__(self, hostname, port):
		super(Server, self).__init__()
		self.hostname = hostname
		self.port = port

	def connect(self):
		addr = (self.hostname, self.port)
		self.conn = socket.create_connection(addr, 5)
		self.conn.settimeout(5)

class Proxy(threading.Thread):
	def __init__(self, client, ssh_port, vpn_port):
		super(Proxy, self).__init__()
		self.client = client
		self.hostname = socket.gethostbyname('')
		self.ssh_port = ssh_port
		self.vpn_port = vpn_port
		self.server = None

	def _process_rlist(self, rlist):
		if self.client.conn in rlist:
			data = self.client.recv()
			if not data: return True
			self.server.send(data)

		if self.server.conn in rlist:
			data = self.server.recv()
			if not data: return True
			self.client.send(data)

	def _process(self):
		while True:
			socks_list = select.select([self.client.conn, self.server.conn], [], [], 1)
			if self._process_rlist(socks_list[0]): break

	def request(self):
		data = self.client.recv(3)
		if not data:
			return
		if b'\x00' in data:
			logger.info('Cliente (OPENVPN): %s:%d' % self.client.addr)
			self.server = Server(self.hostname, self.vpn_port)
			self.server.connect()
		else:
			self.server = Server(self.hostname, self.ssh_port)
			self.server.connect()

		data += self.client.recv()
		if b'\x16\x03\x01' in data:
			logger.info('Cliente (SSL): %s:%d' % self.client.addr)
			self.client.ssl = True
			self.client.do_tls_handshake(data)
		elif b'SSH-' in data:
			logger.info('Cliente (DIRECT): %s:%d' % self.client.addr)
			self.server.send(data)
		else:
			logger.info('Cliente (SOCKS): %s:%d' % self.client.addr)

		self._process()

	def run(self):
		try:
			self.request()
		except Exception as e:
			print(e)
			pass
		finally:
			self.client.close()
			if self.server:
				self.server.close()
			logger.info('Cliente desconectado: %s:%d' % (self.client.addr))

class Socks(object):
	def __init__(self, hostname, port, ssh_port, vpn_port):
		self.hostname = hostname
		self.port = port
		self.ssh_port = ssh_port
		self.vpn_port = vpn_port
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	def handler(self, client):
		proxy = Proxy(client, self.ssh_port, self.vpn_port)
		proxy.daemon = True
		proxy.start()

	def run(self):
		try:
			logger.info('Servidor ativo: %s:%d' % (self.hostname, self.port))
			self.server.bind((self.hostname, self.port))
			self.server.listen(0)
			while True:
				conn, addr = self.server.accept()
				client = Client(conn, addr)
				self.handler(client)
				
		except Exception as e:
			logger.exception('%r' % e)
		finally:
			self.server.close()

def main():
	logging.basicConfig(
		level=logging.INFO,
		format='%(asctime)s - %(message)s',
		datefmt='%H:%M:%S'
	)
	try:
		proxy = Socks('0.0.0.0', 8080, 22, 443)
		proxy.run()
	except KeyboardInterrupt:
		pass

if __name__ == '__main__':
	main()