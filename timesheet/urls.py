from django.urls import path
from .views import TimesheetCreateUpdateView,WeeklyReportView, ManagerRetrieveTimesheetView, \
            EmployeeRetriveDataWeekly, EmployeeRetriveDataApproveNotApprove, ManagerApproveTimesheetView, \
            AdminApproveTimesheetView
               ##  WeekReportManagerUpdateView,




urlpatterns = [
    path('timesheetdata/', TimesheetCreateUpdateView.as_view(), name='data'),
    path('updatedata/<str:pk>/', TimesheetCreateUpdateView.as_view(), name='updatedata'),
    path('retriveallweeksdata/', EmployeeRetriveDataWeekly.as_view(), name='retriveparticularweekdata'),
    path('retriveparticularweekdata/<int:wknum>/', EmployeeRetriveDataWeekly.as_view(), name='timesheetweekly'),
    path('submitnotsubmitdata/', EmployeeRetriveDataApproveNotApprove.as_view(), name='submitnotsubmit'),
    path('managergetdata/', ManagerRetrieveTimesheetView.as_view(), name='managergetdata'),
    path('weekreport/', WeeklyReportView.as_view(), name='weekreport'),
    path('weekreport/<int:pk>/', WeeklyReportView.as_view(), name='weekreport'),
    # path('weekreportupdate/<int:pk>/', WeekReportManagerUpdateView.as_view(), name='weekreportupdate'),
    path('managerapprove/', ManagerApproveTimesheetView.as_view(), name='managerapprove'),
    path('adminapprove/', AdminApproveTimesheetView.as_view(), name='adminapprove'),
    path('adminretrive/<str:emp>/', AdminApproveTimesheetView.as_view(), name='adminapprove'),
]

