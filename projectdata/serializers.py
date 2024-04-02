from rest_framework import serializers
from .models import Project
from django.utils import timezone


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
        if not project_manager.is_manager:
            raise serializers.ValidationError("-projectManager- user does not have manager rights ... ")
        return super().validate(attrs)
    
    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['addedby'] = user
        validated_data['organization'] = user.organization
        validated_data['created_at'] = timezone.now()
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        instance.projectCode = validated_data.get('projectCode', instance.projectCode)
        instance.projectSubCode = validated_data.get('projectSubCode', instance.projectSubCode)
        instance.projectManager = validated_data.get('projectManager', instance.projectManager)
        instance.complete = validated_data.get('complete', instance.complete)
        # return super().update(instance, validated_data)
        instance.save()
        return instance
