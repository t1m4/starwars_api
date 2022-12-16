from rest_framework import serializers

from swapi.constants import ALLOWED_PERSON_FIELDS
from swapi.models import File


class PageInputSerializer(serializers.Serializer):
    page = serializers.IntegerField(default=1)


class PersonFieldsInputSerializer(serializers.Serializer):
    person_fields = serializers.CharField(max_length=255)

    def validate_person_fields(self, person_fields: str):
        fields = set(person_fields.replace(" ", "").split(","))
        result_fields = [allowed_field for allowed_field in ALLOWED_PERSON_FIELDS if allowed_field in fields]
        if len(result_fields) < 1:
            raise serializers.ValidationError("Empty fields")
        return result_fields


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ["id", "filename", "datetime", "count_of_people"]
