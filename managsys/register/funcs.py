from .models import Acc, IPaddr
import random
import os
from ftplib import FTP
import paramiko
import threading
from django.utils import timezone

"""
def sentence_name(name_id):
	name_id = name_id.strip() 
	try:
		if name_id.isdigit():
			name_id = int(name_id)
			account = Acc.objects.get(id=name_id)

		else:
			account = Acc.objects.get(account_name=name_id)

	except Acc.DoesNotExist:
			return (True, None)

	else:
		#passwd = account.account_passwd
		return (False, account)
"""

def generate_id():
	while 1:
		ids = int(random.uniform(0.1, 1) * 1e10)
		try:
			account = Acc.objects.get(id=ids)
		except Acc.DoesNotExist:
			break
		else:
			continue
	return ids

def make_dir(ids):
	path = os.path.dirname(os.getcwd())
	path = os.path.join(path, str(ids))
	os.makedirs(path)
	path2 = os.path.join(path, 'downloadfiles')
	os.makedirs(path2)
	return path

class Account_thread(threading.Thread):
	def __init__(self, target, args=(), kwargs={}):
		super().__init__()
		self.target = target
		self.args = args
		self.kwargs = kwargs
		self.result = (True, None)

	def run(self):
		self.result = self.target(*self.args, **self.kwargs)

	def get_result(self):
		return self.result


class Account():
	def __init__(self, account):
		self.account = account

	def add_server(self, IPv4, user, passwd, path, port=21):
		st, msg = self.check_ip(IPv4)
		if not st:
			return (st, msg)

		st, msg = self.check_port(port)
		if not st:
			return (st, msg)

		if user == '' or passwd == '' or path == '':
			return (False, "Please input")

		try:
			self.account.ipaddr_set.create(
				name=self.account, 
				ipAddr=IPv4, 
				userName=user, 
				userPasswd=passwd, 
				port=port, 
				serverPath=path
			)
		except Exception as e:
			return (False, "Failed to add: " + str(e))

		return (True, None)

	def add_multiserver(self, textPath):
		with open(textPath, 'r') as file:
			first = file.readline().strip().split(' ')
			while '' in first:
				first.remove('')

			second = first.copy()
			items = ['IPv4', 'port', 'user', 'passwd', 'path']
			for i in items:
				if i not in second:
					print("hello")
					return (False, "Illegal text file format")
				second.remove(i)
			if second != []:
				print("hi")
				return (False, "Illegal text file format")

			threads = []
			for i in file.readlines():
				i = i.strip().split(' ')
				while '' in i:
					i.remove('')
				in_add = dict(zip(first, i))
				thread = Account_thread(target=self.add_server, kwargs=in_add)
				thread.daemon = True
				threads.append(thread)
				thread.start()

		for thread in threads:
			thread.join()
			st, msg = thread.get_result()
			if not st:
				return (False, msg)

		return (True, None)

	def change_fileState(self, ip_choice):
		filename = os.path.basename(ip_choice.serverPath)
		file = self.account.filesacc_set.filter(name=filename)
		if list(file) == []:
			self.account.filesacc_set.create(
				name = os.path.basename(ip_choice.serverPath), 
				date = timezone.now()
			)
		else:
			file[0].date = timezone.now()
			file[0].save()

	def fetch_file_ftp(self, ip_choice):
		ftp=FTP()

		try:
			ftp.connect(ip_choice.ipAddr, ip_choice.port)
			ftp.login(ip_choice.userName, ip_choice.userPasswd)
		except Exception as e:
			return (False, "Couldn't connect to the server: " + str(e))

		path_a = os.path.basename(ip_choice.serverPath)
		path_b = os.path.dirname(ip_choice.serverPath)

		try:
			ftp.cwd(path_b)
			fd = open(os.path.join(self.account.path, 'downloadfiles', path_a), \
				'wb')
			ftp.retrbinary('RETR '+ path_a, fd.write)
		except Exception as e:
			return (False, "Couldn't access to the file: " + str(e))

		fd.close()
		self.change_fileState(ip_choice)
		return (True, None)

	def fetch_file_sftp(self, ip_choice):
		try:
			sf = paramiko.Transport(ip_choice.ipAddr, ip_choice.port)
			sf.connect(username=ip_choice.userName, password=ip_choice.userPasswd)
			sftp = paramiko.SFTPClient.from_transport(sf)
		except Exception as e:
			return (False, "Couldn't connect to the server: " + str(e))

		path_a = os.path.basename(ip_choice.serverPath)

		try:
			sftp.get(ip_choice.serverPath.strip(), \
				os.path.join(self.account.path, 'downloadfiles', path_a))
		except Exception as e:
			return (False, "Couldn't access to the file: " + str(e))

		self.change_fileState(ip_choice)
		return (True, None)

	def fetch_multifile(self, choice_list, d_type):
		if d_type.lower() == 'ftp':
			func = self.fetch_file_ftp
		elif d_type.lower() == 'sftp':
			func = self.fetch_file_sftp
		else:
			return (False, "No type match")

		threads = []
		for choice_id in choice_list:
			ip_choice = IPaddr.objects.get(pk=choice_id)
			thread = Account_thread(target=func, args=(ip_choice,))
			thread.daemon = True
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()
			st, msg = thread.get_result()
			if not st:
				return (False, msg)

		return (True, None)


	def modify_item(self, ip_choice, item, value):
		if item == 'ipAddr':
			st, msg = self.check_ip(value)
			if not st:
				return (st, msg)
		elif item == 'port':
			st, msg = self.check_port(value)
			if not st:
				return (st, msg)

		command = "ip_choice.%s = '%s'" % (item, value)
		
		try:
			exec(command)	
			ip_choice.save()
		except Exception as e:
			return (False, "Failed to revise %s: %s" % (item, str(e)))

		return (True, None)

	def delete_item(self, ip_choice):
		ip_choice.delete()

	def delete_multifile(self, choice_list):
		threads = []
		for choice_id in choice_list:
			ip_choice = IPaddr.objects.get(pk=choice_id)
			thread = Account_thread(target=self.delete_item, args=(ip_choice,))
			thread.daemon = True
			threads.append(thread)
			thread.start()

		for thread in threads:
			thread.join()
			thread.get_result()

		return (True, None)


	def check_ip(self, IPv4):
		a = IPv4.split('.')
		if len(a) != 4:
			return (False, "Illegal IPv4 address")
		for i in a:
			if not i.isdigit():
				return (False, "Illegal IPv4 address")
			if int(i) > 255:
				return (False, "Illegal IPv4 address")
		return (True, None)

	def check_port(self, port):
		if type(port) == int:
			return (True, None)
		elif not port.isdigit():
			return (False, "Illegal Port")
		else:
			return (True, None)



