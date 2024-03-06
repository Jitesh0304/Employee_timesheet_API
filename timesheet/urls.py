from django.urls import path
from .views import TimesheetCreateUpdateView,WeeklyReportView, ManagerRetrieveTimesheetView, WeekReportManagerUpdateView



urlpatterns = [
    path('data/', TimesheetCreateUpdateView.as_view(), name='data'),
    path('updatedata/<str:pk>/', TimesheetCreateUpdateView.as_view(), name='updatedata'),
    path('managergetdata/', ManagerRetrieveTimesheetView.as_view(), name='managergetdata'),
    path('weekreport/', WeeklyReportView.as_view(), name='weekreport'),
    path('weekreport/<int:pk>/', WeeklyReportView.as_view(), name='weekreport'),
    path('weekreportupdate/<int:pk>/', WeekReportManagerUpdateView.as_view(), name='weekreportupdate'),
]
