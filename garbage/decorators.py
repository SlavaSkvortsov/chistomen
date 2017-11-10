from .models import Garbage, GarbageStatus
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication


def check_permission(view_func):
    def _decorator(self, request, pk, *args, **kwargs):
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

        request.garbage = garbage
        if garbage.status in GarbageStatus.INTERMEDIATE_STATUSES and garbage.owner != request.user and not request.user.is_stuff:
            return Response(dict(message='Permission denied! You cant edit this garbage!', status=status.HTTP_403_FORBIDDEN))
        if garbage.status in GarbageStatus.FINAL_STATUSES and not request.user.is_stuff:
            return Response(dict(message='Incorrect status for editing garbage! '
                                         'You should change status to some of intermediate status first', status=status.HTTP_403_FORBIDDEN))
        return view_func(self, request, pk, *args, **kwargs)
    return _decorator


def authorization(view_func):
    def _decorator(self, request, *args, **kwargs):
        if request.user.is_anonymous():
            return Response(dict(message='Authorization failed!'), status=status.HTTP_401_UNAUTHORIZED)
        return view_func(self, request, *args, **kwargs)
    return _decorator