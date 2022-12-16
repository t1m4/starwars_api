from factory import fuzzy
from factory.django import DjangoModelFactory

from swapi.models import File


class FileFactory(DjangoModelFactory):
    filename = fuzzy.FuzzyText(length=40)
    count_of_people = fuzzy.FuzzyInteger(0, 100)

    class Meta:
        model = File
