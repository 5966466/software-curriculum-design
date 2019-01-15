import sqlite3
import os
import numpy as np
import pickle

class DataPro():
	def __init__(self, pre):
		self.pre = pre
		self.path = os.path.join(pre.setpath, pre.setName)

		dm = "SELECT COUNT(*) FROM %s" % self.pre.tableName
		data = self.pre.execute_set(dm)
		if data[0][0] == 0:
			self.st_msg = (False, "There is no datum to analyze")
			os.remove(os.path.join(pre.setpath, pre.setName+'.db'))
			os.rmdir(self.path)
		else:
			self.st_msg = (True, None)

	def acc_Dates(self):
		dm = "SELECT DISTINCT(Dates) FROM %s" % self.pre.tableName
		data = self.execute_set(dm)
		date_dict = {i[0]:[] for i in data}
		for i in date_dict.keys():
			dm = "SELECT Timing, user, IP, state FROM %s WHERE Dates = '%s'" \
				% (self.pre.tableName, i)
			data = self.execute_set(dm)
			date_dict[i] = np.array(data)

		self.save(date_dict, 'Dates')

	def acc_user(self):
		dm = "SELECT DISTINCT user, IP FROM %s" % self.pre.tableName
		data = self.execute_set(dm)
		user_dict = {i:[] for i in data}
		for i in user_dict.keys():
			dm = "SELECT Dates, Timing, state FROM %s WHERE user = '%s' AND IP = '%s'" \
				% (self.pre.tableName, i[0], i[1])
			data = self.execute_set(dm)
			user_dict[i] = np.array(data)
		
		self.save(user_dict, 'user')

	def acc_state(self):
		state_dict = {'Success': 0, 'Failure': 0}
		dm = "SELECT COUNT(*) FROM %s WHERE state = 'Success'" % self.pre.tableName
		data = self.execute_set(dm)
		state_dict['Success'] = data[0][0]

		dm = "SELECT COUNT(*) FROM %s WHERE state = 'Failure'" % self.pre.tableName
		data = self.execute_set(dm)
		state_dict['Failure'] = data[0][0]

		self.save(state_dict, 'state')

	def execute_set(self, demand):
		self.pre.cursor.execute(demand)
		self.pre.connection.commit()
		data = self.pre.cursor.fetchall()
		return data

	def save(self, data, name):
		with open(os.path.join(self.path, name+'.pkl'), 'wb') as f:
			pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

	def add_msg(self, msg):
		if self.st_msg[0]:
			self.st_msg = (False, msg)

	def acc_all(self):
		try:
			self.acc_Dates()
			self.acc_user()
			self.acc_state()
		except Exception as e:
			self.add_msg(str(e))