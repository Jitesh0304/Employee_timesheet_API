from django.urls import path
from .views import ProjectRetrieveView, ProjectCreateUpdateView, ManagerRetrieveProjectUser


urlpatterns = [
    path('createproject/', ProjectCreateUpdateView.as_view(), name='createproject'),
    path('updateproject/<str:pname>/', ProjectCreateUpdateView.as_view(), name='updateproject'),
    path('getproject/<str:pname>/', ProjectRetrieveView.as_view(), name='getproject'),
    path('allprusers/', ManagerRetrieveProjectUser.as_view(), name='allprojectUser'),
    path('projectuser/<str:pname>/', ManagerRetrieveProjectUser.as_view(), name='projectUser'),
]
