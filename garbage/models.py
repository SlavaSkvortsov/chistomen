#from django.db import models
from django.contrib.gis.db import models
from django.contrib.auth.models import User


class GarbageStatus(object):
    STATUS_DIRTY = 0
    STATUS_IN_CLEANING = 1
    STATUS_CLEANED = 2
    STATUS_TAKING_OUT = 3
    STATUS_COMPLETE = 4

    STATUSES = {
        STATUS_DIRTY: 'Not cleaned',
        STATUS_IN_CLEANING: 'In cleaning',
        STATUS_CLEANED: 'Cleaned, not taken out',
        STATUS_TAKING_OUT: 'Taking out',
        STATUS_COMPLETE: 'Complete',
    }


class Garbage(models.Model):
    SIZE_SMALL = 0
    SIZE_MEDIUM = 1
    SIZE_LARGE = 2

    SIZES = {
        SIZE_SMALL: 'Small',
        SIZE_MEDIUM: 'Medium',
        SIZE_LARGE: 'Large',
    }

    location = models.PointField()
    size = models.SmallIntegerField('Size', choices=SIZES.items(), default=SIZE_SMALL)
    solo_point = models.BooleanField('Point for one person', default=True)
    status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    founder = models.ForeignKey(User, null=True, blank=True, related_name='founders')
    cleaner = models.ForeignKey(User, null=True, blank=True, related_name='cleaners')
    took_out_by = models.ForeignKey(User, null=True, blank=True, related_name='took_out_by')

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'founder', None) is None:
            obj.founder = request.user
        super().save_model(request, obj, form, change)


class GarbageImage(models.Model):
    garbage = models.ForeignKey(Garbage, related_name='photos', null=True)
    photo = models.CharField('Link on photo', max_length=300)
    garbage_status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    added_by = models.ForeignKey(User, null=True, blank=True)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'added_by', None) is None:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
