from django.urls import path
from .views import TimesheetCreateUpdateView,WeeklyReportView, ManagerRetrieveTimesheetView, \
            EmployeeRetriveDataWeekly, EmployeeRetriveDataApproveNotApprove, ManagerApproveTimesheetView, \
            AdminApproveTimesheetView, ManagerModifyEmpTimesheetView
               ##  WeekReportManagerUpdateView,




urlpatterns = [
    path('timesheetdata/', TimesheetCreateUpdateView.as_view(), name='data'),
    path('updatedata/<str:pk>/', TimesheetCreateUpdateView.as_view(), name='updatedata'),
    path('retriveallweeksdata/', EmployeeRetriveDataWeekly.as_view(), name='retriveparticularweekdata'),
    path('retriveparticularweekdata/<str:wknum>/', EmployeeRetriveDataWeekly.as_view(), name='timesheetweekly'),
    path('submitnotsubmitdata/', EmployeeRetriveDataApproveNotApprove.as_view(), name='submitnotsubmit'),
    path('managergetdata/<int:prID>/', ManagerRetrieveTimesheetView.as_view(), name='managergetdata'),
    path('managergetdataweek/<int:prID>/<str:empid>/<str:yr_wk>/', ManagerRetrieveTimesheetView.as_view(), name='managergetdataweek'),
    path('weekreport/', WeeklyReportView.as_view(), name='weekreport'),

    path('managerapprove/', ManagerApproveTimesheetView.as_view(), name='managerapprove'),
    path('adminapprove/', AdminApproveTimesheetView.as_view(), name='adminapprove'),
    # path('adminretrive/<str:emp>/', AdminApproveTimesheetView.as_view(), name='adminretrive'),
    # path('adminretriveyear/<str:emp>/<int:year>/', AdminApproveTimesheetView.as_view(), name='adminretriveyear'),
    path('adminretrive/<str:empid>/', AdminApproveTimesheetView.as_view(), name='adminretrive'),
    path('adminretriveweek/<str:empid>/<str:yr_wk>/', AdminApproveTimesheetView.as_view(), name='adminretriveweek'),
    path('managerupdatetimesheet/', ManagerModifyEmpTimesheetView.as_view(), name='managerupdatetimesheet')
]

