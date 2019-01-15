from django.urls import include, path
from . import views


app_name = 'register'
urlpatterns = [
	path('', views.welcome, name='welcome'), 
	path('login/', views.before_login, name='login'), 
	path('signup/', views.signup, name='signup'), 
	path('logout/', views.logout_view, name='logout'), 
	path('afterlogin/', views.after_login, name='after_login'), 
	path('aftersignup/', views.after_signup, name='after_signup'),
	path('<int:account_id>/', views.detail, name='detail'), 
	path('<int:account_id>/<int:choice_id>/before_download', \
		views.before_download, name='before_download'), 
	path('<int:account_id>/<int:choice_id>/download', \
		views.download, name='download'), 
	path('<int:account_id>/<int:choice_id>/loading_download', \
		views.loading_download, name='loading_download'), 
	path('<int:account_id>/<int:choice_id>/before_revise', \
		views.before_revise, name='before_revise'), 
	path('<int:account_id>/<int:choice_id>/revise', views.revise, name='revise'), 
	path('<int:account_id>/<int:choice_id>/delete', views.delete, name='delete'), 
	path('<int:account_id>/before_add', views.before_add, name='before_add'), 
	path('<int:account_id>/add', views.add, name='add'), 
	path('<int:account_id>/revise_account', \
		views.revise_account, name='revise_account'), 
	path('<int:account_id>/after_revise', \
		views.after_revise, name='after_revise'), 
	path('<int:account_id>/before_addfile', \
		views.before_addfile, name='before_addfile'), 
	path('<int:account_id>/add_file', views.add_file, name='add_file'), 
	path('<int:account_id>/multi_process', \
		views.multi_process, name ='multi_process'), 
	path('<int:account_id>/<str:d_type>/multi_download', \
		views.download_multi, name ='download_multi'), 
]