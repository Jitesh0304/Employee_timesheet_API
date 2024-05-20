from django.urls import path
from .views import LeaveAppicationView, DepartmentTrackerView




urlpatterns = [
    path('leaveapplication/', LeaveAppicationView.as_view(), name='leaveapply'),
    path('leaveapplication/<int:pk>/', LeaveAppicationView.as_view(), name='leaveapply'),
    path('deptracker/<int:pk>/', DepartmentTrackerView.as_view(), name='deptracker'),
    path('deptracker/', DepartmentTrackerView.as_view(), name='deptracker'),
]
