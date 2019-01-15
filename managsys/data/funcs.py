from .models import App
import random
import os
import shutil
from ftplib import FTP
import paramiko
import sys
import threading
import zipfile
import importlib

def check_dir(account):
	#path = os.path.join(account.path, 'downloadfiles')
	#files = os.listdir(path)
	#files_copy = files.copy()
	#for f in files:
	#	filt = account.filesacc_set.filter(name=f)
	#	if list(filt) == []:
	#		files.remove(f)
	files = []
	filesacc = account.filesacc_set.all()
	for f in filesacc:
		files.append(f.name)

	return files

def make_dir(account, app_name):
	if app_name == '':
		return (False, "Please enter App Name")
	path = os.path.join(account.path, app_name)
	if os.path.exists(path):
		return (False, "The application exists.")
	os.makedirs(path)
	return (True, path)

def get_file(file, path):
	try: 
		with open(path, 'wb+') as destination:
			for chunk in file.chunks(): 
				destination.write(chunk)
	except Exception as e:
		return (False, "Can't upload file: %s" % str(e))

	return (True, None)

def check_python(filename):
	if '.' in filename:
		a = filename.split('.')[-1]
		if a != 'py':
			return (False, "Not a python file")
	else:
		return (False, "Not a python file")
	return (True, None)

def check_zip(filename):
	if '.' in filename:
		a = filename.split('.')[-1]
		if a != 'zip':
			return (False, "Not a zip file")
	else:
		return (False, "Not a zip file")
	return (True, None)

def uploadFile(files, names, msg_path):
	if len(files) != 3:
		os.removedirs(msg_path)
		return (False, "Some files didn't uploaded")

	for n, f in zip(names, files[0:3]):
		st, msg = check_python(f.name)
		if not st:
			os.removedirs(msg_path)
			return (False, msg)

		path = os.path.join(msg_path, '%s.py' % n)

		st, msg = get_file(f, path)
		if not st:
			shutil.rmtree(msg_path)
			return (False, msg)

	return (True, None)

def uploadZip(file, msg_path):
	st, msg = check_zip(file.name)
	if not st:
		shutil.rmtree(msg_path)
		return (False, msg)

	path = os.path.join(msg_path, 'others.zip')

	st, msg = get_file(file, path)
	if not st:
		shutil.rmtree(msg_path)
		return (False, msg)

	try:
		unzip(path, msg_path)
	except Exception as e:
		shutil.rmtree(msg_path)
		return (False, "Can't extract the file: " + str(e))

	return (True, None)

def unzip(file, path):
	z = zipfile.ZipFile(file, 'r')
	z.extractall(path=path)
	z.close()

def modifyFile(file, path):
	if file is not None:
		st, msg = check_python(file.name)
		if not st:
			return (False, msg)

		st, msg = get_file(file, path)
		if not st:
			return (False, msg)

	return (True, None)

def modify_dir(app, name):
	if app.appName != name:
		path_new = os.path.dirname(app.path)
		path_new = os.path.join(path_new, name)
		try:
			os.rename(app.path, path_new)
			app.path = path_new
			app.appName = name
			app.save()
		except Exception as e:
			return (False, str(e))

	return (True, None)

class showPara():
	def __init__(self, chart, title, xAxis, yAxis, series):
		self.chart_type = chart['type']
		self.title_text = title['text']
		self.xAxis_categories = xAxis['categories']
		self.yAxis_type = yAxis['type']
		self.yAxis_title_text = yAxis['title']['text']
		series_name = list(series.keys())
		series_data = []
		for i in series_name:
			series_data.append(series[i])
		self.series = zip(series_name, series_data)

def copyfile(path):
	for f in os.listdir(os.path.join(os.getcwd())):
		if 'tmp' in f:
			shutil.rmtree(f)
	tmp_name = 'tmp' + str(int(random.uniform(0.1, 1) * 1e5))
	os.makedirs(os.path.join(os.getcwd(), tmp_name))
	sys.path.append(os.path.join(os.getcwd(), tmp_name))
	f = open(os.path.join(tmp_name, '__init__.py'), 'wb')
	f.close()
	shutil.copy(os.path.join(path, 'dataPre.py'), \
		os.path.join(tmp_name, 'dataPre.py'))
	shutil.copy(os.path.join(path, 'dataPro.py'), \
		os.path.join(tmp_name, 'dataPro.py'))
	shutil.copy(os.path.join(path, 'dataSho.py'), \
		os.path.join(tmp_name, 'dataSho.py'))
	if 'others.zip' in os.listdir(path):
		unzip(os.path.join(path, 'others.zip'), tmp_name)

	return tmp_name

def deletefile(tmp_name):
	sys.path.remove(os.path.join(os.getcwd(), tmp_name))
	#shutil.rmtree(tmp_name)

def show_in_views(account, app, filename):
	tmp_name = copyfile(app.path)
	#from dataPro import DataPro
	#from dataPre import DataPre
	#from dataSho import DataSho
	dataPre = importlib.import_module('%s.dataPre' % tmp_name)
	dataPro = importlib.import_module('%s.dataPro' % tmp_name)
	dataSho = importlib.import_module('%s.dataSho' % tmp_name)
	DataPre = dataPre.DataPre
	DataPro = dataPro.DataPro
	DataSho = dataSho.DataSho

	file = app.filesapp_set.filter(name=filename)
	fileInAccount = account.filesacc_set.get(name=filename)
	if list(file) == []:
		app.filesapp_set.create(
			name = filename, 
			date = fileInAccount.date
		)
	elif file[0].date != fileInAccount.date:
		file[0].isAnalysis = False
		print("hello")
		file[0].date = fileInAccount.date
		file[0].save()

	f = filename.split('.')[0]

	file = app.filesapp_set.filter(name=filename)
	if file[0].isAnalysis:
		try:
			pre = DataPre(os.path.join(account.path, 'downloadfiles', filename), \
				app.path)
			pro = DataPro(pre)
			sho = DataSho(pro)
		except Exception as e:
			return (False, str(e))
		#sys.path.remove(app.path)
		deletefile(tmp_name)
		return (True, sho)
	else:
		if f in os.listdir(app.path):
			shutil.rmtree(os.path.join(app.path, f))
			os.remove(os.path.join(app.path, f+'.db'))
		pre = DataPre(os.path.join(account.path, 'downloadfiles', filename), \
			app.path)
		if not pre.st_msg[0]:
			return (False, pre.st_msg[1])
		try:
			st, sho = establish_new(account, file[0], pre, tmp_name)
		except Exception as e:
			return (False, str(e))
		#sys.path.remove(app.path)
		deletefile(tmp_name)
		return (st, sho)

def establish_new(account, file, pre, tmp_name):
	#from dataPro import DataPro
	#from dataPre import DataPre
	#from dataSho import DataSho
	dataPre = importlib.import_module('%s.dataPre' % tmp_name)
	dataPro = importlib.import_module('%s.dataPro' % tmp_name)
	dataSho = importlib.import_module('%s.dataSho' % tmp_name)
	DataPre = dataPre.DataPre
	DataPro = dataPro.DataPro
	DataSho = dataSho.DataSho
	pre.estab_table()
	if not pre.st_msg[0]:
		return (False, pre.st_msg[1])
	pro = DataPro(pre)
	if not pro.st_msg[0]:
		return (False, pro.st_msg[1])
	pro.acc_all()
	if not pro.st_msg[0]:
		return (False, pro.st_msg[1])

	file.isAnalysis = True
	file.save()

	return (True, DataSho(pro))

def delete_all(account, filename):
	file = account.filesacc_set.get(name=filename)
	file.delete()
	for app in account.app_set.all():
		for file in app.filesapp_set.filter(name=filename):
			file.delete()
	path = account.path
	files = os.listdir(path)
	files.remove('downloadfiles')
	filename = filename.split('.')[0]
	if '.DS_Store' in files:
		files.remove('.DS_Store')
	for file in files:
		if filename in os.listdir(os.path.join(path, file)):
			if os.path.exists(os.path.join(path, file, filename)):
				shutil.rmtree(os.path.join(path, file, filename))
			if os.path.exists(os.path.join(path, file, filename+'.db')):
				os.remove(os.path.join(path, file, filename+'.db'))
