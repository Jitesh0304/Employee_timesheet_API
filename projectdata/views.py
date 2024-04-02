from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
# from account.models import Employee
from .models import Project
from .serializers import ProjectCreateSerializer
from .custom_permission import AdminPermission, ManagerPermission
from timesheet.models import Timesheet
from django.db.models import Q, F, Count




class ProjectCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        user = request.user
        try:
            if user.is_admin:
                serializer = ProjectCreateSerializer(data= request.data, context={'request':request})
                if serializer.is_valid():
                    serializer.save()
                    return Response({'msg':'Project data saved ...'}, status= status.HTTP_201_CREATED)
                return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
            return Response({'msg':'You have no permissions'}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pname, format=None):
        user = request.user
        try:
            if user.is_admin:
                try:
                    project = Project.objects.get(projectName= pname, organization=user.organization)
                except Exception:
                    return Response({'msg':'Project does not exist in your organization ...'}, status= status.HTTP_400_BAD_REQUEST)
                serializer = ProjectCreateSerializer(project, data= request.data, context={'request':request}, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({'msg':'Project data saved ...'}, status= status.HTTP_201_CREATED)
                return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
            return Response({'msg':'You have no permissions'}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



class ProjectDetailsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pname=None, format=None):
        user = request.user
        try:
            if not pname:
                all_projects = Project.objects.filter(organization= user.organization, complete=False)
                serializer = ProjectCreateSerializer(all_projects, many=True)
                return Response({"all_projects":serializer.data}, status= status.HTTP_200_OK)
            else:
                try:
                    project = Project.objects.get(organization= user.organization, projectName=pname)
                except Exception:
                    return Response({'msg':'Project does not exist in your organization ...'}, status= status.HTTP_400_BAD_REQUEST)
                serializer = ProjectCreateSerializer(project)
                return Response({"project_data":serializer.data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)





class ProjectNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            # project_data = Project.objects.annotate(subcode=F('projectSubCode')).values('projectName', 'subcode')
            # project_data_dict = {project['projectName']: project['subcode'] for project in project_data}
            if user.is_admin:
                all_projects = Project.objects.filter(organization= user.organization)
            else:
                all_projects = Project.objects.filter(organization= user.organization, complete=False)
            project_data_dict = {project.projectName:project.projectSubCode for project in all_projects}
            return Response(project_data_dict, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



###   manager can only see those projects where he/she is the manager of those projects
class ManagerRetrieveAllProjects(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def get(self, request, format=None):
        try:
            user = request.user
            all_projects = Project.objects.filter(organization= user.organization, projectManager=user, complete=False).values_list("projectName", flat=True)
            # serializer = ProjectCreateSerializer(all_projects, many=True)
            return Response({'all_projects':all_projects}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)




class ManagerRetrieveProjectUser(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pname=None, format=None):
        user = request.user
        try:
            if user.is_manager:
                if pname:
                    try:
                        project_data = Project.objects.get(organization=user.organization, projectManager=user,
                                                                 projectName=pname)
                    except Exception:
                        return Response({'msg': 'Project does not belongs to you ....'}, status=status.HTTP_400_BAD_REQUEST)
                    # if project_data.complete:
                    #     return Response({'msg': 'Project is completed ... you can not see completed project data ....'}, 
                    #                     status=status.HTTP_400_BAD_REQUEST)
                    associated_users = Timesheet.objects.filter(project_name=project_data).values_list(
                                                    'employee', flat=True).distinct()
                    return Response({'msg': associated_users}, status=status.HTTP_200_OK)
                else:
                    ## fetch all projects along with the count of associated users
                    projects_with_users = Project.objects.filter(organization=user.organization, projectManager=user).annotate(
                                        user_count=Count('project_related_name__employee', distinct=True))

                    ## Create a dictionary to store project names as keys and lists of associated users as values
                    project_users_dict = {}
                    for project in projects_with_users:
                        project_name = project.projectName
                        associated_users = Timesheet.objects.filter(
                            project_name=project, submit=True, approve=False
                        ).values_list('employee', flat=True).distinct()
                        project_users_dict[project_name] = list(associated_users)

                    return Response({'msg': project_users_dict}, status=status.HTTP_200_OK)        
            return Response({'msg': 'You do not have permission.'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)