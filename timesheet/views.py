from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
# from account.models import Employee
from projectdata.models import Project
from .serializers import TimesheetSerializer, TimesheetRetrieveSerializer, WeeklyReportSerializer, \
    ManagerWeeklyReportRetrieveSerializer
from .models import Timesheet, WeeklyReport
from django.db.models import Q, F, Count
from datetime import datetime, timedelta
from .utils import get_number_of_days_btw_dates #get_days_between_dates
from django.db import IntegrityError, transaction
from rest_framework.pagination import PageNumberPagination



class TimesheetCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            # today = timezone.datetime.now().date()
            # fifteen_days_ago = today - timedelta(days=15)
            # all_data = Timesheet.objects.filter(organization= user.organization, employee= user).exclude(date__lte = fifteen_days_ago)
            # all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
            #                                     date__range=[fifteen_days_ago, today], submit=False, approve=False)
            all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
                                                submit=False, approve=False)
            serializer = TimesheetRetrieveSerializer(all_data, many=True)
            return Response({'msg':serializer.data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


    def post(self, request, format=None):
        user = request.user
        try:
            serializer = TimesheetSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                # project = serializer.validated_data['project_name']
                serializer.save(organization= user.organization)
                return Response({'msg':'Timesheet data saved....'}, status= status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk, format=None):
        user = request.user
        try:
            # if user.is_manager or user.is_employee:
            timesheet_data = Timesheet.objects.filter(Q(organization= user.organization, id=pk, employee=user) |
                                                        Q(organization= user.organization, id=pk, 
                                                        project_name__projectManager=user)).exclude(submit=True).first()
            if timesheet_data:
                serializer = TimesheetSerializer(timesheet_data, data= request.data, context={'request':request}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'msg':'Timesheet data update ....'}, status= status.HTTP_200_OK)
                return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
            return Response({'msg':'Data does not exist or data is pushed to manager verification'}, 
                            status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




class ManagerRetrieveTimesheetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            if user.is_manager:
                all_data = Timesheet.objects.filter(organization=user.organization, project_name__projectManager=user,
                                                    submit=True, approve=False)
                grouped_data = all_data.values('project_name', 'employee').annotate(timesheet_count=Count('id'))
                
                final_data = {}
                for entry in grouped_data:
                    project_name = entry['project_name']
                    employee_id = entry['employee']
                    timesheets = all_data.filter(project_name=project_name, employee=employee_id)
                    serializer = TimesheetRetrieveSerializer(timesheets, many=True)
                    
                    ## append all data to final dict
                    if project_name not in final_data:
                        final_data[project_name] = {}
                    final_data[project_name][employee_id] = serializer.data

                return Response({'msg': final_data}, status=status.HTTP_200_OK)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



        ## with pagination
# class ManagerRetrieveTimesheetView(APIView):
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination

#     def get(self, request, format=None):
#         user = request.user
#         try:
#             if user.is_manager:
#                 today = timezone.datetime.now().date()
#                 fifteen_days_ago = today - timedelta(days=15)
#                 all_data = Timesheet.objects.filter(organization=user.organization, project_name__projectManager=user,
#                                                      date__range=[fifteen_days_ago, today], submit=True, approve=False)

#                 grouped_data = all_data.values('employee').annotate(timesheet_count=Count('id'))

#                 final_data = {}
#                 paginator = self.pagination_class()
#                 paginator.page_size = 1

#                 for entry in grouped_data:
#                     employee_id = entry['employee']
#                     timesheets = all_data.filter(employee=employee_id)

#                     result_page = paginator.paginate_queryset(timesheets, request)

#                     serializer = TimesheetRetrieveSerializer(result_page, many=True)
#                     final_data[employee_id] = serializer.data

#                 return paginator.get_paginated_response(final_data)
#             return Response({'msg': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
#         except Exception as e:
#             return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class WeeklyReportView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, format=None):
        user = request.user
        try:
            serializer = WeeklyReportSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                week_start_date = serializer.validated_data['week_start_date']
                week_end_date = serializer.validated_data['week_end_date']

                if WeeklyReport.objects.filter(employee= user, week_start_date__range=[week_start_date, week_end_date]).exists():
                    return Response({'msg':f'You have already send this week data'}, status= status.HTTP_400_BAD_REQUEST)
                
                endDate = week_end_date.isocalendar()
                startDate = week_start_date.isocalendar()
                if startDate[1] != endDate[1]:
                    total_weeks = [i for i in range(startDate[1], endDate[1]+1)]
                    return Response({'msg':f'Send only one week data ... you are sending more then one week data {total_weeks}'}, 
                                    status= status.HTTP_400_BAD_REQUEST)
                    # try:
                    #     all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
                    #                             date__range=[week_start_date, week_end_date], submit=False)
                    #     for oneData in all_data:
                    #         oneData.submit = True
                    #         oneData.save()
                    #     sid = transaction.savepoint()
                    # except IntegrityError:
                    #     transaction.savepoint_rollback(sid)
                    # transaction.savepoint_commit(sid)
                all_timesheet = Timesheet.objects.filter(organization=user.organization,
                                                        employee=user, date__range=[week_start_date, week_end_date],
                                                        submit=False)
                if all_timesheet.exists():

                    # ####################################
                    # all_project = all_timesheet.values_list('project_name', flat=True).distinct()

                    # reports_list = []
                    # for project in all_project:
                    #     project_timesheet = all_timesheet.filter(project_name=project)
                    #     print(list(project_timesheet))
                    #     onereport = WeeklyReport.objects.create(
                    #         employee= user, week_start_date= week_start_date, week_end_date=week_end_date,
                    #         submit=True, approve=False, submit_date= timezone.now()
                    #     )
                    #     onereport.submit_timesheet.set(project_timesheet)
                    # updated_count = all_timesheet.update(submit=True)
                    # #####################################


                    serializer.save(submit_date= timezone.now(), submit_timesheet= all_timesheet, approve_data=[],
                                    reject_data = [])
                    updated_count = all_timesheet.update(submit=True)
                    # serializer.save(submit_date= timezone.now(), submit_timesheet= [data for data in all_timesheet])
                    return Response({'msg':f'Weekly report added and {updated_count} timesheet data updated ...'},
                            status= status.HTTP_200_OK)
                return Response({'msg':'You do not have any data between these days'}, status= status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




    def get(self, request, pk=None, format=None):
        user = request.user
        try:
            if user.is_manager or user.is_admin:
                if pk:
                        # report = WeeklyReport.objects.get(id= pk, submit=True, approve=False)
                    report = WeeklyReport.objects.filter(id= pk, submit_timesheet__submit=True,
                                                          submit_timesheet__approve=False).first()
                    if report:
                        # filtered_report = report.filter(submit_timesheet__project_name__projectManager=user).values_list(
                        #                                             'submit_timesheet__id')
                        filtered_report = report.submit_timesheet.filter(project_name__projectManager=user,submit=True, approve=False)
                        all_ids_list = filtered_report.values_list('id', flat=True)
                        weekly_report_serializer = ManagerWeeklyReportRetrieveSerializer(report)
                        new_weekly_report_serializer = weekly_report_serializer.data
                        new_weekly_report_serializer['submit_timesheet'] = all_ids_list
                        timesheet_serializer = TimesheetRetrieveSerializer(filtered_report, many=True)
                        return Response({'weeklyreport': new_weekly_report_serializer,
                                        'timesheet_data': timesheet_serializer.data}, status=status.HTTP_200_OK)
                    return Response({'msg': f'Weekreport does not exist with -{pk}- ID '}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # reports = WeeklyReport.objects.filter(submit_timesheet__project_name__projectManager=user, submit=True,
                    #                                     approve=False)
                    reports = WeeklyReport.objects.filter(submit_timesheet__project_name__projectManager=user,
                                                           submit_timesheet__submit=True,submit_timesheet__approve=False)
                    # all_users_reports = reports.values_list('submit_timesheet__employee', 'id', 'submit_timesheet__id')
                    all_users_reports = reports.values_list('submit_timesheet__employee', 'id').distinct()
                    final_data = {}
                    # for employee_name, report_id, timesheet_id in all_users_reports:
                    for employee_name, report_id in all_users_reports:
                        if employee_name not in final_data:
                            # final_data[employee_name] = {'data':[]}
                            final_data[employee_name] = []
                        weekly_report = WeeklyReport.objects.get(id=report_id)
                        serializer = ManagerWeeklyReportRetrieveSerializer(weekly_report, context={'request':request})
                        timesheets = weekly_report.submit_timesheet.filter(project_name__projectManager=user).values_list('id', flat=True)
                        serializer_data = serializer.data
                        serializer_data['submit_timesheet'] = timesheets
                        # final_data[employee_name]['data'].append(serializer_data)
                        final_data[employee_name].append(serializer_data)
                    return Response({'msg': final_data}, status=status.HTTP_200_OK)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class WeekReportManagerUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk, format=None):
        user = request.user
        try:
            if user.is_manager:
                onereport = WeeklyReport.objects.filter(id= pk, submit_timesheet__submit=True,
                                                        submit_timesheet__approve=False).first()
                if onereport:
                    serializer = ManagerWeeklyReportRetrieveSerializer(onereport, data=request.data, partial=True,
                                                                       context={'request':request})
                    if serializer.is_valid():
                        approve = serializer.validated_data['approve']
                        all_filtered_timesheet = onereport.submit_timesheet.filter(project_name__projectManager=user,submit=True,
                                                                            approve=False)
                        if approve:
                            if any([onereport.approve_data == [], onereport.approve_data == "", onereport.approve_data == None]):
                                approved_data = []
                            else:
                                approved_data = onereport.approve_data

                            new_approved_data = {'manager': user.empID,
                                                 'approve': list(all_filtered_timesheet.values_list('id', flat=True)),
                                                 'total': all_filtered_timesheet.count()}
                            count = 0
                            for i in approved_data:
                                count =+ i['total']
                            if count+all_filtered_timesheet.count() == onereport.submit_timesheet.count():
                                approve_val = True
                            else:
                                approve_val = False
                            approved_data.append(new_approved_data)
                            serializer.save(approve=approve_val, approve_data=approved_data)
                            all_filtered_timesheet.update(approve=True, submit=True)
                            message = "Weekly data approved"
                        else:
                            if any([onereport.reject_data == [], onereport.reject_data == "", onereport.reject_data == None]):
                                rejected_data = []
                            else:
                                rejected_data = onereport.reject_data
                            new_rejected_data = {'manager': user.empID,
                                                 'reject': list(all_filtered_timesheet.values_list('id', flat=True)),
                                                 'total': len(all_filtered_timesheet)}
                            rejected_data.append(new_rejected_data)
                            serializer.save(approve=False, reject_data=rejected_data)
                            all_filtered_timesheet.update(approve=False, submit=False)
                            message = "Weekly data rejected"
                        return Response({'msg': message}, status=status.HTTP_200_OK)
                    return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
                return Response({'msg': f'Weeklyreport with -{pk}- ID does not exist ...'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)


