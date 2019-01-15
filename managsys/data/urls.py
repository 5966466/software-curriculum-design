from django.urls import include, path
from . import views
from django.views.static import serve
from django.conf.urls import url

app_name = 'data'
urlpatterns = [
	path('<int:account_id>/<str:prestatus>/', views.detail, name='detail'), 
	path('<int:account_id>/before_add', views.before_add, name='before_add'), 
	path('<int:account_id>/add', views.add, name='add'), 
	path('<int:account_id>/<int:app_id>/<str:error_message>/application', views.application, name='application'), 
	path('<int:account_id>/<int:app_id>/delete', views.delete, name='delete'), 
	path('<int:account_id>/<int:app_id>/before_revise', \
		views.before_revise, name='before_revise'), 
	path('<int:account_id>/<int:app_id>/revise', views.revise, name='revise'), 
	path('<int:account_id>/<int:app_id>/<str:filename>/show_approx', \
		views.show_approx, name='show_approx'), 
	path('<int:account_id>/<int:app_id>/<str:filename>/show_loading', \
		views.show_loading, name='show_loading'), 
	path('<int:account_id>/<int:app_id>/<str:filename>/<str:item>', \
		views.show_detail, name='show_detail'), 
	path('<int:account_id>/<str:prestatus>/managfile', \
		views.manage_file, name='manage_file'), 
	path('<int:account_id>/<str:filename>/deletefile', \
		views.delete_file, name='delete_file'), 
	path('<int:account_id>/before_upLog', \
		views.before_upLog, name='before_upLog'), 
	path('<int:account_id>/upLog', views.upLog, name='upLog'), 
	path('<int:account_id>/<str:filename>/downloadfile', \
		views.downloadLocal, name='downloadLocal')
	#url(r'^static/img/(?P<path>.*)$', serve, {'document_root': 'register/static/img/'}), 
]