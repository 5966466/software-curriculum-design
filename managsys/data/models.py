from django.db import models
from register.models import Acc

# Create your models here.
class App(models.Model):
	name = models.ForeignKey(Acc, on_delete=models.CASCADE)
	appName = models.CharField(max_length=30)
	path = models.CharField(max_length=200)

	def __str__(self):
		return self.appName

class FilesApp(models.Model):
	app_name = models.ForeignKey(App, on_delete=models.CASCADE)
	name = models.CharField(max_length=50)
	date = models.DateTimeField()
	isAnalysis = models.BooleanField(default=False)