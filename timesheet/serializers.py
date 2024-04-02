from rest_framework import serializers
from .models import Timesheet, WeeklyReport
from django.utils import timezone


class TimesheetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = ['day', 'date','status','hours','project_name','project_subcode','bill','location','comment']


    def validate(self, attrs):
        user = self.context.get('request').user
        if "project_name" not in attrs or "project_subcode" not in attrs:
            raise serializers.ValidationError("[ project_name or project_subcode ] field is missing ....")
        project = attrs.get('project_name')
        if user.organization != project.organization:
            raise serializers.ValidationError("Project does not belong to your organization")
        attrs['project_code'] = project.projectCode
        if attrs.get("project_subcode") not in project.projectSubCode:
            raise serializers.ValidationError("Please provide a valid project subcode ... ")
        # return super().validate(attrs)
        return attrs

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['employee'] = user
        return super().create(validated_data)


    def update(self, instance, validated_data):
        instance.project_code = validated_data.get('project_code', instance.project_code)
        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.project_subcode = validated_data.get('project_subcode', instance.project_subcode)
        instance.hours = validated_data.get('hours', instance.hours)
        instance.status = validated_data.get('status', instance.status)
        instance.date = validated_data.get('date', instance.date)
        instance.day = validated_data.get('day', instance.day)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.location = validated_data.get('location', instance.location)
        instance.bill = validated_data.get('bill', instance.bill)
        # return super().update(instance, validated_data)
        instance.save()
        return instance




class TimesheetRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timesheet
        fields = "__all__"



class WeeklyReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = ['week_start_date', 'week_end_date','submit']

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['employee'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        instance.week_start_date = validated_data.get('week_start_date', instance.week_start_date)
        instance.week_end_date = validated_data.get('week_end_date', instance.week_end_date)
        # instance.submit = validated_data.get('submit', instance.submit)
        # instance.approve = validated_data.get('approve', instance.approve)
        # instance.submit_date = validated_data.get('submit_date', instance.submit_date)
        # instance.approve_data = validated_data.get('approve_data', instance.approve_data)
        # instance.reject_data = validated_data.get('reject_data', instance.reject_data)
        instance.save()
        return instance


class ManagerWeeklyReportRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeeklyReport
        fields = "__all__"

    def validate(self, attrs):
        user = self.context.get('request').user
        if 'approve' not in attrs:
            raise serializers.ValidationError("[approve] field is missing")
        update_list = ['approve']
        data = {key: value for key, value in attrs.items() if key in update_list}
        return data


    def update(self, instance, validated_data):
        instance.submit = validated_data.get('submit', instance.submit)
        instance.approve = validated_data.get('approve', instance.approve)
        # instance.submit_date = validated_data.get('submit_date', instance.submit_date)
        instance.approve_data = validated_data.get('approve_data', instance.approve_data)
        instance.reject_data = validated_data.get('reject_data', instance.reject_data)
        instance.save()
        return instance
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'approve_data' in data:
            data.pop('approve_data')
        if 'reject_data' in data:
            data.pop('reject_data')
        return data