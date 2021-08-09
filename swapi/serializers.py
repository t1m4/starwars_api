from rest_framework import serializers

from swapi.models import File


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'filename', 'datetime', 'count_of_people']

