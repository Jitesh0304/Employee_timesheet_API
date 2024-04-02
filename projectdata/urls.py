from django.urls import path
from .views import ProjectDetailsView, ProjectCreateUpdateView, ManagerRetrieveProjectUser, ProjectNameView, \
                ManagerRetrieveAllProjects


urlpatterns = [
    path('createproject/', ProjectCreateUpdateView.as_view(), name='createproject'),
    path('updateproject/<str:pname>/', ProjectCreateUpdateView.as_view(), name='updateproject'),
    path('managerprojects/', ManagerRetrieveAllProjects.as_view(), name='managerprojects'),

    path('getproject/<str:pname>/', ProjectDetailsView.as_view(), name='getproject'),
    path('getproject/', ProjectDetailsView.as_view(), name='getoneproject'),
    path('getprojectname/', ProjectNameView.as_view(), name='getprojectname'),
    path('allprojectusers/', ManagerRetrieveProjectUser.as_view(), name='allprojectUser'),
    path('projectuser/<str:pname>/', ManagerRetrieveProjectUser.as_view(), name='projectUser'),
]
