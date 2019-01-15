import numpy as np
import pickle, os

class DataSho():
	def __init__(self, pro):
		self.pro = pro

	def load(self, name):
		with open(os.path.join(self.pro.path, name+'.pkl'), 'rb') as f:
			return pickle.load(f)

	def show_items(self):
		return 'Dates', 'Timing', 'user', 'IP', 'state'

	def show_appro(self):
		chart = {'type': 'column'}
		title = {'text': 'Analyzed log'}
		date_dict = self.load('Dates')
		xAxis = {'categories': list(date_dict.keys())}
		yAxis = {'title': {'text': 'log10(Numbers)'}, 'type': 'logarithmic'}
		success = []
		failure = []
		log = True
		for i in date_dict.keys():
			a = date_dict[i][:, 3]
			#success.append(np.log10(np.sum(a == 'Success')+1))
			#failure.append(np.log10(np.sum(a == 'Failure')+1))
			success.append(np.sum(a == 'Success'))
			failure.append(np.sum(a == 'Failure'))
		series = {"Success": success, "Failure": failure}
		#return series

		return chart, title, xAxis, yAxis, series

	#def show_det(self, return_value):
	#	return self.show_date(return_value)

	def show_det(self, dates):
		dating = self.load('Dates')[dates]
		users = list(set(dating[:, 1]))
		user_ips = []
		for u in users:
			rows = (dating[:, 1] == u)
			ips = list(set(dating[rows, 2]))
			user_ips.extend([(u, ip) for ip in ips])
		success = []
		failure = []
		for user_ip in user_ips:
			rows = (dating[:, 1] == user_ip[0])
			a = dating[rows, :]
			rows = (a[:, 2] == user_ip[1])
			a = a[rows, :]
			success.append(np.sum(a=='Success'))
			failure.append(np.sum(a=='Failure'))

		user_ips = np.array(user_ips)
		users = list(user_ips[:, 0])
		ips = list(user_ips[:, 1])

		return ["user", "ip", "Success", "Failure"], users, ips, success, failure

	def show_all(self):
		user_ips = self.load('user')
		users = []
		ips = []
		datings = []
		success = []
		failure = []
		for user_ip, mat in user_ips.items():
			dating = list(set(mat[:, 0]))
			for d in dating:
				users.append(user_ip[0])
				ips.append(user_ip[1])
				datings.append(d)
				rows = (mat[:, 0] == d)
				a = mat[rows, 2]
				success.append(np.sum(a=='Success'))
				failure.append(np.sum(a=='failure'))

		namelist = ["user", "ip", "Date", "Success", "Failure"]
		return namelist, users, ips, datings, success, failure




