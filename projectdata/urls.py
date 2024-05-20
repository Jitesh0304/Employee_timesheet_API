from django.urls import path
from .views import ProjectCreateUpdateView, ManagerRetrieveProjectUser, ProjectNameView, \
                ManagerRetrieveAllProjects, ProjectSubcodeView, ProjectSubcodeActivityView, ProjectDetailAPIView, \
                ProjectSubcodeRetrieveView, ProjectSubcodeActivityRetrieveView


urlpatterns = [
    path('createproject/', ProjectCreateUpdateView.as_view(), name='createproject'),
    path('updateproject/<str:prID>/', ProjectCreateUpdateView.as_view(), name='updateproject'),
    path('managerprojects/', ManagerRetrieveAllProjects.as_view(), name='managerprojects'),

    # path('getproject/<int:pk>/', ProjectDetailsView.as_view(), name='getproject'),
    # path('getproject/', ProjectDetailsView.as_view(), name='getoneproject'),
    path('getprojectname/', ProjectNameView.as_view(), name='getprojectname'),
    path('projectusers/<int:pk>/', ManagerRetrieveProjectUser.as_view(), name='projectUser'),
    path('getsubcode/<int:proj>/', ProjectSubcodeRetrieveView.as_view(), name='projectsubcode'),
    path('storesubcode/', ProjectSubcodeView.as_view(), name='projectsubcode'),
    path('updatesubcode/<int:pk>/', ProjectSubcodeView.as_view(), name='projectsubcode_update'),
    path('getsubcodeactivity/<int:psubID>/', ProjectSubcodeActivityRetrieveView.as_view(), name='subcodeactivity'),
    path('subcodeactivity/', ProjectSubcodeActivityView.as_view(), name='subcodeactivity'),
    path('updateactivity/<int:pk>/', ProjectSubcodeActivityView.as_view(), name='updateactivity'),


        ## this url will display project details and foreignkey details
    path('detail/<int:id>/', ProjectDetailAPIView.as_view(), name='detail'), 
    path('detail/', ProjectDetailAPIView.as_view(), name='detail'),
]
