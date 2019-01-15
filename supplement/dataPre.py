import sqlite3
import os
import datetime
import threading, queue
import math
import time

class DataPre():
	def __init__(self, filepath, setpath):
		self.filepath = filepath
		self.setpath = setpath

		setName = os.path.basename(filepath)
		self.setName = setName.split('.')[0]
		
		self.tableName = 'DataPre'
		self.connection = sqlite3.connect(\
			os.path.join(self.setpath, self.setName+'.db'))
		#self.connection = pymysql.connect("localhost", "root", "jeskkyf5", "test")
		self.cursor = self.connection.cursor()
		path = os.path.join(self.setpath, self.setName)
		if not os.path.exists(path):
			os.mkdir(path)

		self.st_msg = (True, None)
		self.lock = threading.Lock()

	def add_msg(self, msg):
		if self.st_msg[0]:
			self.st_msg = (False, msg)


	def execute_set(self, demand):
		#connection = sqlite3.connect('%s/%s.db' % (self.setpath, self.setName))
		#cursor = connection.cursor()
		#cursor.execute(demand)
		#connection.commit()
		#connection.close()
		#data = cursor.fetchall()
		self.cursor.execute(demand)
		self.connection.commit()
		data = self.cursor.fetchall()
		return data

	def create_table(self):
		dm = '''CREATE TABLE %s
			(
		 	id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
		 	Dates date NULL ,
		 	Timing time NULL ,
		 	user varchar(50) NULL , 
		 	IP varchar(20) NULL , 
		 	state varchar(10) NULL
			);''' % self.tableName

		try:
			self.execute_set(dm)
		except Exception as e:
			self.add_msg(str(e))

	def insert_table(self, Dates, Timing, user, IP, state):
		dm = '''INSERT INTO %s(Dates, Timing, user, IP, state) 
				VALUES('%s', '%s', '%s', '%s', '%s');''' \
			% (self.tableName, Dates, Timing, user, IP, state)

		try:
			self.execute_set(dm)
		except Exception as e:
			self.add_msg(str(e))

	def insert_table_all(self, tups):
		for tup in tups:
			dm = '''INSERT INTO %s(Dates, Timing, user, IP, state) 
				VALUES('%s', '%s', '%s', '%s', '%s');''' \
			% (self.tableName, tup[0], tup[1], tup[2], tup[3], tup[4])
			try:
				self.cursor.execute(dm)
			except Exception as e:
				self.add_msg(str(e))
		try:
			self.connection.commit()
		except Exception as e:
			self.add_msg(str(e))

	def insert_table_queue(self, tup_queue):
		while True:
			tup = tup_queue.get()
			dm = '''INSERT INTO %s(Dates, Timing, user, IP, state) 
				VALUES('%s', '%s', '%s', '%s', '%s');''' \
			% (self.tableName, tup[0], tup[1], tup[2], tup[3], tup[4])
			self.cursor.execute(dm)
			tup_queue.task_done()


	def insert_lines(self, lines):
		for line in lines:
			tup = self.check_line(line)
			if tup is None:
				continue
			self.insert_table(*tup)

	def estab_table2(self):
		print(time.ctime())
		line_queue = queue.Queue()
		tups = []
		i = 0
		for n in range(10):
			check_thread = threading.Thread(target=self.check_line_queue, args=(line_queue, tups,))
			check_thread.setDaemon(True)
			check_thread.start()

		with open(self.filepath, 'rt') as f:
			for line in f:
				line_queue.put(line)
				#tup = self.check_line(line)
				#if tup is None:
				#	continue
				#else:
				#	tups.append(tup)

		line_queue.join()
		print(time.ctime())
		self.insert_table_all(tups)
		#self.connection.commit()
		print(time.ctime())

	def estab_table(self):
		self.create_table()
		tups = []
		with open(self.filepath, 'rt') as f:
			i = 0
			for line in f:
				tup = self.check_line(line)
				if tup is None:
					continue
				else:
					tups.append(tup)
		self.insert_table_all(tups)


	def get_time(self, ls):
		time = [str(datetime.datetime.now().year)]
		time.extend(ls)
		time = ' '.join(time)
		time = datetime.datetime.strptime(time,'%Y %b %d %H:%M:%S')
		time = datetime.datetime.strftime(time,'%Y-%m-%d %H:%M:%S')
		return time.split(' ')

	def get_checks(self, line):
		checks = line.split(' ')
		if '' in checks:
			checks.remove('')
		Dates, Timing = self.get_time(checks[0:3])
		i = checks.index('from')
		IP = checks[i+1]
		user = checks[i-1]
		while '"' in user or "'" in user or '[' in user or ']' in user:
			user = 'BAD NAME'
		return Dates, Timing, IP, user

	def check_line(self, line):
		if 'Accepted password' in line:
			state = 'Success'
			Dates, Timing, IP, user = self.get_checks(line)
			return Dates, Timing, user, IP, state

		elif 'Failed password' in line:
			state = 'Failure'
			Dates, Timing, IP, user = self.get_checks(line)
			return Dates, Timing, user, IP, state

		else:
			return None

	def check_line_queue(self, line_queue, tups):
		while True:
			line = line_queue.get()
			tup = self.check_line(line)
			if tup is not None:
				self.lock.acquire()
				tups.append(tup)
				self.lock.release()
			line_queue.task_done()

	def show(self):
		#dm = "PRAGMA table_info(%s)" % (self.tableName)
		dm = "SELECT * FROM %s WHERE id = 10" % (self.tableName)
		#dm = "SELECT DISTINCT(Dates) FROM %s" % self.tableName
		#dm = "SELECT Timing, user, IP, state FROM %s WHERE Dates = '%s'" % (self.tableName, '2018-09-29')
		#dm = "SELECT DISTINCT(user) FROM %s" % self.tableName
		#dm = "SELECT * FROM %s WHERE Timing between datetime('2018-09-29', 'start of day', '1 second') and datetime('2018-09-29', 'start of day', '1 day', '-1 second') AND state='Failure'" % (self.tableName)
		data = self.execute_set(dm)
		for i in data:
			print(i)
