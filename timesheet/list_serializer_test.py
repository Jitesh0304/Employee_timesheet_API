
from rest_framework import serializers

class BulkUpdateListSerializer(serializers.ListSerializer):
    def update(self, queryset, validated_data):
        # Ensure we have a valid list of updates
        if len(queryset) != len(validated_data):
            raise serializers.ValidationError("Mismatched data count for bulk update.")

        # Map each object to its data
        object_data_map = {item['id']: item for item in validated_data}

        # Update each object in the queryset
        updated_objects = []
        for obj in queryset:
            obj_data = object_data_map.get(obj.id)
            if obj_data:
                for attr, value in obj_data.items():
                    setattr(obj, attr, value)
                obj.save()
                updated_objects.append(obj)

        return updated_objects

class ManagerModifyEmpTimesheetView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def patch(self, request, format=None):
        try:
            timesheet_ids = request.data.get('ids', [])
            if not timesheet_ids:
                return Response({"msg": "No timesheet IDs provided."}, status=400)

            timesheets = Timesheet.objects.filter(id__in=timesheet_ids, status__id=2)
            if timesheets.count() != len(timesheet_ids):
                raise Http404("Some timesheets not found or do not have the correct status.")

            serializer = ManagerUpdateEmpTimesheetSerializer(timesheets, data=request.data['data'], many=True, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Timesheets updated successfully."}, status=200)

            return Response(serializer.errors, status=400)

        except Http404 as e:
            return Response({"msg": str(e)}, status=404)
        except Exception as e:
            return Response({"msg": str(e)}, status=500)









from rest_framework import serializers

class TimesheetListSerializer(serializers.ListSerializer):
    def update(self, queryset, validated_data):
        # Maps for id->instance and id->data item.
        timesheet_mapping = {timesheet.id: timesheet for timesheet in queryset}
        data_mapping = {item['id']: item for item in validated_data}

        ret = []
        for timesheet_id, data in data_mapping.items():
            timesheet = timesheet_mapping.get(timesheet_id, None)
            if timesheet is not None:
                ret.append(self.child.update(timesheet, data))

        return ret


class ManagerModifyEmpTimesheetView(APIView):
    permission_classes = [IsAuthenticated, ManagerPermission]

    def patch(self, request, format=None):
        try:
            timesheet_ids = request.data.get('ids', [])
            if not timesheet_ids:
                return Response({"msg": "No timesheet IDs provided."}, status=400)

            timesheets = Timesheet.objects.filter(id__in=timesheet_ids, status__id=2)

            serializer = ManagerUpdateEmpTimesheetSerializer(
                timesheets,
                data=request.data['data'],
                many=True,
                partial=True
            )

            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Timesheets updated successfully."}, status=200)
            
            return Response(serializer.errors, status=400)

        except Exception as e:
            return Response({"msg": str(e)}, status=500)
