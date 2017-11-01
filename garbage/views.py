from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import GarbageSerializer, PhotoSerializer, GarbageShowSerializer

from rest_framework.authentication import TokenAuthentication
import logging
from .models import Garbage, GarbageImage

logger = logging.getLogger(__name__)

class GarbageCreate(APIView):
    #authentication_classes = (TokenAuthentication,)

    def post(self, request):
        """
        Adding a new garbage to db
        """
        serializer = GarbageSerializer(data=request.POST)
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

        serializer = GarbageSerializer(garbage, data=request.POST)

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


