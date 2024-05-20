from rest_framework import serializers
from .models import Project, ProjectSubcode, ProjectSubcodeActivity
from django.utils import timezone
from account.serializers import OrganizationSerializer




class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"


    def validate(self, attrs):
        user = self.context.get('request').user
        if "projectManager" not in attrs:
            raise serializers.ValidationError("-projectManager- field is missing ....")
        project_manager = attrs.get('projectManager')
        if project_manager.organization != user.organization:
            raise serializers.ValidationError("You can't assign other organization user in your organization project ...")
        if project_manager.role.id not in [1,2]:
            raise serializers.ValidationError("-projectManager- user does not have manager rights ... ")
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['projectAddedby'] = user
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        instance.projectManager = validated_data.get('projectManager', instance.projectManager)
        instance.projectCode = validated_data.get('projectCode', instance.projectCode)
        instance.complete = validated_data.get('complete', instance.complete)
        # return super().update(instance, validated_data)
        instance.save()
        return instance

    def to_representation(self, instance):
        # return super().to_representation(instance)
        data = super().to_representation(instance)
        # project_id = data['project']
        # data['projectCode'] = data['pro']
        return data




class ProjectSubcodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubcode
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.projectSubcode = validated_data.get('projectSubcode', instance.projectSubcode)
        instance.description = validated_data.get('description', instance.description)
        # return super().update(instance, validated_data)
        instance.save()
        return instance


class ProjectSubcodeActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubcodeActivity
        fields = "__all__"

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.activityCode = validated_data.get('activityCode', instance.activityCode)
        instance.description = validated_data.get('description', instance.description)
        # return super().update(instance, validated_data)
        instance.save()
        return instance



# Serializer for ProjectSubcodeActivity
class ProjectSubcodeActivitySerializerRetrive(serializers.ModelSerializer):
    class Meta:
        model = ProjectSubcodeActivity
        fields = ['id', 'name', 'activityCode', 'description', 'projectsubcode']


# Serializer for ProjectSubcode with nested ProjectSubcodeActivity
class ProjectSubcodeSerializerRetrive(serializers.ModelSerializer):
    project_subcode_activity = ProjectSubcodeActivitySerializerRetrive(many=True)

    class Meta:
        model = ProjectSubcode
        fields = ['id', 'projectSubcode', 'description', 'project_subcode_activity']
        # fields = ['id', 'projectSubcode', 'description', 'project']


# Serializer for Project with nested ProjectSubcode
class ProjectSerializerRetrive(serializers.ModelSerializer):
    project_subcode = ProjectSubcodeSerializerRetrive(many=True)
    organization = OrganizationSerializer()
    class Meta:
        model = Project
        fields = ['projectID', 'projectName', 'projectCode', 'projectManager', 'projectAddedby', 'complete',
                  'created_at','organization', 'project_subcode']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        project_code = data.get('projectCode', 'Unkown')
        response_data = {project_code : data}
        return response_data