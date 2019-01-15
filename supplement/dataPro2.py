import sqlite3
import os, shutil
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

	def acc_Img(self):
		dm = "SELECT DISTINCT(labelled_img) FROM %s" % self.pre.tableName
		data = self.execute_set(dm)
		img_dict = {i[0]:[] for i in data}
		for i in img_dict.keys():
			dm = "SELECT interfered_img, state FROM %s WHERE labelled_img = '%s'"\
				% (self.pre.tableName, i)
			data = self.execute_set(dm)
			img_dict[i] = np.array(data)

		self.save(img_dict, 'Img')

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
			self.acc_Img()
		except Exception as e:
			self.add_msg(str(e))
			print(str(e))




