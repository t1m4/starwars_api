import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from swapi.models import File
from tests.swapi.factories import FileFactory

pytestmark = pytest.mark.django_db


class TestFileEndpoint:
    def test_get_files(self, api_client: APIClient):
        FileFactory.create()
        url = reverse("swapi-file_list")
        response = api_client.get(url)
        files = response.json()
        assert isinstance(files, list)
        assert len(files) == 1
        response_file = files[0]
        db_file = File.objects.get(id=response_file["id"])
        assert response_file["filename"] == db_file.filename
        assert response_file["count_of_people"] == db_file.count_of_people
