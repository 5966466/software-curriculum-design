import numpy as np
import pickle, os

class DataSho():
	def __init__(self, pro):
		self.pro = pro

	def load(self, name):
		with open(os.path.join(self.pro.path, name+'.pkl'), 'rb') as f:
			return pickle.load(f)

	def show_items(self):
		return 'labelled_img', 'interfered_img', 'state'

	def show_appro(self):
		chart = {'type': 'bar'}
		title = {'text': 'Picture classification'}
		img_dict = self.load('Img')
		xAxis = {'categories': list(img_dict.keys())}
		yAxis = {'title': {'text': 'log10(Numbers)'}, 'type': 'logarithmic'}
		right = []
		wrong = []
		for i in img_dict.keys():
			a = img_dict[i][:, 1]
			right.append(np.sum(a == 'Right'))
			wrong.append(np.sum(a == 'Wrong'))
		series = {"Right": right, "Wrong": wrong}

		return chart, title, xAxis, yAxis, series

	def show_det(self, img_name):
		img = self.load('Img')[img_name]
		interfered_img = list(img[:, 0])
		state = list(img[:, 1])
		return ["interfered_img", "state"], interfered_img, state

	def show_all(self):
		img_dict = self.load('Img')
		labelled_img = []
		interfered_img = []
		state = []
		for i in img_dict.keys():
			cont = img_dict[i]
			interfered_img.extend(list(cont[:, 0]))
			state.extend(list(cont[:, 1]))
			for j in cont[:, 0]:
				labelled_img.append(i)

		namelist = ["labelled_img", "interfered_img", "state"]
		return namelist, labelled_img, interfered_img, state

