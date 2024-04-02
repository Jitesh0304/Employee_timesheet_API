from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from account.models import Employee
from projectdata.models import Project
from .serializers import TimesheetSerializer, TimesheetRetrieveSerializer, WeeklyReportSerializer, \
    ManagerWeeklyReportRetrieveSerializer
from .models import Timesheet, WeeklyReport
from django.db.models import Q, F, Count
# from datetime import datetime, timedelta
from .utils import get_week_nums_and_days_till_today, get_all_days_of_the_week, get_current_and_previous_week_days,\
     check_date_format
from django.db import transaction  ## IntegrityError
# from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models.functions import ExtractWeek, ExtractMonth
from projectdata.custom_permission import AdminPermission






class TimesheetCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]


    # def get(self, request, format=None):
    #     user = request.user
    #     try:
    #         today = timezone.datetime.now().date()
    #         fifteen_days_ago = today - timedelta(days=15)
    #         # all_data = Timesheet.objects.filter(organization= user.organization, employee= user).exclude(date__lte = fifteen_days_ago)
    #         all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
    #                                             date__range=[fifteen_days_ago, today], submit=False, approve=False)
    #         # all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
    #         #                                     submit=False, approve=False)
    #         serializer = TimesheetRetrieveSerializer(all_data, many=True)
    #         return Response({'msg':serializer.data}, status= status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        user = request.user
        try:
            current_year, current_week_number, _ = timezone.now().isocalendar()
            two_weeks_days = get_current_and_previous_week_days(current_year, current_week_number)
            filter_q = Q(organization=user.organization, employee=user)
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
                        all_data[week] = serializer.data
                return Response({'msg':all_data}, status= status.HTTP_200_OK)
            else:
                # print(two_weeks_days)
                week_data = Timesheet.objects.filter(filter_q & Q(date__range= [two_weeks_days[0], two_weeks_days[-1]]))
                serializer = TimesheetRetrieveSerializer(week_data, many=True)
                all_data = {current_week_number:serializer.data}
                return Response({'msg':all_data}, status= status.HTTP_200_OK)
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
            # timesheet_data = Timesheet.objects.filter(Q(organization= user.organization, id=pk, employee=user) |
            #                                             Q(organization= user.organization, id=pk, 
            #                                             project_name__projectManager=user)).exclude(submit=True).first()

            timesheet_data = Timesheet.objects.filter(organization= user.organization, id=pk, employee=user).exclude(submit=True).first()
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







class EmployeeRetriveDataWeekly(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request, format=None):
    #     user = request.user
    #     try:
    #         # today = timezone.datetime.now().date()
    #         # fifteen_days_ago = today - timedelta(days=15)
    #         # all_data = Timesheet.objects.filter(organization= user.organization, employee= user).exclude(date__lte = fifteen_days_ago)
    #         # all_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
    #         #                                     date__range=[fifteen_days_ago, today], submit=False, approve=False)

    #         current_year, current_week_number, current_day = (timezone.now().isocalendar()[0], timezone.now().isocalendar()[1], 
    #                                                                 timezone.now().isocalendar()[2])
    #         weeks_till_today = get_week_nums_and_days_till_today(current_year, current_week_number)

    #         all_data = {}
    #         for week, days in weeks_till_today.items():
    #             week_data = Timesheet.objects.filter(organization= user.organization, employee= user, 
    #                                             date__range=[days[0],days[-1]])
    #             if not week_data:
    #                 pass
    #             else:
    #                 serializer = TimesheetRetrieveSerializer(week_data, many=True)
    #                 all_data[week] = serializer.data
    #         return Response({'msg':all_data}, status= status.HTTP_200_OK)
    #     except Exception as e:
    #         return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def get(self, request, wknum=None, format=None):
        user = request.user
        try:
            current_year, current_week_number, _ = timezone.now().isocalendar()
            all_data = {}
            if wknum:
                week_days = get_all_days_of_the_week(current_year, wknum)
                week_data = Timesheet.objects.filter(organization=user.organization, employee=user, 
                                                     date__range=[week_days[0], week_days[-1]])
                serializer = TimesheetRetrieveSerializer(week_data, many=True)
                all_data[wknum] = serializer.data
            else:
                weeks_till_today = get_week_nums_and_days_till_today(current_year, current_week_number)
                filter_q = Q(organization=user.organization, employee=user) ## , submit=False, approve=False
                ###   OR operation for all weeks
                date_q = Q()
                for week, days in weeks_till_today.items():
                    date_q |= Q(date__range=[days[0], days[-1]])

                week_data = Timesheet.objects.filter(filter_q & date_q)

                for week, days in weeks_till_today.items():
                    week_data_for_week = week_data.filter(date__range=[days[0], days[-1]])
                    if week_data_for_week.exists():
                        serializer = TimesheetRetrieveSerializer(week_data_for_week, many=True)
                        all_data[week] = serializer.data

            return Response({'msg': all_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class EmployeeRetriveDataApproveNotApprove(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            current_year, current_week_number, _ = timezone.now().isocalendar()

            weeks_till_today = get_week_nums_and_days_till_today(current_year, current_week_number)
            filter_q = Q(organization=user.organization, employee=user) ## , submit=False, approve=False
            ###   OR operation for all weeks
            date_q = Q()
            for week, days in weeks_till_today.items():
                date_q |= Q(date__range=[days[0], days[-1]])

            week_data = Timesheet.objects.filter(filter_q & date_q)

            all_data = {}
            all_data['Admin_Approve'] = {}
            all_data['Manager_Approve'] = {}
            all_data['Submit'] = {}
            all_data['NotSubmit'] = {}
            for week, days in weeks_till_today.items():
                week_data_for_week = week_data.filter(date__range=[days[0], days[-1]])
                if week_data_for_week.exists():
                    
                    # serializer = TimesheetRetrieveSerializer(week_data_for_week, many=True)
                    # if week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=True):
                    #     all_data['Admin_Approve'][week] = serializer.data
                    # elif week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=False):
                    #     all_data['Manager_Approve'][week] = serializer.data
                    # elif week_data_for_week.filter(submit=True, manager_approve=False, admin_approve=False):
                    #     all_data['Submit'][week] = serializer.data
                    # elif week_data_for_week.filter(submit=False, manager_approve=False, admin_approve=False):
                    #     all_data['NotSubmit'][week] = serializer.data
                    if week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=True):
                        admin_approve_filter = week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=True)
                        admin_serializer = TimesheetRetrieveSerializer(admin_approve_filter, many=True)
                        all_data['Admin_Approve'][week] = admin_serializer.data
                    elif week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=False):
                        manager_approve_filter = week_data_for_week.filter(submit=True, manager_approve=True, admin_approve=False)
                        manager_serializer = TimesheetRetrieveSerializer(manager_approve_filter, many=True)
                        all_data['Manager_Approve'][week] = manager_serializer.data
                    elif week_data_for_week.filter(submit=True, manager_approve=False, admin_approve=False):
                        submit_data = week_data_for_week.filter(submit=True, manager_approve=False, admin_approve=False)
                        submit_serializer = TimesheetRetrieveSerializer(submit_data, many=True)
                        all_data['Submit'][week] = submit_serializer.data
                    elif week_data_for_week.filter(submit=False, manager_approve=False, admin_approve=False):
                        notsubmit_data = week_data_for_week.filter(submit=False, manager_approve=False, admin_approve=False)
                        notsubmit_serializer = TimesheetRetrieveSerializer(notsubmit_data, many=True)
                        all_data['NotSubmit'][week] = notsubmit_serializer.data

            return Response({'msg': all_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)







class ManagerRetrieveTimesheetView(APIView):
    permission_classes = [IsAuthenticated]

    # def get(self, request, format=None):
    #     user = request.user
    #     try:
    #         if user.is_manager:
    #             all_data = Timesheet.objects.filter(organization=user.organization, project_name__projectManager=user,
    #                                                 submit=True, approve=False)
                
    #             ###  <QuerySet [{'project_name': 'project2', 'employee': 'aspl3', 'timesheet_count': 2}]>
    #             grouped_data = all_data.values('project_name', 'employee').annotate(timesheet_count=Count('id'))
    #             # print(grouped_data)

    #             final_data = {}
    #             for entry in grouped_data:
    #                 project_name = entry['project_name']
    #                 employee_id = entry['employee']
    #                 timesheets = all_data.filter(project_name=project_name, employee=employee_id)
    #                 serializer = TimesheetRetrieveSerializer(timesheets, many=True)
                    
    #                 ## append all data to final dict
    #                 if project_name not in final_data:
    #                     final_data[project_name] = {}
    #                 final_data[project_name][employee_id] = serializer.data

    #             return Response({'msg': final_data}, status=status.HTTP_200_OK)
    #         return Response({'msg': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
    #     except Exception as e:
    #         return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, format=None):
        user = request.user
        try:
            if user.is_manager:
                all_data = Timesheet.objects.filter(organization=user.organization, project_name__projectManager=user, 
                                                    submit=True, manager_approve=False)
                ## <QuerySet [{'project_name': 'project2', 'employee': 'aspl3', 'week_number': 10, 'timesheet_count': 2}]>
                grouped_data = all_data.annotate(week_number=ExtractWeek('date')).values('week_number','project_name',
                                                            'employee').annotate(timesheet_count=Count('id'))
                # print(grouped_data)
                final_data = {}
                for entry in grouped_data:
                    week_number = entry['week_number']
                    project_name = entry['project_name']
                    employee_id = entry['employee']
                    timesheets = all_data.filter(date__week=week_number, project_name=project_name,
                                                        employee=employee_id)
                    serializer = TimesheetRetrieveSerializer(timesheets, many=True)

                    # if week_number not in final_data:
                    #     final_data[week_number] = {}
                    # if project_name not in final_data[week_number]:
                    #     final_data[week_number][project_name] = {}
                    # final_data[week_number][project_name][employee_id] = serializer.data

                    if project_name not in final_data:
                        final_data[project_name] = {}
                    if employee_id not in final_data[project_name]:
                        final_data[project_name][employee_id] = {}
                    final_data[project_name][employee_id]["week_"+str(week_number)] = serializer.data

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

                endDate = week_end_date.isocalendar()
                startDate = week_start_date.isocalendar()
                if startDate[1] != endDate[1]:
                    total_weeks = [i for i in range(startDate[1], endDate[1]+1)]
                    return Response({'msg':f'Send only one week data ... you are sending more then one week data {total_weeks}'}, 
                                    status= status.HTTP_400_BAD_REQUEST)
                
                weekly_report = WeeklyReport.objects.filter(employee= user, week_start_date__range=[week_start_date, week_end_date])
                if weekly_report.exists():
                    all_timesheet = Timesheet.objects.filter(organization=user.organization,employee=user, 
                                                             date__range=[week_start_date, week_end_date],
                                                            manager_approve=False, submit=False)        #, submit=False
                

                    ##########################################################################

                    new_timesheet_dict = all_timesheet.values_list("id", flat=True).annotate(project_name=
                                                                    F('project_name')).values('id', 'project_name')
                    project_tsid_dict = {}
                    for timesheet_data in new_timesheet_dict:
                        timesheet_id = timesheet_data['id']
                        project_name = timesheet_data['project_name']
                        project_tsid_dict.setdefault(project_name, []).append(timesheet_id)


                    all_timesheets_ids = all_timesheet.values_list('id', flat=True).distinct()

                    all_projects = all_timesheet.values_list('project_name', flat=True).distinct()
                    if weekly_report:
                        empty_reports = set()
                        ts_id = []
                        reportid_projects = {}
                        for oneid in all_timesheets_ids:
                            reports = weekly_report.filter(submit_timesheet=oneid)
                            if reports.exists():
                                report = reports.first()
                                timesheets = report.submit_timesheet.all()
                                if timesheets.count() >= 2:
                                    project_names = list({timesheet.project_name.projectName for timesheet in timesheets})
                                    report.submit_timesheet.remove(oneid)
                                    reportid_projects[report.id] = project_names
                                    ts_id.append(oneid)
                                else:
                                    project_names = list({timesheet.project_name.projectName for timesheet in timesheets})
                                    report.submit_timesheet.remove(oneid)
                                    empty_reports.add(report.id)
                                    reportid_projects[report.id] = project_names
                                    ts_id.append(oneid)

                        copy_reportid_projects = reportid_projects.copy()
                        copy_ts_id = ts_id.copy()

                        if reportid_projects:
                            for i,(wkid_num, prlist) in enumerate(reportid_projects.items()):
                                for proj in prlist:
                                    weekly_rp = weekly_report.filter(submit_timesheet__project_name__projectName = proj)
                                    project_timesheet_ids = list(all_timesheet.filter(project_name__projectName = 
                                                                                      proj).values_list('id', flat=True))
                                    if weekly_rp.exists():
                                        weekly_rp.first().submit_timesheet.add(*project_timesheet_ids)
                                        try:
                                            copy_reportid_projects.pop(wkid_num)
                                        except Exception:
                                            pass
                                        try:
                                            x = [copy_ts_id.remove(item) for item in project_timesheet_ids]
                                        except Exception:
                                            pass
                                    else:
                                        weekly_rp = weekly_report.filter(id=wkid_num).first()
                                        weekly_rp.submit_timesheet.add(*project_timesheet_ids)
                                        try:
                                            copy_reportid_projects.pop(wkid_num)
                                        except Exception:
                                            pass
                                        try:
                                            x = [copy_ts_id.remove(item) for item in project_timesheet_ids]
                                        except Exception:
                                            pass
                        if copy_ts_id:
                            new_dict = all_timesheet.filter(id__in=copy_ts_id).values_list("id", flat=True).annotate(project_name=
                                                                            F('project_name')).values('id', 'project_name')
                            proj_tsID_dict = {}
                            for timesheet_data in new_dict:
                                timesheet_id = timesheet_data['id']
                                project_name = timesheet_data['project_name']
                                proj_tsID_dict.setdefault(project_name, []).append(timesheet_id)

                            for proj,ts_list in proj_tsID_dict.items():
                                same_project_report = WeeklyReport.objects.filter(employee= user, week_start_date__range=[week_start_date,
                                                 week_end_date], submit_timesheet__project_name__projectName= proj)
                                if same_project_report.exists():
                                    same_project_report.first().submit_timesheet.add(*ts_list)
                                else:
                                    null_record = WeeklyReport.objects.filter(employee= user, week_start_date__range=[week_start_date,
                                                 week_end_date], submit_timesheet__isnull=True)
                                    if null_record.exists():
                                        null_record.first().submit_timesheet.add(*ts_list)
                                    else:
                                        newreport = WeeklyReport.objects.create(
                                            employee= user, week_start_date= week_start_date, week_end_date=week_end_date,
                                            submit=True, managerApprove=False, submit_date= timezone.now(), adminApprove=False
                                            )
                                        newreport.submit_timesheet.set(ts_list)

                    if all_timesheet.exists():
                        total_updates = all_timesheet.update(submit=True)
                    else:
                        total_updates = 0
                    return Response({'msg':f'Your {total_updates} timesheet datas has been updated ...'}, 
                                    status= status.HTTP_201_CREATED)

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
                print('ok2')
                all_timesheet = Timesheet.objects.filter(organization=user.organization,
                                                        employee=user, date__range=[week_start_date, week_end_date],
                                                        submit=False)
                
                if all_timesheet.exists():
                    all_projects = all_timesheet.values_list('project_name', flat=True).distinct()

                    for project in all_projects:
                        project_timesheet = all_timesheet.filter(project_name=project)
                        onereport = WeeklyReport.objects.create(
                            employee= user, week_start_date= week_start_date, week_end_date=week_end_date,
                            submit=True, managerApprove=False, submit_date= timezone.now(), adminApprove=False
                        )
                        onereport.submit_timesheet.set(project_timesheet)
                    updated_count = all_timesheet.update(submit=True)
                    return Response({'msg':f'Weekly report added and {updated_count} timesheet data updated ...'},
                            status= status.HTTP_201_CREATED)
                return Response({'msg':'You do not have any data between these days'}, status= status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'msg':str(e)}, status=status.HTTP_400_BAD_REQUEST)




    def get(self, request, pk=None, format=None):
        user = request.user
        try:
            if user.is_manager or user.is_admin:
                if pk:
                        # report = WeeklyReport.objects.get(id= pk, submit=True, approve=False)
                    report = WeeklyReport.objects.filter(id= pk, submit_timesheet__submit=True,
                                                          submit_timesheet__manager_approve=False).first()
                    if report:
                        # filtered_report = report.filter(submit_timesheet__project_name__projectManager=user).values_list(
                        #                                             'submit_timesheet__id')
                        filtered_report = report.submit_timesheet.filter(project_name__projectManager=user, submit=True, 
                                                                         manager_approve=False)
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
                                                           submit_timesheet__submit=True,submit_timesheet__manager_approve=False)
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




        ###   week report id is required
# class WeekReportManagerUpdateView(APIView):
#     permission_classes = [IsAuthenticated]

#     def patch(self, request, pk, format=None):
#         user = request.user
#         try:
#             if user.is_manager:
#                 onereport = WeeklyReport.objects.filter(id= pk, submit_timesheet__submit=True,
#                                                         submit_timesheet__approve=False).first()
#                 if onereport:
#                     serializer = ManagerWeeklyReportRetrieveSerializer(onereport, data=request.data, partial=True,
#                                                                        context={'request':request})
#                     if serializer.is_valid():
#                         approve = serializer.validated_data['approve']
#                         all_filtered_timesheet = onereport.submit_timesheet.filter(project_name__projectManager=user,submit=True,
#                                                                             approve=False)
#                         if approve:
#                             if any([onereport.approve_data == [], onereport.approve_data == "", onereport.approve_data == None]):
#                                 approved_data = []
#                             else:
#                                 approved_data = onereport.approve_data

#                             new_approved_data = {'manager': user.empID,
#                                                  'approve': list(all_filtered_timesheet.values_list('id', flat=True)),
#                                                  'total': all_filtered_timesheet.count()}
#                             count = 0
#                             for i in approved_data:
#                                 count =+ i['total']
#                             if count+all_filtered_timesheet.count() == onereport.submit_timesheet.count():
#                                 approve_val = True
#                             else:
#                                 approve_val = False
#                             approved_data.append(new_approved_data)
#                             serializer.save(approve=approve_val, approve_data=approved_data)
#                             all_filtered_timesheet.update(approve=True, submit=True)
#                             message = "Weekly data approved"
#                         else:
#                             if any([onereport.reject_data == [], onereport.reject_data == "", onereport.reject_data == None]):
#                                 rejected_data = []
#                             else:
#                                 rejected_data = onereport.reject_data
#                             new_rejected_data = {'manager': user.empID,
#                                                  'reject': list(all_filtered_timesheet.values_list('id', flat=True)),
#                                                  'total': all_filtered_timesheet.count()}
#                             rejected_data.append(new_rejected_data)
#                             serializer.save(approve=False, reject_data=rejected_data)
#                             all_filtered_timesheet.update(approve=False, submit=False)
#                             message = "Weekly data rejected"
#                         return Response({'msg': message}, status=status.HTTP_200_OK)
#                     return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
#                 return Response({'msg': f'Weeklyreport with -{pk}- ID does not exist ...'}, status=status.HTTP_400_BAD_REQUEST)
#             return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)




class ManagerApproveTimesheetView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request,format=None):
        user = request.user
        try:
            if user.is_manager:
                
                required_data = ["week_start_date", "week_end_date", "employee_id", "approve"]
                missing_fields = [field for field in required_data if field not in request.data]

                if missing_fields:
                    return Response({'msg': f'Required fields are missing : [{", ".join(missing_fields)}]'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
                week_start_date = check_date_format(request.data.get("week_start_date"))
                week_end_date = check_date_format(request.data.get("week_end_date"))

                if not week_start_date or not week_end_date:
                    return Response({'msg': f'Date format should be => YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
                # employee_id = request.data.get('employee_id')
                # approve = request.data.get('approve')
                employee_id = request.data['employee_id']
                req_approve = request.data['approve']
                
                endDate = week_end_date.isocalendar()
                startDate = week_start_date.isocalendar()
                if startDate[1] != endDate[1]:
                    total_weeks = [i for i in range(startDate[1], endDate[1]+1)]
                    return Response({'msg':f'Send only one week data ... you are sending more then one week data {total_weeks}'}, 
                                    status= status.HTTP_400_BAD_REQUEST)
                
                timesheet_data = Timesheet.objects.filter(project_name__projectManager=user, submit=True, employee__empID=employee_id,
                                                          manager_approve=False, date__range=[week_start_date, week_end_date])
                # print(timesheet_data)

                if req_approve=="True":
                    # all_timesheet_ids = timesheet_data.values_list('id', flat=True)
                    # print(all_timesheet_ids)
                    onereport = WeeklyReport.objects.filter(submit_timesheet__submit=True, employee__empID=employee_id,
                                                            submit_timesheet__in = timesheet_data,
                                                            submit_timesheet__manager_approve=False).distinct()
                    onereport.update(managerApprove=True)
                    total = timesheet_data.update(manager_approve=True)
                    message = f"Total {total} timesheet data approved..."
                else:
                    total = timesheet_data.update(manager_approve=False, submit=False)
                    message = f"Total {total} timesheet data rejected..."
                return Response({'msg': message}, status=status.HTTP_200_OK)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)





class AdminApproveTimesheetView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]


    def get(self, request, emp, format=None):
        user = request.user
        try:
            if user.is_manager:
                try:
                    employee_data = Employee.objects.get(empID=emp, organization=user.organization)
                except Exception:
                    return Response({'msg': f'No employee is present with this {emp} empID in your organization '}, 
                                    status=status.HTTP_403_FORBIDDEN)
                all_data = Timesheet.objects.filter(employee= employee_data, organization=user.organization, submit=True) ## manager_approve=True
                ## <QuerySet [{'project_name': 'project2', 'employee': 'aspl3', 'month_number': 10, 'timesheet_count': 2}]>
                grouped_data = all_data.annotate(month_number=ExtractMonth('date')).values('month_number').annotate(
                                                                                    timesheet_count=Count('id'))
                # print(grouped_data)
                final_data = {}
                for entry in grouped_data:
                    month_number = entry['month_number']
                    timesheets = all_data.filter(date__month=month_number)
                    serializer = TimesheetRetrieveSerializer(timesheets, many=True)
                    if emp not in final_data:
                        final_data[emp] = {}

                    # if month_number not in final_data:
                    #     final_data[emp][month_number] = {}
                    final_data[emp][month_number] = serializer.data

                return Response({'msg': final_data}, status=status.HTTP_200_OK)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def post(self, request,format=None):
        user = request.user
        try:
            if user.is_admin:
                required_data = ["week_start_date", "week_end_date", "employee_id", "approve"]
                missing_fields = [field for field in required_data if field not in request.data]

                if missing_fields:
                    return Response({'msg': f'Required fields are missing : [{", ".join(missing_fields)}]'}, 
                                    status=status.HTTP_400_BAD_REQUEST)
                week_start_date = check_date_format(request.data.get("week_start_date"))
                week_end_date = check_date_format(request.data.get("week_end_date"))

                if not week_start_date or not week_end_date:
                    return Response({'msg': f'Date format should be => YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
                # employee_id = request.data.get('employee_id')
                # approve = request.data.get('approve')
                employee_id = request.data['employee_id']
                req_approve = request.data['approve']
                
                startDate_month = week_start_date.strftime("%m")
                endDate_month = week_end_date.strftime("%m")
                if endDate_month != startDate_month:
                    # total_weeks = [i for i in range(startDate_month, endDate_month+1)]
                    return Response({'msg': 'Send only one month data ... you are sending more then one month data'}, 
                                    status= status.HTTP_400_BAD_REQUEST)
                
                timesheet_data = Timesheet.objects.filter(submit=True, employee__empID=employee_id,
                                                        date__range=[week_start_date, week_end_date])  ## manager_approve=True,

                onereport = WeeklyReport.objects.filter(submit_timesheet__submit=True, employee__empID=employee_id,
                                                        submit_timesheet__in = timesheet_data,
                                                        ).distinct()   ## submit_timesheet__manager_approve=True
                print(timesheet_data)
                if req_approve=="True":
                    # all_timesheet_ids = timesheet_data.values_list('id', flat=True)
                    # print(all_timesheet_ids)
                    onereport.update(adminApprove=True)
                    total = timesheet_data.update(admin_approve=True)
                    message = f"Total {total} timesheet data approved..."
                else:
                    onereport.update(adminApprove=False, managerApprove=False)
                    total = timesheet_data.update(manager_approve=False, admin_approve=False, submit=True)
                    message = f"Total {total} timesheet data rejected..."
                return Response({'msg': message}, status=status.HTTP_200_OK)
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



