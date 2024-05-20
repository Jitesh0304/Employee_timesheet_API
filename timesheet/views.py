from rest_framework.response import Response
from rest_framework import status as httpstatus
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from account.models import Employee
from projectdata.models import Project
from .serializers import TimesheetSerializer, TimesheetRetrieveSerializer, ManagerUpdateEmpTimesheetSerializer
from .models import Timesheet, Status
from django.db.models import Q, F, Count
# from datetime import datetime, timedelta
from .utils import get_week_nums_and_days_till_today, get_all_days_of_the_week, get_current_and_previous_week_days,\
     check_date_format, get_year_and_week_number
from django.db import transaction  ## IntegrityError
# from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear
from account.custom_auth import AdminPermission,ManagerPermission
from collections import defaultdict





class TimesheetCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            current_year, current_week_number, _ = timezone.now().isocalendar()
            two_weeks_days = get_current_and_previous_week_days(current_year, current_week_number)
            filter_q = Q(employee=user)
            if current_week_number >= 2:
                all_data = {}
                ###   OR operation for all weeks
                date_q = Q()
                for week, days in two_weeks_days.items():
                    date_q |= Q(date__range=[days[0], days[-1]])
                week_data = Timesheet.objects.filter(filter_q & date_q)

                for week, days in two_weeks_days.items():
                    week_data_for_week = week_data.filter(date__range=[days[0], days[-1]])
                    if week_data_for_week.exists():
                        serializer = TimesheetRetrieveSerializer(week_data_for_week, many=True)
                        all_data[f"{current_year}_{week}"] = serializer.data
                return Response({'msg':all_data}, status= httpstatus.HTTP_200_OK)
            else:
                # print(two_weeks_days)
                week_data = Timesheet.objects.filter(filter_q & Q(date__range= [two_weeks_days[0], two_weeks_days[-1]]))
                serializer = TimesheetRetrieveSerializer(week_data, many=True)
                all_data = {f"{current_year}_{current_week_number}":serializer.data}
                return Response({'msg':all_data}, status= httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)



    def post(self, request, format=None):
        user = request.user
        try:
            serializer = TimesheetSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                status_dt = Status.objects.get(id=1)
                serializer.save(status=status_dt)
                return Response({'msg':'Timesheet data saved....'}, status= httpstatus.HTTP_201_CREATED)
            return Response(serializer.errors, status= httpstatus.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk, format=None):
        user = request.user
        try:
            # timesheet_data = Timesheet.objects.filter(id=pk, employee=user).exclude(status__statusName='Submit').first()
            timesheet_data = Timesheet.objects.filter(id=pk, employee=user, status__id=1).first()
            if timesheet_data:
                serializer = TimesheetSerializer(timesheet_data, data= request.data, context={'request':request}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'msg':'Timesheet data update ....'}, status= httpstatus.HTTP_200_OK)
                return Response(serializer.errors, status= httpstatus.HTTP_400_BAD_REQUEST)
            return Response({'msg':'Data does not exist or data is pushed to manager verification'}, 
                            status=httpstatus.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)







class EmployeeRetriveDataWeekly(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, wknum=None, format=None):
        user = request.user
        # try:
        #     current_year, current_week_number, _ = timezone.now().isocalendar()
        #     all_data = {}
        #     if wknum:
        #         week_days = get_all_days_of_the_week(current_year, wknum)
        #         week_data = Timesheet.objects.filter(employee=user, 
        #                                              date__range=[week_days[0], week_days[-1]])
        #         serializer = TimesheetRetrieveSerializer(week_data, many=True)
        #         all_data[f"{current_year}_{wknum}"] = serializer.data
        #     else:
        #         weeks_till_today = get_week_nums_and_days_till_today(current_year, current_week_number)
        #         filter_q = Q(employee=user) ## , submit=False, approve=False
        #         ###   OR operation for all weeks
        #         date_q = Q()
        #         for week, days in weeks_till_today.items():
        #             date_q |= Q(date__range=[days[0], days[-1]])

        #         week_data = Timesheet.objects.filter(filter_q & date_q)

        #         for week, days in weeks_till_today.items():
        #             week_data_for_week = week_data.filter(date__range=[days[0], days[-1]])
        #             if week_data_for_week.exists():
        #                 serializer = TimesheetRetrieveSerializer(week_data_for_week, many=True)
        #                 all_data[f"{current_year}_{week}"] = serializer.data
        #     return Response({'msg': all_data}, status=httpstatus.HTTP_200_OK)
        # except Exception as e:
        #     return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)


        try:
            if wknum:
                week_data = Timesheet.objects.filter(employee=user, year_week= wknum)
                serializer = TimesheetRetrieveSerializer(week_data, many=True)
                return Response({'msg': serializer.data}, status=httpstatus.HTTP_200_OK)
            else:
                week_data = list(set(Timesheet.objects.filter(employee=user).values_list('year_week', flat=True).distinct()))
                return Response({'msg': week_data}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)





class EmployeeRetriveDataApproveNotApprove(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            # current_year, current_week_number, _ = timezone.now().isocalendar()
            # weeks_till_today = get_week_nums_and_days_till_today(current_year, current_week_number)
            # date_ranges = [(days[0], days[-1]) for week, days in weeks_till_today.items()]
            # timesheet_data = Timesheet.objects.filter(
            #     employee=user, date__range=(date_ranges[0][0], date_ranges[-1][1])
            # )
            # serializer = TimesheetRetrieveSerializer(timesheet_data, many=True)
            # all_data = defaultdict(lambda: defaultdict(list))
            # for timesheet in serializer.data:
            #     week_number = timesheet['year_week']
            #     status_name = timesheet['status']['statusName']
            #     all_data[status_name][week_number].append(timesheet)
            # return Response({"msg": dict(all_data)}, status=httpstatus.HTTP_200_OK)



            # timesheet_data = set(
            #     Timesheet.objects
            #     .filter(employee=user)
            #     .values_list('status__statusName','year_week').distinct())
            # grouped_data = {}
            # for statusname, week_name in timesheet_data:
            #     if statusname not in grouped_data:
            #         grouped_data[statusname] = []
            #     grouped_data[statusname].append(week_name)
            # print(timesheet_data)



            timesheet_data = (
                Timesheet.objects
                .filter(employee=user)
                .select_related('status')  ### Status objects are fetched in one query
                .values_list('status__statusName', 'year_week').distinct()  ### Select only required fields
                .order_by('status__statusName', 'year_week')  ### Optional: Order by status name and year_week
            )
            grouped_data = {}
            for status_name, year_week in timesheet_data:
                if status_name not in grouped_data:
                    grouped_data[status_name] = []
                grouped_data[status_name].append(year_week)

            return Response({"msg": grouped_data}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({"msg": str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)







class ManagerRetrieveTimesheetView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]


    def get(self, request, prID, yr_wk=None, empid=None, format=None):
        user = request.user
        try:
            # if not yr_wk:
            #     all_data = Timesheet.objects.filter(project__projectManager=user, status__id=2)
            #     ## <QuerySet [{'project_name': 'project2', 'employee': 'aspl3', 'week_number': 10, 'timesheet_count': 2}]>
            #     grouped_data = all_data.annotate(week_number=ExtractWeek('date'), year_name=ExtractYear('date')).values(
            #                                                 'week_number','project__projectName','employee', 'year_name'
            #                                                 ).annotate(timesheet_count=Count('id'))
            #     # print(grouped_data)
            #     final_data = {}
            #     for entry in grouped_data:
            #         year_name = entry['year_name']
            #         week_number = entry['week_number']
            #         project_name = entry['project__projectName']
            #         employee_id = entry['employee']

            #         if project_name not in final_data:
            #             final_data[project_name] = {}
            #         if employee_id not in final_data[project_name]:
            #             final_data[project_name][employee_id] = {}
            #         timesheet_group = all_data.filter(
            #             project__projectName=project_name,
            #             employee__empID=employee_id,
            #             date__week=entry['week_number'],
            #         )
            #         serializer = TimesheetRetrieveSerializer(timesheet_group, many=True)
            #         final_data[project_name][employee_id][str(year_name)+"_"+str(week_number)] = serializer.data
            #     return Response({'msg': final_data}, status=httpstatus.HTTP_200_OK)
            # else:
            #     all_data = Timesheet.objects.filter(project__projectManager=user, status__id=2, year_week= yr_wk)
            #     serializer = TimesheetRetrieveSerializer(all_data, many=True)
            #     return Response({'msg': {f'{yr_wk}':serializer.data}}, status=httpstatus.HTTP_200_OK)



            if not yr_wk and not empid:
                print('1')
                queryset = Timesheet.objects.filter(project__projectManager=user, project__projectID = prID, 
                                                    status__id=2).select_related('employee').values_list('employee__empID', 
                                                                        flat=True).distinct().order_by('employee__empID')
                
                return Response({f'{prID}': queryset}, status=httpstatus.HTTP_200_OK)
            else:
                print('2')
                queryset = Timesheet.objects.filter(project__projectManager=user, status__id=2, project__projectID = prID,
                                                    year_week= yr_wk, employee__empID= empid)
                serializer = TimesheetRetrieveSerializer(queryset, many=True)
                return Response({'msg': {f'{yr_wk}':serializer.data}}, status=httpstatus.HTTP_200_OK)

        except Exception as e:
            return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)





class WeeklyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        user = request.user
        try:
            required_fields = ['week_start_date', 'week_end_date']
            if not any(field in request.data for field in required_fields):
                return Response({'msg': f'{required_fields}- these fields are required'}, 
                                    status= httpstatus.HTTP_400_BAD_REQUEST)
            
            week_start_date = check_date_format(request.data.get('week_start_date'))
            week_end_date = check_date_format(request.data.get('week_end_date'))

            if not week_start_date or not week_end_date:
                return Response({'msg': f'Date format error.. Send date in (YYYY-MM-DD) this format'}, 
                                    status= httpstatus.HTTP_400_BAD_REQUEST)

            endDate = week_end_date.isocalendar()
            startDate = week_start_date.isocalendar()
            if startDate[1] != endDate[1]:
                total_weeks = [i for i in range(startDate[1], endDate[1]+1)]
                return Response({'msg':f'Send only one week data ... you are sending more then one week data {total_weeks}'}, 
                                status= httpstatus.HTTP_400_BAD_REQUEST)
            all_timesheet = Timesheet.objects.filter(employee=user, date__range=[week_start_date, week_end_date], 
                                                     status__id=1)
            if all_timesheet.exists():
                status_dt = Status.objects.get(id=2)
                total = all_timesheet.update(status=status_dt)
                message = f"Total {total} timesheet data submited successfully"
            else:
                total = 0
                message = f"Total {total} timesheet data submited successfully"
            return Response({'msg': message}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)




    # def get(self, request, pk=None, format=None):
    #     user = request.user
    #     try:
    #         if user.is_manager or user.is_admin:
    #             if pk:
    #                 timesheet_data = Timesheet.objects.filter(employee=user, date__week=pk)
    #                 timesheet_serializer = TimesheetRetrieveSerializer(timesheet_data, many=True)
    #                 return Response({'week_number': pk,'timesheet_data': timesheet_serializer.data}, status=status.HTTP_200_OK)
    #             else:
    #                 reports = WeeklyReport.objects.filter(submit_timesheet__project_name__projectManager=user,
    #                                                        submit_timesheet__submit=True, submit_timesheet__manager_approve=False)
    #                 # all_users_reports = reports.values_list('submit_timesheet__employee', 'id', 'submit_timesheet__id')
    #                 all_users_reports = reports.values_list('submit_timesheet__employee', 'id').distinct()
    #                 final_data = {}
    #                 # for employee_name, report_id, timesheet_id in all_users_reports:
    #                 for employee_name, report_id in all_users_reports:
    #                     if employee_name not in final_data:
    #                         # final_data[employee_name] = {'data':[]}
    #                         final_data[employee_name] = []
    #                     weekly_report = WeeklyReport.objects.get(id=report_id)
    #                     serializer = ManagerWeeklyReportRetrieveSerializer(weekly_report, context={'request':request})
    #                     timesheets = weekly_report.submit_timesheet.filter(project_name__projectManager=user).values_list('id', flat=True)
    #                     serializer_data = serializer.data
    #                     serializer_data['submit_timesheet'] = timesheets
    #                     # final_data[employee_name]['data'].append(serializer_data)
    #                     final_data[employee_name].append(serializer_data)
    #                 return Response({'msg': final_data}, status=status.HTTP_200_OK)
    #         return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
    #     except Exception as e:
    #         return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class ManagerModifyEmpTimesheetView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def patch(self, request, format=None):
        # user = request.user
        try:
            # timesheet_ids = request.data.get('ids', [])
            # if not timesheet_ids:
            #     return Response({"msg": "No timesheet IDs provided."}, status=httpstatus.HTTP_400_BAD_REQUEST)

            req_data = request.data
            if 'data' not in req_data:
                return Response({"msg": "Your request body format is not correct ..",
                                 "data_format": {"data": [{"id":"int", "bill":"boolean", "comment":"str"},]}}, status=httpstatus.HTTP_400_BAD_REQUEST)

            try:
                timesheet_data = req_data.get('data', '')
                all_ids = [timesheet_id['id'] for timesheet_id in timesheet_data]
            except Exception:
                return Response({"msg": "data format mismatch"}, status=httpstatus.HTTP_400_BAD_REQUEST)

            timesheets = Timesheet.objects.filter(id__in=all_ids, status__id=2)
            serializer = ManagerUpdateEmpTimesheetSerializer(timesheets, data=request.data['data'], many=True, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Timesheets updated successfully."}, status=httpstatus.HTTP_200_OK)
            
            return Response(serializer.errors, status=httpstatus.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"msg": str(e)}, status=httpstatus.HTTP_500_INTERNAL_SERVER_ERROR)


class ManagerApproveTimesheetView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def post(self, request,format=None):
        user = request.user
        try:
            
            required_data = ["week_start_date", "week_end_date", "employee_id", "approve"]
            missing_fields = [field for field in required_data if field not in request.data]

            if missing_fields:
                return Response({'msg': f'Required fields are missing : [{", ".join(missing_fields)}]'}, 
                                status=httpstatus.HTTP_400_BAD_REQUEST)
            week_start_date = check_date_format(request.data.get("week_start_date"))
            week_end_date = check_date_format(request.data.get("week_end_date"))

            if not week_start_date or not week_end_date:
                return Response({'msg': f'Date format should be => YYYY-MM-DD'}, status=httpstatus.HTTP_400_BAD_REQUEST)
            # employee_id = request.data.get('employee_id')
            # approve = request.data.get('approve')
            employee_id = request.data['employee_id']
            req_approve = request.data['approve']
            
            endDate = week_end_date.isocalendar()
            startDate = week_start_date.isocalendar()
            if startDate[1] != endDate[1]:
                total_weeks = [i for i in range(startDate[1], endDate[1]+1)]
                return Response({'msg':f'Send only one week data ... you are sending more then one week data {total_weeks}'}, 
                                status= httpstatus.HTTP_400_BAD_REQUEST)
            
            timesheet_data = Timesheet.objects.filter(project__projectManager=user,status__id=2, 
                                                        employee__empID=employee_id,
                                                        date__range=[week_start_date, week_end_date])
            # print(timesheet_data)

            if req_approve=="True":
                status_dt = Status.objects.get(id=3)
                total = timesheet_data.update(status=status_dt)
                # total = 0
                message = f"Total {total} timesheet data approved..."
            else:
                status_dt = Status.objects.get(id=1)
                total = timesheet_data.update(status=status_dt)
                # total =0
                message = f"Total {total} timesheet data rejected..."
            return Response({'msg': message}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)





# class AdminApproveTimesheetView(APIView):
#     permission_classes = [IsAuthenticated, AdminPermission]


#     def get(self, request, emp, year=None, format=None):
#         user = request.user
#         try:
#             try:
#                 employee_data = Employee.objects.get(empID=emp, organization=user.organization)
#             except Exception:
#                 return Response({'msg': f'No employee is present with this {emp} empID in your organization '}, 
#                                 status=httpstatus.HTTP_403_FORBIDDEN)
#             if not year:
#                 current_year, current_week_number, _ = timezone.now().isocalendar()
#                 all_data = Timesheet.objects.filter(employee= employee_data, status__id=3, date__year=current_year)
#             else:
#                 all_data = Timesheet.objects.filter(employee= employee_data, status__id=3, date__year=year)

#             ## <QuerySet [{'project_name': 'project2', 'employee': 'aspl3', 'month_number': 10, 'timesheet_count': 2}]>
#             grouped_data = all_data.annotate(month_number=ExtractMonth('date')).values('month_number').annotate(
#                                                                                 timesheet_count=Count('id'))
#             # print(grouped_data)
#             final_data = {}
#             for entry in grouped_data:
#                 month_number = entry['month_number']
#                 timesheets = all_data.filter(date__month=month_number)
#                 serializer = TimesheetRetrieveSerializer(timesheets, many=True)
#                 if emp not in final_data:
#                     final_data[emp] = {}
#                 # if month_number not in final_data:
#                 #     final_data[emp][month_number] = {}
#                 final_data[emp][f"{month_number}"] = serializer.data

#             return Response({'msg': final_data}, status=httpstatus.HTTP_200_OK)
#         except Exception as e:
#             return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)

class AdminApproveTimesheetView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def get(self, request, empid, yr_wk=None, format=None):
        user = request.user
        try:
            if not yr_wk:
                # timesheet_years = Timesheet.objects.annotate(week_num = ExtractWeek('date'),year_num = ExtractYear('date')
                #                                             ).values('week_num','year_num')
                timesheet_years_week = set(Timesheet.objects.filter(employee__empID=empid).annotate(week_num = ExtractWeek('date'),year_num = ExtractYear('date')
                                                            ).values_list('week_num','year_num').distinct())
                yearly_data = {}
                for week_num, year_num in timesheet_years_week:
                    if year_num not in yearly_data:
                        yearly_data[year_num] = []
                    yearly_data[year_num].append(f"{year_num}_{week_num}")
                return Response({'msg': yearly_data}, status=httpstatus.HTTP_200_OK)
            else:
                timesheet_data = Timesheet.objects.filter(employee__empID=empid, year_week= yr_wk)
                serializer = TimesheetRetrieveSerializer(timesheet_data, many=True)
                return Response({'msg': serializer.data}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)



    def post(self, request,format=None):
        user = request.user
        try:
            required_data = ["week_start_date", "week_end_date", "employee_id", "approve"]
            missing_fields = [field for field in required_data if field not in request.data]

            if missing_fields:
                return Response({'msg': f'Required fields are missing : [{", ".join(missing_fields)}]'}, 
                                status=httpstatus.HTTP_400_BAD_REQUEST)
            week_start_date = check_date_format(request.data.get("week_start_date"))
            week_end_date = check_date_format(request.data.get("week_end_date"))

            if not week_start_date or not week_end_date:
                return Response({'msg': f'Date format should be => YYYY-MM-DD'}, status=httpstatus.HTTP_400_BAD_REQUEST)
            # employee_id = request.data.get('employee_id')
            # approve = request.data.get('approve')
            employee_id = request.data['employee_id']
            req_approve = request.data['approve']
            
            startDate_month = week_start_date.strftime("%m")
            endDate_month = week_end_date.strftime("%m")
            if endDate_month != startDate_month:
                # total_weeks = [i for i in range(startDate_month, endDate_month+1)]
                return Response({'msg': 'Send only one month data ... you are sending more then one month data'}, 
                                status= httpstatus.HTTP_400_BAD_REQUEST)
            
            timesheet_data = Timesheet.objects.filter(status__id=3, employee__empID=employee_id,
                                                    date__range=[week_start_date, week_end_date])

            if req_approve=="True":
                status_dt = Status.objects.get(id=4)
                total = timesheet_data.update(status=status_dt)
                message = f"Total {total} timesheet data approved..."
            else:
                status_dt = Status.objects.get(id=2)
                total = timesheet_data.update(status=status_dt)
                message = f"Total {total} timesheet data rejected..."
            return Response({'msg': message}, status=httpstatus.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=httpstatus.HTTP_400_BAD_REQUEST)



