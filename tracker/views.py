from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import DepartmentTracker, LeaveAppication
from .serializers import LeaveAppicationSerializer, DepartmentTrackerSerializer, LeaveAppicationRetrieveSerializer
from django.db.models import Q
from account.custom_auth import ManagerPermission, AdminPermission




class DepartmentTrackerView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def get(self, request, pk=None, format=None):
        try:
            user = request.user
            if not pk:
                if user.role.id == 2:
                    dept_data = DepartmentTracker.objects.filter(Q(department= user.department))
                else:
                    dept_data = DepartmentTracker.objects.all()
                serializer = DepartmentTrackerSerializer(dept_data, many=True)
            else:
                try:
                    if user.role.id == 2:
                        dept_data = DepartmentTracker.objects.get(id=pk, department= user.department)
                    else:
                        dept_data = DepartmentTracker.objects.get(id=pk)
                except Exception as e:
                    return Response({'msg': 'Tracer data is not exist '}, status=status.HTTP_400_BAD_REQUEST)
                serializer = DepartmentTrackerSerializer(dept_data)
            return Response({'msg': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



class LeaveAppicationView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, pk=None, format=None):
        try:
            user = request.user
            print(user.role.id)
            if not pk:
                if user.role.id == 2:
                    leave_data = LeaveAppication.objects.filter(status__in=["NotSeen"],employee__department= user.department)
                elif user.role.id == 1:
                    leave_data = LeaveAppication.objects.all().exclude(status="NotSeen")
                else:
                    leave_data = LeaveAppication.objects.filter(employee= user)
                # serializer = LeaveAppicationSerializer(leave_data, many=True)
                user_dict = {leave.id:leave.employee.empID for leave in leave_data}
                return Response({'msg': user_dict}, status=status.HTTP_200_OK)
            else:
                try:
                    if user.role.id == 2:
                        leave_data = LeaveAppication.objects.get(id= pk, status__in=["NotSeen"], employee__department= user.department)
                    elif user.role.id == 1:
                        leave_data = LeaveAppication.objects.get(id= pk)
                    else:
                        leave_data = LeaveAppication.objects.get(id= pk, employee= user)
                    serializer = LeaveAppicationRetrieveSerializer(leave_data)
                except Exception as e:
                    return Response({'msg': 'Leave application does not exist ...'}, status=status.HTTP_400_BAD_REQUEST)
                return Response({'msg': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def post(self, request, format=None):
        user = request.user
        try:
            serializer = LeaveAppicationSerializer(data= request.data, context={'request':request})
            if serializer.is_valid():
                serializer.save(status="NotSeen")
                return Response({'msg':'Leave applied successfully ......'}, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)



    def patch(self, request, pk, format=None):
        user = request.user
        try:
            try:
                leave_data = LeaveAppication.objects.get(id= pk, employee= user, status="NotSeen")
            except Exception as e:
                return Response({'msg': 'Leave application does not exist ...'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = LeaveAppicationSerializer(leave_data, data= request.data, context={'request':request}, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'msg':'Leave application updated successfully ......'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)


