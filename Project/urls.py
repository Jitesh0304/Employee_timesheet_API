from django.contrib import admin
from django.urls import path,include
from account import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.homepage, name='homepage'),
    path('user/', include('account.urls')),
    path('project/', include('projectdata.urls')),
    path('timesheet/', include('timesheet.urls')),
]
