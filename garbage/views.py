from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import (
    GarbageSerializer, GarbageSearchSerializer, PhotoSerializer, DescriptionSerializer,
    GarbageShowSerializer, ChangeStatusSerializer
)

from rest_framework.authentication import TokenAuthentication
import logging
from .models import Garbage, GarbageImage, GarbageException, GarbageDescription
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from django.db import connection
from .decorators import check_permission, authorization
logger = logging.getLogger(__name__)


class GarbageView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """
        Getting list of garbages by filter params
        This method uses without identification - everyone can call it
        """
        serializer = GarbageSearchSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        flt = dict()

        if connection.vendor == 'mysql':
            # Looking for points in radius does not working on MySQL
            pass
        else:
            if 'lng' in serializer.data and 'lat' in serializer.data and 'radius' in serializer.data:
                point = Point((float(serializer.data['lng']), float(serializer.data['lat'])))
                flt['location__distance_lte'] = (point, Distance(km=float(serializer.data['radius'])))
        for var in ('size', 'status'):
            if var in serializer.data:
                value = serializer.data[var].split(',')
                flt['{}__in'.format(var)] = value
        garbages = Garbage.objects.filter(**flt)


        # TODO Захуярь вывод через сериалайзер, идиот
        result = [dict(id=garbage.id, lng=garbage.location.x, lat=garbage.location.y, size=garbage.size, status=garbage.status) for garbage in garbages]
        if result:
            return Response(result)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @authorization
    def post(self, request):
        """
        Adding a new garbage to db
        """
        serializer = GarbageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        garbage = serializer.save(user=request.user)
        return Response(dict(id=garbage.pk), status=status.HTTP_201_CREATED)


class GarbageDetail(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request, pk):
        """
        Getting existing garbage
        This method uses without identification - everyone can call it
        """
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

        serializer = GarbageShowSerializer(garbage)
        return Response(serializer.data)

    @authorization
    @check_permission
    def patch(self, request, pk):
        """
        Editing existing garbage
        """
        serializer = GarbageSerializer(request.garbage, data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(status=status.HTTP_200_OK)


class GarbagePhoto(APIView):
    authentication_classes = [TokenAuthentication]

    @authorization
    @check_permission
    def post(self, request, pk):
        """
        Adding a new photo to garbage
        """
        serializer = PhotoSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        photo = serializer.save(garbage=request.garbage)
        return Response(dict(id=photo.id), status=status.HTTP_201_CREATED)


class DelPhoto(APIView):
    authentication_classes = [TokenAuthentication]

    @authorization
    @check_permission
    def delete(self, request, pk_garbage, pk_photo):
        """
        Deleting photo
        """
        try:
            photo = GarbageImage.objects.get(pk=pk_photo, garbage=request.garbage)
        except GarbageImage.DoesNotExist:
            return Response(dict(message='Cant find photo with id={}'.format(pk_photo)), status=status.HTTP_404_NOT_FOUND)

        photo.delete()
        return Response(status=status.HTTP_200_OK)


class GarbageDescriptionView(APIView):
    authentication_classes = [TokenAuthentication]

    @authorization
    @check_permission
    def post(self, request, pk):
        """
        Adding a new description to garbage
        """
        serializer = DescriptionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        description = serializer.save(garbage=request.garbage)
        return Response(dict(id=description.id), status=status.HTTP_201_CREATED)


class DelDescription(APIView):
    authentication_classes = [TokenAuthentication]

    @authorization
    @check_permission
    def delete(self, request, pk_garbage, pk_description):
        """
        Deleting photo
        """
        try:
            description = GarbageDescription.objects.get(pk=pk_description, garbage=request.garbage)
        except GarbageDescription.DoesNotExist:
            return Response(dict(message='Cant find photo with id={}'.format(pk_description)), status=status.HTTP_404_NOT_FOUND)

        description.delete()
        return Response(status=status.HTTP_200_OK)


class ChangeStatus(APIView):
    authentication_classes = [TokenAuthentication]

    @authorization
    @check_permission(status_editing=True)
    def post(self, request, pk):
        """
        Changing status to new one
        """
        serializer = ChangeStatusSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            request.garbage.change_status(serializer.validated_data['status'], request.user)
        except GarbageException:
            return Response(data=GarbageException.data, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)
