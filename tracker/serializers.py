from rest_framework import serializers
from .models import DepartmentTracker, LeaveAppication
from django.utils import timezone


class DepartmentTrackerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentTracker
        fields = "__all__"



class LeaveAppicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveAppication
        fields = ['start_date', 'start_half', 'end_date', 'end_half', 'message', 'leave_type']


    def validate(self, attrs):
        start_date = attrs['start_date']
        end_date = attrs['end_date']
        
        if end_date < timezone.now().date():
            raise serializers.ValidationError("You can not apply leave for already past dates ..")

        if start_date > end_date:
            raise serializers.ValidationError("Start date must be before or equal to end date ..")
        
        if start_date == end_date:
            if attrs['start_half'] == "second_half" and attrs['end_half'] == "first_half":
                raise serializers.ValidationError("You cannot apply for leave starting from the second half to the first half on the same day.")
        return attrs


    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['employee'] = user
        return super().create(validated_data)
    

    def update(self, instance, validated_data):
        # return super().update(instance, validated_data)
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.start_half = validated_data.get('start_half', instance.start_half)
        instance.end_date = validated_data.get('end_date', instance.end_date)
        instance.end_half = validated_data.get('end_half', instance.end_half)
        instance.message = validated_data.get('message', instance.message)
        instance.leave_type = validated_data.get('leave_type', instance.leave_type)
        instance.save()
        return instance
    


class LeaveAppicationRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveAppication
        fields = "__all__"

