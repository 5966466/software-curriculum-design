from django.shortcuts import render, redirect
from .models import App, FilesApp
from register.models import Acc
from django.http import HttpResponse
import shutil, os
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils import timezone
#from data.funcs import get_file, check_dir
from .funcs import *
from django.http import FileResponse

# Create your views here.
@login_required
def detail(request, account_id, prestatus='default'):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	content = {
		'account': account, 
		'files': files,
		'url': url,
		'prestatus': prestatus,
	}
	return render(request, 'registers/homepage.html', content)

@login_required
def before_add(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
	
	prestatus = 'appspace'
	content = {
		'id': account_id,
		'prestatus': prestatus, 
	}
	return render(request, 'datas/add.html', content)

@login_required
def add(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)

	appName = request.POST['appName']
	st, msg_path = make_dir(account, appName)
	if not st:
		prestatus = 'appspace'
		content = {
			'id': account_id, 
			'prestatus': prestatus, 
			'error_message': msg_path
		}
		return render(request, 'datas/add.html', content)

	names = ['dataPre', 'dataPro', 'dataSho']
	files = request.FILES.getlist('data')
	st, msg = uploadFile(files, names, msg_path)
	if not st:
		prestatus = 'appspace'
		content = {
			'id': account_id, 
			'prestatus': prestatus, 
			'error_message': msg
		}
		return render(request, 'datas/add.html', content)

	otherFile = request.FILES.get('others')
	if otherFile is not None:
		st, msg = uploadZip(otherFile, msg_path)
		if not st:
			prestatus = 'appspace'
			content = {
				'id': account_id, 
				'prestatus': prestatus, 
				'error_message': msg
			}
			return render(request, 'datas/add.html', content)

	account.app_set.create(
		name=account, 
		appName=appName, 
		path=msg_path
		)
	prestatus = 'appspace'
	content = {
		'message': "Successfully added", 
		'account': account, 
		'prestatus': prestatus,
		'type': 1, 
	}
	return render(request, 'datas/message.html', content)

@login_required
def application(request, account_id, app_id, error_message):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	app = App.objects.get(pk=app_id)
	files = check_dir(account)
	dates = []
	for f in files:
		f = account.filesacc_set.get(name = f)
		dates.append(f.date)
	f_d = list(zip(files, dates))
	url = 'img/' + os.path.basename(account.img.url)

	if error_message == 'NULL':
		error_message = None

	content = {
		'id': account_id, 
		'error_message': error_message,
		'app': app, 
		'f_d': f_d, 
		'url': url,
	}
	return render(request, 'datas/application.html', content)

@login_required
def manage_file(request, account_id, prestatus):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	prestatus = 'filespace'
	content = {
		'account': account, 
		'files': files, 
		'url': url,
		'prestatus': prestatus,
	}
	return render(request, 'registers/homepage.html', content)

@login_required
def delete_file(request, account_id, filename):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	os.remove(os.path.join(account.path, 'downloadfiles', filename))
	delete_all(account, filename)

	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	prestatus = 'filespace'
	content = {
		'message': "Successfully deleted", 
		'account': account, 
		'files': files,
		'url': url,
		'prestatus': prestatus,
		'type': 1, 
	}
	
	return render(request, 'registers/homepage.html', content)

@login_required
def before_upLog(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	prestatus = 'filespace'
	content = {
		'account': account,
		'prestatus': prestatus,  
	}
	return render(request, 'datas/uplog.html', content)

@login_required
def upLog(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	file = request.FILES.get('data')
	if file is None:
		prestatus = 'filespace'
		content = {
			'account': account,
			'prestatus': prestatus,
			'error_message': "Please select a log file to upload"
		}
		return render(request, 'datas/uplog.html', content)

	filename = file.name
	st, msg = get_file(file, os.path.join(account.path, \
		'downloadfiles', filename))
	if not st:
		prestatus = 'filespace'
		content = {
			'account': account,
			'prestatus': prestatus,   
			'error_message': msg
		}
		return render(request, 'datas/uplog.html', content)

	file = account.filesacc_set.filter(name=filename)
	if list(file) == []:
		account.filesacc_set.create(
			name = filename, 
			date = timezone.now()
		)
	else:
		file[0].date = timezone.now()
		file[0].save()

	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	prestatus = 'filespace'
	content = {
		'message': "Successfully upLoaded", 
		'account': account,
		'files': files,
		'url': url, 
		'prestatus': prestatus,
		'type': 1, 
	}

	
	return render(request, 'registers/homepage.html', content)

@login_required
def delete(request, account_id, app_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	app = App.objects.get(pk=app_id)
	app.delete()
	shutil.rmtree(app.path)
	prestatus = 'appspace'
	content = {
		'message': "Successfully deleted", 
		'account': account, 
		'prestatus': prestatus,  
		'type': 1, 
	}
	return render(request, 'datas/message.html', content)

@login_required
def before_revise(request, account_id, app_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	app = App.objects.get(pk=app_id)
	prestatus = 'appspace'
	account = Acc.objects.get(pk=account_id)
	content = {
		'account': account,
		'id': account_id,
		'prestatus': prestatus,   
		'app': app, 
	}
	return render(request, 'datas/revise.html', content)

@login_required
def revise(request, account_id, app_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	app = App.objects.get(pk=app_id)

	names = ['dataPre', 'dataPro', 'dataSho']
	isModify = False
	for i in range(3):
		file = request.FILES.get('data%s' % (i+1))
		path = os.path.join(app.path, names[i] + '.py')

		if file is not None:
			isModify = True

		st, msg = modifyFile(file, path)
		if not st:
			prestatus = 'appspace'
			content = {
				'account': account,
				'id': account_id, 
				'app': app, 
				'prestatus': prestatus,  
				'error_message': msg, 
			}
			return render(request, 'datas/revise.html', content)
			
	otherFile = request.FILES.get('others')
	if otherFile is not None:
		st, msg = uploadZip(otherFile, app.path)
		if not st:
			prestatus = 'appspace'
			content = {
				'id': account_id, 
				'prestatus': prestatus, 
				'error_message': msg
			}
			return render(request, 'datas/add.html', content)

	new_name = request.POST['appName']
	if new_name == '':
		prestatus = 'appspace'
		content = {
			'account': account,
			'id': account_id, 
			'app': app, 
			'prestatus': prestatus,  
			'error_message': "Please input app Name", 
		}
		return render(request, 'datas/revise.html', content)
	st, msg = modify_dir(app, new_name)
	if not st:
		prestatus = 'appspace'
		content = {
			'account': account,
			'id': account_id, 
			'app': app, 
			'prestatus': prestatus,  
			'error_message': msg, 
		}
		return render(request, 'datas/revise.html', content)

	if isModify:
		for f in app.filesapp_set.all():
			f.isAnalysis = False
			f.save()
	prestatus = 'appspace'
	content = {
		'error_message': "Successfully revised", 
		'account': account,
		'prestatus': prestatus,   
		'app': app, 
		'type': 2, 
	}
	return render(request, 'datas/message.html', content)
	
@login_required
def show_loading(request, account_id, app_id, filename):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	#account = Acc.objects.get(pk=account_id)
	#app = App.objects.get(pk=app_id)
	content = {
		'id': account_id, 
		'a_id': app_id, 
		'f': filename, 
	}
	return render(request, 'datas/show_loading.html', content)

@login_required
def show_approx(request, account_id, app_id, filename):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	app = App.objects.get(pk=app_id)

	st, show = show_in_views(account, app, filename)
	if not st:
		content = {
			'error_message': show, 
			'account': account, 
			'app': app, 
			'type': 2,
		}
		return render(request, 'datas/message.html', content)
	para = show.show_appro()
	para = showPara(*para)

	content = {
		'para': para, 
		'account': account, 
		'id': app_id, 
		'f': filename, 
	}
	return render(request, 'datas/show_approx.html', content)

@login_required
def show_detail(request, account_id, app_id, filename, item):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	app = App.objects.get(pk=app_id)

	st, show = show_in_views(account, app, filename)
	if not st:
		content = {
			'error_message': show, 
			'account': account, 
			'app': app, 
			'type': 2,
		}
		return render(request, 'datas/message.html', content)

	if item == 'ALL':
		items, *values = show.show_all()
	else:
		items, *values = show.show_det(item)
	content = {
		'items': items, 
		'values': list(zip(*values)), 
		'account': account, 
		'item': item, 
		'app': app, 
		'f': filename, 
	}
	return render(request, 'datas/show_detail.html', content)

@login_required
def downloadLocal(request, account_id, filename):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	path = os.path.join(account.path, 'downloadfiles', filename)

	return FileResponse(open(path, 'rb'), as_attachment=True)
	


	
