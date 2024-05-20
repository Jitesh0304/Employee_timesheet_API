from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
# from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
# from account.models import Employee
from .models import Project, ProjectSubcode, ProjectSubcodeActivity
from .serializers import ProjectCreateSerializer, ProjectSubcodeSerializer, ProjectSubcodeActivitySerializer, \
    ProjectSerializerRetrive
from account.custom_auth import AdminPermission, ManagerPermission
from timesheet.models import Timesheet
from django.db.models import Q, F, Count
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch



class ProjectCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated, AdminPermission]

    def post(self, request, format=None):
        user = request.user
        try:
            serializer = ProjectCreateSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project data saved ...'}, status= status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



    def patch(self, request, prID, format=None):
        user = request.user
        try:
            try:
                project = Project.objects.get(projectName= prID)
            except Exception:
                return Response({'msg':'Project does not exist in your organization ...'}, status= status.HTTP_400_BAD_REQUEST)
            serializer = ProjectCreateSerializer(project, data= request.data, context={'request':request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project data saved ...'}, status= status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



# class ProjectDetailsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, pk=None, format=None):
#         user = request.user
#         try:
#             if not pk:
#                 all_projects = Project.objects.filter(complete=False)
#                 serializer = ProjectCreateSerializer(all_projects, many=True)
#                 return Response({"all_projects":serializer.data}, status= status.HTTP_200_OK)
#             else:
#                 try:
#                     project = Project.objects.get(projectID=pk)
#                 except Exception:
#                     return Response({'msg':'Project does not exist in your organization ...'}, status= status.HTTP_400_BAD_REQUEST)
#                 serializer = ProjectCreateSerializer(project)
#                 return Response({"project_data":serializer.data}, status= status.HTTP_200_OK)
#         except Exception as e:
#             return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)





class ProjectSubcodeView(APIView):
    permission_classes = [AdminPermission, IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        try:
            serializer = ProjectSubcodeSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project subcode is saved ....'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)


    def patch(self, request, pk, format=None):
        user = request.user
        try:
            try:
                pro_subcode = ProjectSubcode.objects.get(id= pk)
            except Exception:
                return Response({'msg':"Subcode does not exist .."}, status= status.HTTP_400_BAD_REQUEST)
            serializer = ProjectSubcodeSerializer(pro_subcode, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project subcode is updated ....'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



class ProjectSubcodeRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, proj, format=None):
        user = request.user
        try:
            # project_subcode_data = ProjectSubcode.objects.filter(project__projectID=proj).values_list('projectSubcode',
                                                                                                    #   flat=True).distinct()
            # return Response({'project': proj, 'subcodes':project_subcode_data}, status= status.HTTP_200_OK)

            project_subcode_data = ProjectSubcode.objects.filter(project__projectID=proj).values('id','projectSubcode')

            return Response({'msg': project_subcode_data}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)





class ProjectSubcodeActivityView(APIView):
    permission_classes = [AdminPermission, IsAuthenticated]

    def post(self, request, format=None):
        user = request.user
        try:
            serializer = ProjectSubcodeActivitySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project subcode activity is saved ....'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk, format=None):
        user = request.user
        try:
            try:
                subcode_activity = ProjectSubcodeActivity.objects.get(id= pk)
            except Exception:
                return Response({'msg':"Subcode activity does not exist .."}, status= status.HTTP_400_BAD_REQUEST)
            serializer = ProjectSubcodeActivitySerializer(subcode_activity, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Project subcode activity is updated ....'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



class ProjectSubcodeActivityRetrieveView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, psubID, format=None):
        user = request.user
        try:
            project_subcode_activitydata = ProjectSubcodeActivity.objects.filter(
                projectsubcode__id=psubID).values('id','activityCode', 'name')
            # serializer = ProjectSubcodeSerializer(project_subcode_data, many=True)
            return Response({'msg':project_subcode_activitydata}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)




class ProjectNameView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        try:
            if user.role.id == 1:
                all_projects = Project.objects.all().values('projectID','projectName', 'projectCode')
            else:
                all_projects = Project.objects.filter(complete=False).values('projectID','projectName', 'projectCode')
            # project_data_dict = {project.projectID:project.projectName for project in all_projects}
            return Response({'msg': all_projects}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)



###   manager can only see those projects where he/she is the manager of those projects
class ManagerRetrieveAllProjects(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def get(self, request, format=None):
        try:
            user = request.user
            all_projects = Project.objects.filter(projectManager=user, complete=False).values("projectID", "projectCode","projectName")
            # serializer = ProjectCreateSerializer(all_projects, many=True)
            return Response({'all_projects':all_projects}, status= status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg':str(e)}, status= status.HTTP_400_BAD_REQUEST)




class ManagerRetrieveProjectUser(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def get(self, request, pk, format=None):
        user = request.user
        try:
            try:
                project_data = Project.objects.get(projectManager=user, projectID=pk)
            except Exception:
                return Response({'msg': 'Project does not belongs to you ....'}, status=status.HTTP_400_BAD_REQUEST)
            # if project_data.complete:
            #     return Response({'msg': 'Project is completed ... you can not see completed project data ....'}, 
            #                     status=status.HTTP_400_BAD_REQUEST)
            associated_users = Timesheet.objects.filter(project=project_data).values_list(
                                            'employee', flat=True).distinct()
            res_data = {'id': pk, 'all_employees': list(set(associated_users))}
            return Response({'msg': res_data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class ProjectDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, id=None, format=None):
        user = request.user
        if id:
            ## Get the Project with its related ProjectSubcode and ProjectSubcodeActivity
            project = get_object_or_404(
                Project.objects.prefetch_related(
                    'project_subcode__project_subcode_activity'  ## Prefetch ProjectSubcodeActivity through ProjectSubcode
                ),
                projectID=id
            )

            print(project)
            ## Serialize the Project data
            serializer = ProjectSerializerRetrive(project)
        else:
            ## Get the Project with its related ProjectSubcode and ProjectSubcodeActivity
            project = Project.objects.filter(organization=user.organization, complete=False).prefetch_related(
                Prefetch('project_subcode__project_subcode_activity')
            )

            ## Serialize the Project data
            serializer = ProjectSerializerRetrive(project, many=True)

        ## Return the serialized data in the response
        return Response({'msg':serializer.data}, status=status.HTTP_200_OK)