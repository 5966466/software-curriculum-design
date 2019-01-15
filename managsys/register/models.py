from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Acc(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	path = models.CharField(max_length=200)
	img = models.ImageField(upload_to='register/static/img', \
		default="register/static/img/default.png")

	def __str__(self):
		return "User: %s" % (self.user)

class IPaddr(models.Model):
	name = models.ForeignKey(Acc, on_delete=models.CASCADE)
	ipAddr = models.CharField(max_length=15)
	userName = models.CharField(max_length=50)
	userPasswd = models.CharField(max_length=50)
	port = models.IntegerField(default=21)
	serverPath = models.CharField(max_length=200)

	def __str__(self):
		return self.ipAddr

class FilesAcc(models.Model):
	acc_name = models.ForeignKey(Acc, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	date = models.DateTimeField()
