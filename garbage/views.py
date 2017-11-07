from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GarbageCreateSerializer, GarbageUpdateSerializer, GarbageSearchSerializer, PhotoSerializer, GarbageShowSerializer

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import authentication_classes
import logging
from .models import Garbage, GarbageImage, GarbageException
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from .decorators import check_permission
logger = logging.getLogger(__name__)

class GarbageView(APIView):
    def get(self, request):
        """
        Getting list of garbages by filter params
        This method uses without identification - everyone can call it
        """
        serializer = GarbageSearchSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        flt = dict()

        if 'lng' in serializer.data and 'lat' in serializer.data and 'radius' in serializer.data:
            point = Point((float(serializer.data['lng']), float(serializer.data['lat'])))
            flt.update(dict(location__distance_lte=(point, Distance(km=float(serializer.data['radius'])))))
        for var in ('size', 'status'):
            if var in serializer.data:
                value = serializer.data[var]
                if not isinstance(value, list):
                    value = [value]
                flt.update({'{}__in'.format(var): value})
        garbages = Garbage.objects.filter(**flt)

        result = [dict(id=garbage.id, lng=garbage.location.x, lat=garbage.location.y, size=garbage.size, status=garbage.status) for garbage in garbages]
        if result:
            return Response(result)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @authentication_classes([TokenAuthentication])
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
        Getting existing garbage
        This method uses without identification - everyone can call it
        """
        serializer = GarbageShowSerializer(request.garbage)
        return Response(serializer.data)

    @check_permission
    @authentication_classes([TokenAuthentication])
    def patch(self, request, pk):
        """
        Editing existing garbage
        """
        serializer = GarbageUpdateSerializer(request.garbage, data=request.POST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if 'status' in serializer.validated_data:
            try:
                request.garbage.change_status(serializer.validated_data['status'], request.user)
            except GarbageException:
                return Response(data=GarbageException.data, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()

        return Response(status=status.HTTP_200_OK)


class GarbagePhoto(APIView):
    authentication_classes = [TokenAuthentication]

    @check_permission
    def post(self, request, pk):
        """
        Adding a new photo to garbage
        """
        serializer = PhotoSerializer(data=request.POST)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        photo = serializer.save(garbage=request.garbage)
        return Response(dict(id=photo.id), status=status.HTTP_201_CREATED)


class DelPhoto(APIView):
    authentication_classes = [TokenAuthentication]

    @check_permission
    def delete(self, request, pk_garbage, pk_photo):
        """
        Deleting photo
        """
        try:
            photo = GarbageImage.objects.get(pk=pk_garbage, garbage=request.garbage)
        except GarbageImage.DoesNotExist:
            return Response(dict(message='Cant find photo with id={}'.format(pk_photo)), status=status.HTTP_404_NOT_FOUND)

        photo.delete()
        return Response(status=status.HTTP_200_OK)


