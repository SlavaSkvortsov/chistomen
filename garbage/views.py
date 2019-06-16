import logging

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from garbage.mongo import MongoGarbagePoint
from .decorators import check_permission, authorization
from .models import Garbage, GarbageImage, GarbageException, GarbageDescription
from .serializers import (
    GarbageSerializer, PhotoSerializer, DescriptionSerializer,
    GarbageShowSerializer, ChangeStatusSerializer,
    MediaObjectSerializer)

logger = logging.getLogger(__name__)


class GarbageView(APIView):
    authentication_classes = [TokenAuthentication]

    def get(self, request):
        """
        Getting list of garbages by filter params
        This method uses without identification - everyone can call it
        """

        lng = request.query_params.get('lng', None)
        lat = request.query_params.get('lat', None)
        radius = request.query_params.get('radius', None)

        if lng and lat:
            try:
                lng = float(lng)
            except TypeError:
                raise ValidationError({
                    'lng': "param is invalid"
                })

            try:
                lat = float(lat)
            except TypeError:
                raise ValidationError({
                    'lat': "param is invalid"
                })

            try:
                radius = float(radius)
            except TypeError:
                raise ValidationError({
                    'radius': "param is invalid"
                })

        flt = dict()
        raw_points = None
        if lng and lat and radius:
            raw_points = MongoGarbagePoint.objects.filter(
                point__geo_within_sphere=[(lng, lat), radius / (6371 * 1000)]
            )

        for var in ('size', 'status'):
            if var in request.query_params:
                value = request.query_params.get(var)
                value = value.split(',')
                flt['{}__in'.format(var)] = value

        if raw_points is not None:
            flt['pk__in'] = map(lambda x: x.garbage_ptr, raw_points)

        garbages = Garbage.objects.filter(**flt)

        result = GarbageShowSerializer(instance=garbages, many=True).data
        return Response(data=result)

    @authorization
    def post(self, request):
        """
        Adding a new garbage to db
        """
        serializer = GarbageSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        garbage = serializer.save(user=request.user)
        return Response(GarbageShowSerializer(instance=garbage).data, status=status.HTTP_201_CREATED)


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

        return Response(GarbageShowSerializer(instance=serializer.instance).data, status=status.HTTP_200_OK)


class GarbagePhoto(APIView):
    authentication_classes = [TokenAuthentication]
    parser_class = (FileUploadParser,)

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
        GarbageImage.objects.filter(photo__pk=pk_photo, garbage=request.garbage).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


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
            return Response(dict(message='Cant find photo with id={}'.format(pk_description)),
                            status=status.HTTP_404_NOT_FOUND)

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


class MediaObjectAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    parser_class = (FileUploadParser,)

    @authorization
    def post(self, request):
        """
        Adding a new photo to garbage
        """
        serializer = MediaObjectSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        photo = serializer.save()
        return Response(dict(id=photo.id), status=status.HTTP_201_CREATED)
