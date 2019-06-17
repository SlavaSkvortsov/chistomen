from .models import Garbage, GarbageStatus
from rest_framework.response import Response
from rest_framework import status

def check_permission(*args, **kwargs):
    """
    kwarg - status_editing. When true, then operation of changing status. It is disable one of
    Check permission to edit garbage
    Decorator, which can work with or without args.
    """
    class Decorator(object):
        status_editing = False
        func = None

        def wrapper(self, view_self, request, pk, *args, **kwargs):
            try:
                garbage = Garbage.objects.get(pk=pk)
            except Garbage.DoesNotExist:
                return Response(dict(message='Cant find garbage with id={}'.format(pk)), status=status.HTTP_404_NOT_FOUND)

            request.garbage = garbage
            if garbage.status in GarbageStatus.INTERMEDIATE_STATUSES and garbage.owner != request.user and not request.user.is_staff:
                return Response(
                    dict(message='Permission denied! You cant edit this garbage!', status=status.HTTP_403_FORBIDDEN))
            # if not self.status_editing:
            #     if garbage.status in GarbageStatus.FINAL_STATUSES and not request.user.is_staff:
            #         return Response(dict(message='Incorrect status for editing garbage! '
            #                                      'You should change status to some of intermediate status first',
            #                              status=status.HTTP_403_FORBIDDEN))

            return self.func(view_self, request, pk, *args, **kwargs)

        def double_wrap(self, income_func):
            self.func = income_func
            return self.wrapper

    decorator = Decorator()
    if len(args) == 1 and len(kwargs) == 0 and callable(args[0]):
        # it is called without args
        decorator.func = args[0]
        return decorator.wrapper
    else:
        decorator.status_editing = kwargs['status_editing']
        return decorator.double_wrap


def authorization(view_func):
    def _decorator(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return Response(dict(message='Authorization failed!'), status=status.HTTP_401_UNAUTHORIZED)
        return view_func(self, request, *args, **kwargs)
    return _decorator