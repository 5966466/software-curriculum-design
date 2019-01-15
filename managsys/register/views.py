from django.shortcuts import render, redirect
from .models import Acc, IPaddr, FilesAcc
from data.funcs import get_file, check_dir
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import os

from .funcs import *

def welcome(request):
	return render(request, 'registers/welcome.html')

def before_login(request):
	if request.user.is_authenticated:
		return redirect(reverse('register:detail', args=(request.user.acc.id,)))
	return render(request, 'registers/welcome.html')

def after_login(request):
	username = request.POST['in_name']
	password = request.POST['in_passwd']

	username = username.strip()
	password = password.strip()
	user = authenticate(request, username=username, password=password)
	if user is not None:
		account = user.acc
		url = 'img/' + os.path.basename(account.img.url)
		login(request, user)
		files = check_dir(account)
		content = {
			'account': account, 
			'url': url, 
			'message': "Successfully logged in", 
			'files': files, 
		}
		return render(request, 'registers/homepage.html', content)
	else:
		if len(User.objects.filter(username=username)) == 0:
			return render(request, 'registers/welcome.html', \
				{'error_message': "Account doesn't exit"})
		else:
			return render(request, 'registers/welcome.html', \
				{'error_message': "Password doesn't match"})

	"""
	st, account = sentence_name(name_id)
	if st:
		return render(request, 'registers/login.html', \
			{'error_message': "Account doesn't exit"})

	elif account.account_passwd == passwd:
		content = {
			'account': account, 
			'message': "Successfully logged in"
		}
		return render(request, 'registers/message.html', content)

	else:
		return render(request, 'registers/login.html', \
			{'error_message': "Password doesn't match"})
	"""

def signup(request):
	return render(request, 'registers/signup.html')

def after_signup(request):
	username = request.POST['in_name']
	password = request.POST['in_passwd']
	repasswd = request.POST['re_passwd']

	username = username.strip()
	password = password.strip()
	repasswd = repasswd.strip()

	u = User.objects.filter(username=username)
	if len(u) != 0:
		return render(request, 'registers/signup.html', \
			{'error_message': "The account has already been registered"})
	elif len(username) <= 0 or len(username) > 16 or username.isdigit():
		return render(request, 'registers/signup.html', \
			{'error_message': "The format of name was illegal"})

	if len(password) < 6 or len(password) > 20:
		return render(request, 'registers/signup.html', \
			{'error_message': "The format of password was illegal"})
	elif password != repasswd:
		return render(request, 'registers/signup.html', \
			{'error_message': "The reinput of the password in wrong"})

	ids = generate_id()
	path = make_dir(ids)

	user = User.objects.create_user(username=username, password=password)
	user.save()

	account = Acc(id=ids, user=user, path=path)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	account.save()
	user = authenticate(request, username=username, password=password)
	login(request, user)

	content = {
		'account': account, 
		'files':files,
		'url': url, 
		'message': "Successfully signed up", 
	}
	return render(request, 'registers/homepage.html', content)
	"""
	st, p = sentence_name(name)
	if not st:
		return render(request, 'registers/signup.html', \
			{'error_message': "The account has already been registered"})

	elif len(name) <= 0 or len(name) > 16 or name.isdigit(): 
		return render(request, 'registers/signup.html', \
			{'error_message': "The format of name was illegal"})

	if len(passwd) < 6 or len(passwd) > 20:
		return render(request, 'registers/signup.html', \
			{'error_message': "The format of password was illegal"})
	elif passwd != repass:
		return render(request, 'registers/signup.html', \
			{'error_message': "The reinput of the password in wrong"})

	ids = generate_id()
	path = make_dir(ids)

	account = Acc(
		id=ids, 
		account_name=name, 
		account_passwd = passwd, 
		path = path
	)
	account.save()

	content = {
		'account': account, 
		'message': "Successfully signed up", 
	}
	return render(request, 'registers/message.html', content)
	"""

def logout_view(request):
	logout(request)
	return render(request, 'registers/welcome.html')

@login_required
def detail(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	url = 'img/' + os.path.basename(account.img.url)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	content = {
		'account': account, 
		'url': url, 
		'files':files,
	}
	return render(request, 'registers/homepage.html', content)

@login_required
def before_download(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	content = {
		'id': account_id, 
		'c_id': choice_id, 
	}
	return render(request, 'registers/download_choice.html', content)
	
@login_required
def loading_download(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	ip_choice = IPaddr.objects.get(pk=choice_id)


	content = {
		'account': account, 
		'c_id': choice_id, 
	}
	return render(request, 'registers/download_loading.html', content)

@login_required
def download(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	ip_choice = IPaddr.objects.get(pk=choice_id)

	#selection = request.POST.get('choice')
	#if selection is None:
	#	content = {
	#		'id': account_id, 
	#		'c_id': choice_id, 
	#		'error_message': "Please select"
	#	}
	#	return render(request, 'registers/download_choice.html', content)

	method = Account(account)
	
	url = 'img/' + os.path.basename(account.img.url)
	#if selection == 'ftp':
	#	st, msg = method.fetch_file_ftp(ip_choice)
	#elif selection == 'sftp':
	#	st, msg = method.fetch_file_sftp(ip_choice)
	st, msg = method.fetch_file_sftp(ip_choice)
	files = check_dir(account)
	if st:
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Successfully downloaded", 
		}
		return render(request, 'registers/homepage.html', content)

	else:
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': 'Failed! ' + msg, 
		}
		return render(request, 'registers/homepage.html', content)
		
#@login_required
def loading_multi(request, account_id):
#	if request.user.acc.id != account_id:
#		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	
	choice_list = request.POST.getlist('list')
	if choice_list == []:
		content = {
			'account': account, 
			'files': files,
			'url': url,
			'error_message': "Please select files to download simultaneously"
		}
		return render(request, 'registers/homepage.html', content)

	d_type = request.POST.get('choice')
	if d_type is None:
		content = {
			'account': account, 
			'files': files,
			'url': url,
			'error_message': "Please select a download type"
		}
		return render(request, 'registers/homepage.html', content)

	content = {
		'account': account, 
		'choice_list': choice_list, 
		'd_type': d_type, 
	}
	return render(request, 'registers/multi_loading.html', content)

@login_required
def download_multi(request, account_id, d_type):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	choice_list = request.POST.getlist('list')
	if choice_list == []:
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Please select files to download simultaneously"
		}
		return render(request, 'registers/homepage.html', content)
	#d_type = request.POST.get('choice')
	'''
	if d_type is None:
		content = {
			'account': account, 
			'error_message': "Please select a download type"
		}
		return render(request, 'registers/detail.html', content)
	'''
	method = Account(account)
	st, msg = method.fetch_multifile(choice_list, d_type)
	files = check_dir(account)
	if not st:
		content = {
				'account': account, 
				'files': files,
				'url': url, 
				'error_message': "Couldn't download: " + msg, 
			}
		return render(request, 'registers/homepage.html', content)


	content = {
		'account': account, 
		'files': files,
		'url': url, 
		'error_message': "Successfully downloaded"
	}
	return render(request, 'registers/homepage.html', content)

@login_required
def before_revise(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	ip_choice = IPaddr.objects.get(pk=choice_id)

	content = {
		'account': account, 
		'choice': ip_choice, 
	}
	return render(request, 'registers/revise_choice.html', content)

@login_required
def revise(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	ip_choice = IPaddr.objects.get(pk=choice_id)

	values = request.POST.getlist('value')
	choices = ['ipAddr', 'port', 'userName', 'userPasswd', 'serverPath']

	method = Account(account)
	for choice, value in zip(choices, values):
		if getattr(ip_choice, choice) == value:
			continue

		st, msg = method.modify_item(ip_choice, choice, value)

		if not st:
			content = {
				'account': account, 
				'choice': ip_choice, 
				'error_message': msg, 
			}
			return render(request, 'registers/revise_choice.html', content)
		else:
			continue

	content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Successfully revised", 
		}
	return render(request, 'registers/homepage.html', content)

@login_required
def delete(request, account_id, choice_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	ip_choice = IPaddr.objects.get(pk=choice_id)

	method = Account(account)
	method.delete_item(ip_choice)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)

	content = {
		'account': account, 
		'files': files,
		'url': url, 
		'error_message': "Successfully deleted", 
	}
	return render(request, 'registers/homepage.html', content)

#@login_required
def delete_multi(request, account_id):
#	if request.user.acc.id != account_id:
#		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	choice_list = request.POST.getlist('list')
	if choice_list == []:
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Please select files to delete"
		}
		return render(request, 'registers/homepage.html', content)

	method = Account(account)
	st, msg = method.delete_multifile(choice_list)
	if not st:
		content = {
				'account': account, 
				'files': files,
				'url': url, 
				'error_message': "Couldn't delete: " + msg, 
			}
		return render(request, 'registers/homepage.html', content)

	content = {
		'account': account, 
		'files': files,
		'url': url, 
		'error_message': "Successfully deleted"
	}
	return render(request, 'registers/homepage.html', content)

@login_required
def multi_process(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
	
	choose = request.POST.get('post')
	#if choose == 'Download All':
	#	return download_multi(request, account_id)
	if choose == 'Delete All':
		return delete_multi(request, account_id)
	elif choose == 'Revise':
		choice_id = request.POST.getlist('list')
		print(choice_id)
		if choice_id is None:
			account = Acc.objects.get(pk=account_id)
			files = check_dir(account)
			url = 'img/' + os.path.basename(account.img.url)
			content = {
				'account': account, 
				'files': files,
				'url': url, 
				'error_message': "Please select a file revise"
			}
			return render(request, 'registers/homepage.html', content)
		elif len(choice_id) != 1:
			account = Acc.objects.get(pk=account_id)
			files = check_dir(account)
			url = 'img/' + os.path.basename(account.img.url)
			content = {
				'account': account, 
				'files': files,
				'url': url, 
				'error_message': "Please select only one file revise"
			}
			return render(request, 'registers/homepage.html', content)
		else:
			return before_revise(request, account_id, choice_id[0])
	else:
		return loading_multi(request, account_id)
		

@login_required
def before_add(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	return render(request, 'registers/add.html', {'id': account_id})

@login_required
def add(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
		
	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	method = Account(account)
	st, msg = method.add_server(
			IPv4=request.POST['IPv4'], 
			user=request.POST['user'], 
			passwd=request.POST['passwd'], 
			port=request.POST['port'], 
			path=request.POST['path'], 
		)

	if st:
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Successfully added", 
		}
		return render(request, 'registers/homepage.html', content)
	else:
		content = {
			'id': account_id, 
			'error_message': msg, 
		}
		return render(request, 'registers/add.html', content)

@login_required
def before_addfile(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	return render(request, 'registers/before_addfile.html', {'id': account_id})

@login_required
def add_file(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
		
	account = Acc.objects.get(pk=account_id)
	files = check_dir(account)
	url = 'img/' + os.path.basename(account.img.url)
	method = Account(account)
	file = request.FILES.get('data')
	if file is None:
		content = {
			'id': account_id, 
			'error_message': "Please select a file to upload"
		}
		return render(request, 'registers/add.html', content)

	path = os.path.join(account.path, file.name)
	st, msg = get_file(file, path)
	if not st:
		content = {
			'id': account_id, 
			'error_message': msg
		}
		return render(request, 'registers/add.html', content)

	st, msg = method.add_multiserver(path)
	if not st:
		content = {
			'id': account_id, 
			'error_message': msg
		}
		return render(request, 'registers/add.html', content)

	os.remove(path)

	content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Successfully added", 
		}
	return render(request, 'registers/homepage.html', content)

@login_required
def revise_account(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))

	account = Acc.objects.get(pk=account_id)
	content = {'account': account}
	return render(request, 'registers/revise_account.html', content)

@login_required
def after_revise(request, account_id):
	if request.user.acc.id != account_id:
		return redirect('%s?next=%s' % (settings.LOGIN_URL, request.path))
	
	account = Acc.objects.get(pk=account_id)
	
	files = check_dir(account)

	username = request.POST['in_name']
	oldpasswd = request.POST['old_passwd']
	password = request.POST['in_passwd']
	repasswd = request.POST['re_passwd']
	
	user = request.user

	username = username.strip()
	oldpasswd = oldpasswd.strip()
	password = password.strip()
	repasswd = repasswd.strip()

	if len(username) <= 0 or len(username) > 16 or username.isdigit():
		content = {
			'account': account, 
			'error_message': "The format of name was illegal"
		}
		return render(request, 'registers/revise_account.html', content)
	user.username = username
	user.save()

	img = request.FILES.get('img')
	if img is not None:
		account.img = img
		account.save()
	url = 'img/' + os.path.basename(account.img.url)

	if password == '' and repasswd == '':
		content = {
			'account': account, 
			'files': files,
			'url': url, 
			'error_message': "Successfully revised username", 
		}
		return render(request, 'registers/homepage.html', content)

	if not user.check_password(oldpasswd):
		content = {
			'account': account, 
			'error_message': "The input of old password was wrong"
		}
		return render(request, 'registers/revise_account.html', content)
	
	if len(password) < 6 or len(password) > 20:
		content = {
			'account': account, 
			'error_message': "The format of new password was illegal"
		}
		return render(request, 'registers/revise_account.html', content)
	elif password != repasswd:
		content = {
			'account': account, 
			'error_message': "The reinput of the password in wrong"
		}
		return render(request, 'registers/revise_account.html', content)

	user.set_password(password)
	user.save()

	content = {
		'account': account,
		'files': files, 
		'url': url, 
		'error_message': "Successfully revised profile", 
	}
	return render(request, 'registers/homepage.html', content)


