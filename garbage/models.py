from django.db import models
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
        STATUS_CLEANED: 'Cleaned, not took out',
        STATUS_TAKING_OUT: 'Taking out',
        STATUS_COMPLETE: 'Complete',
    }


class Garbage(models):
    SIZE_SMALL = 0
    SIZE_MEDIUM = 1
    SIZE_LARGE = 2

    SIZES = {
        SIZE_SMALL: 'Small',
        SIZE_MEDIUM: 'Medium',
        SIZE_LARGE: 'Large',
    }

    lat = models.DecimalField('Latitude', max_digits=10, decimal_places=8)
    lng = models.DecimalField('Longitude', max_digits=11, decimal_places=8)
    size = models.SmallIntegerField('Size', choices=SIZES)
    solo_point = models.BooleanField('Point for one person', default=True)
    status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    founder = models.ForeignKey(User, 'Found by')
    cleaner = models.ForeignKey(User, 'Cleaned by', null=True, blank=True)
    took_out_by = models.ForeignKey(User, 'Took out by', null=True, blank=True)


class GarbageImage(models):
    garbage = models.ForeignKey(Garbage, 'Garbage', on_delete=models.CASCADE)
    photo = models.CharField('Link on photo')
    garbage_status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    added_by = models.ForeignKey(User, 'Photo adder')
