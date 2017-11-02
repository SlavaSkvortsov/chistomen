from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GarbageCreateSerializer, GarbageUpdateSerializer, GarbageSearchSerializer, PhotoSerializer, GarbageShowSerializer

from rest_framework.authentication import TokenAuthentication
import logging
from .models import Garbage, GarbageImage
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
logger = logging.getLogger(__name__)

class GarbageView(APIView):
    #authentication_classes = (TokenAuthentication,)

    def get(self, request):
        serializer = GarbageSearchSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print((serializer.data['lng'], serializer.data['lat']))
        point = Point((float(serializer.data['lng']), float(serializer.data['lat'])))
        garbages = Garbage.objects.filter(location__distance_lte=(point, Distance(km=serializer.data['radius'])))
        for garbage in garbages:
            print(garbage)

        return Response()
        result = [dict(id=garbage.id, location=garbage.location, size=garbage.size, status=garbage.status) for garbage in garbages]
        return Response(result)

    def post(self, request):
        """
        Adding a new garbage to db
        """
        serializer = GarbageCreateSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        garbage = serializer.save()
        return Response(dict(id=garbage.pk), status=status.HTTP_201_CREATED)


class GarbageDetail(APIView):
    def get(self, request, pk):
        """
        getting existing garbage
        """
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)
        serializer = GarbageShowSerializer(garbage)
        return Response(serializer.data)

    def patch(self, request, pk):
        """
        Editing existing garbage
        """
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

        serializer = GarbageUpdateSerializer(garbage, data=request.POST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        return Response(status=status.HTTP_200_OK)


class GarbagePhoto(APIView):
    def post(self, request, pk):
        """
        Adding a new photo to garbage
        """
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

        serializer = PhotoSerializer(data=request.POST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        photo = serializer.save(garbage=garbage)
        return Response(dict(id=photo.id), status=status.HTTP_201_CREATED)


class DelPhoto(APIView):
    def delete(self, request, pk_garbage, pk_photo):
        """
        Deleting photo
        """
        try:
            garbage = Garbage.objects.get(pk=pk_garbage)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk_garbage)), status=status.HTTP_404_NOT_FOUND)

        try:
            photo = GarbageImage.objects.get(pk=pk_garbage, garbage=garbage)
        except GarbageImage.DoesNotExist:
            return Response(dict(message='Cant find photo with id={}'.format(pk_photo)), status=status.HTTP_404_NOT_FOUND)

        photo.delete()
        return Response(status=status.HTTP_200_OK)


