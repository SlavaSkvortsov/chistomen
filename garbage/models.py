from django.contrib.gis.db import models
from django.contrib.auth.models import User


class GarbageException(Exception):
    data = None

    def __init__(self, data):
        self.data = data

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

    AVAILABLE_STATUS_CHANGE = {
        STATUS_DIRTY: [STATUS_DIRTY, STATUS_IN_CLEANING],
        STATUS_IN_CLEANING: [STATUS_IN_CLEANING, STATUS_DIRTY, STATUS_CLEANED],
        STATUS_CLEANED: [STATUS_CLEANED, STATUS_IN_CLEANING, STATUS_TAKING_OUT],
        STATUS_TAKING_OUT: [STATUS_TAKING_OUT, STATUS_CLEANED, STATUS_COMPLETE],
        STATUS_COMPLETE: [STATUS_COMPLETE, STATUS_TAKING_OUT],
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

    location = models.PointField(geography=True)
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

    def change_status(self, status, user):
        if status not in GarbageStatus.AVAILABLE_STATUS_CHANGE[self.status]:
            raise GarbageException(data=dict(status=['Incorrect status for changing. You cant change status from #{} to #{}'.format(self.status, status)]))
        update_fields = ['status']
        if status != self.status:

            if self.status == GarbageStatus.STATUS_IN_CLEANING and status == GarbageStatus.STATUS_CLEANED:
                self.cleaner = user
                update_fields.append('cleaner')
            elif self.status == GarbageStatus.STATUS_TAKING_OUT and status == GarbageStatus.STATUS_COMPLETE:
                self.took_out_by = user
                update_fields.append('took_out_by')
        self.status = status
        self.save(update_fields=update_fields)

    def get_owner_by_status(self):
        if self.status == GarbageStatus.STATUS_DIRTY:
            return self.founder
        elif self.status == GarbageStatus.STATUS_CLEANED:
            return self.cleaner
        elif self.status == GarbageStatus.STATUS_COMPLETE:
            return self.took_out_by

class GarbageImage(models.Model):
    garbage = models.ForeignKey(Garbage, related_name='photos', null=True)
    photo = models.CharField('Link on photo', max_length=300)
    garbage_status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    added_by = models.ForeignKey(User, null=True, blank=True)

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'added_by', None) is None:
            obj.added_by = request.user
        super().save_model(request, obj, form, change)
