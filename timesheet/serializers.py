from rest_framework import serializers
from .models import Timesheet, Status
from projectdata.models import Project, ProjectSubcode, ProjectSubcodeActivity
from django.db.models import Prefetch
from account.models import CostCenter
# from django.utils import timezone


class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = ['date','hours','project','projectsubcode','project_subcode_activity','location',
                  'year_week', 'comment']


    def validate(self, attrs):
        user = self.context.get('request').user

        required_fields = {'project', 'projectsubcode', 'project_subcode_activity'}
        # if any(field in attrs.keys() for field in required_fields):
        #     raise serializers.ValidationError("project, projectsubcode and project_subcode_activity fields are required ...")
        if not required_fields.issubset(attrs):
            raise serializers.ValidationError(
                "Fields 'project', 'projectsubcode', and 'project_subcode_activity' are required."
            )

        input_project = attrs['project']
        input_project_subcode = attrs['projectsubcode']
        project_subcode_activity = attrs['project_subcode_activity']

        if (project_subcode_activity.projectsubcode.project.projectID != input_project.projectID) or \
            (project_subcode_activity.projectsubcode.id != input_project_subcode.id):
            raise serializers.ValidationError(
                "Mismatch: 'projectsubcode' and 'project_subcode_activity' do not belong to the same project."
            )

        attrs['employee_costcenter'] = user.costcenter

        return attrs



    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['employee'] = user
        return super().create(validated_data)


    # def update(self, instance, validated_data):
    #     instance.project = validated_data.get('project', instance.project)
    #     instance.hours = validated_data.get('hours', instance.hours)
    #     instance.date = validated_data.get('date', instance.date)
    #     instance.comment = validated_data.get('comment', instance.comment)
    #     instance.location = validated_data.get('location', instance.location)
    #     # return super().update(instance, validated_data)
    #     instance.save()
    #     return instance




class TimesheetRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Prefetch related objects in a single query
        queryset = Timesheet.objects.filter(id=instance.id).prefetch_related(
            Prefetch('project', queryset=Project.objects.only('projectID', 'projectName', 'projectCode')),
            Prefetch('status', queryset=Status.objects.only('id', 'statusName')),
            Prefetch('projectsubcode', queryset=ProjectSubcode.objects.only('id', 'projectSubcode')),
            Prefetch('project_subcode_activity', queryset=ProjectSubcodeActivity.objects.only('id', 'activityCode', 'name')),
            Prefetch('employee_costcenter', queryset=CostCenter.objects.only('id', 'name', 'number')),
        ).first()

        project_data = queryset.project
        status_data = queryset.status
        projectsubcode_data = queryset.projectsubcode
        subcodeactivity_data = queryset.project_subcode_activity
        costcenter_data = queryset.employee_costcenter

        if project_data:
            data['project'] = {"projectID": project_data.projectID, "projectName": project_data.projectName,
                               "projectCode": project_data.projectCode}
        if status_data:
            data['status'] = {"id": status_data.id, "statusName": status_data.statusName}

        if projectsubcode_data:
            data['projectsubcode'] = {'id': projectsubcode_data.id, 'projectSubcode':projectsubcode_data.projectSubcode}
            
        if subcodeactivity_data:
            data['project_subcode_activity'] = {'id': subcodeactivity_data.id, 'activityCode':subcodeactivity_data.activityCode,
                                                'name': subcodeactivity_data.name}
            
        if costcenter_data:
            data['employee_costcenter'] = {'id': costcenter_data.id, 'name':costcenter_data.name,
                                                'number': costcenter_data.number}

        return data
    



# class ManagerUpdateEmpTimesheetSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Timesheet
#         fields = ['bill','comment']

#     # def update(self, instance, validated_data):
#     #     instance.bill = validated_data.get('bill', instance.bill)
#     #     instance.comment = validated_data.get('comment', instance.comment)
#     #     instance.save()
#     #     return instance

#     def update(self, instances, validated_data):
#         for instance, data in zip(instances, validated_data):
#             instance.bill = data.get('bill', instance.bill)
#             instance.comment = data.get('comment', instance.comment)
#             instance.save()
#         return instances



class BulkUpdateListSerializer(serializers.ListSerializer):
    def update(self, queryset, validated_data):
        
        if len(queryset) != len(validated_data):
            raise serializers.ValidationError("Mismatched data count for bulk update.")

        # print(validated_data)
        # print(queryset)
        object_data_map = {item['id']: item for item in validated_data}

        updated_objects = []
        for obj in queryset:
            obj_data = object_data_map.get(obj.id)
            if obj_data:
                for attr, value in obj_data.items():
                    setattr(obj, attr, value)
                obj.save()
                updated_objects.append(obj)

        return updated_objects




class ManagerUpdateEmpTimesheetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    class Meta:
        model = Timesheet
        fields = ['id','bill','comment']
        list_serializer_class = BulkUpdateListSerializer


