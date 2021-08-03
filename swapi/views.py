from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class View(APIView):
    def get(self, request, *args, **kwargs):
        return Response("Hello world", status=status.HTTP_201_CREATED)