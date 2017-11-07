from .models import Garbage
from rest_framework.response import Response
from rest_framework import status


def check_permission(view_func):
    def _decorator(self, request, pk, *args, **kwargs):
        try:
            garbage = Garbage.objects.get(pk=pk)
        except Garbage.DoesNotExist:
            return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

        request.garbage = garbage

        if garbage.get_owner_by_status() != request.user and not request.user.is_stuff():
            return Response(data='Permission denied! You cant edit this garbage!', status=status.HTTP_403_FORBIDDEN)
        return view_func(self, request, pk)
    return _decorator