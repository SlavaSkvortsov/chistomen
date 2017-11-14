from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class GarbageException(Exception):
    data = None

    def __init__(self, data):
        self.data = data


class GarbageStatus(object):
    STATUS_PREPARING = 0
    STATUS_DIRTY = 1
    STATUS_IN_CLEANING = 2
    STATUS_CLEANED = 3
    STATUS_TAKING_OUT = 4
    STATUS_COMPLETE = 5

    STATUSES = {
        STATUS_PREPARING: 'Preparing',
        STATUS_DIRTY: 'Not cleaned',
        STATUS_IN_CLEANING: 'In cleaning',
        STATUS_CLEANED: 'Cleaned, not taken out',
        STATUS_TAKING_OUT: 'Taking out',
        STATUS_COMPLETE: 'Complete',
    }

    AVAILABLE_STATUS_CHANGE = {
        STATUS_PREPARING: [STATUS_PREPARING, STATUS_DIRTY],
        STATUS_DIRTY: [STATUS_DIRTY, STATUS_IN_CLEANING],
        STATUS_IN_CLEANING: [STATUS_IN_CLEANING, STATUS_DIRTY, STATUS_CLEANED],
        STATUS_CLEANED: [STATUS_CLEANED, STATUS_TAKING_OUT],
        STATUS_TAKING_OUT: [STATUS_TAKING_OUT, STATUS_CLEANED, STATUS_COMPLETE],
        STATUS_COMPLETE: [STATUS_COMPLETE, STATUS_TAKING_OUT],
    }

    INTERMEDIATE_STATUSES = [STATUS_PREPARING, STATUS_IN_CLEANING, STATUS_TAKING_OUT]
    FINAL_STATUSES = [STATUS_DIRTY, STATUS_CLEANED, STATUS_COMPLETE]


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
    status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())  # Denormalization

    def change_status(self, new_status, user):
        if new_status not in GarbageStatus.AVAILABLE_STATUS_CHANGE[self.status]:
            raise GarbageException(data=dict(status=['Incorrect status for changing. You cant change status from #{} to #{}'.format(self.status, new_status)]))
        if new_status in GarbageStatus.INTERMEDIATE_STATUSES and not user.is_staff and self.owner != user:
            raise GarbageException(data=['Access denied. This garbage is using by another user'])

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])
            status_changing = StatusChanging(garbage=self, changer=user, status=new_status)
            status_changing.save()

    @property
    def owner(self):
        return self.status_obj.changer

    @property
    def status_obj(self):
        return StatusChanging.objects.filter(garbage=self).order_by('-date')[0]


class StatusChanging(models.Model):
    garbage = models.ForeignKey(Garbage, related_name='statuses', null=True)
    changer = models.ForeignKey(User)
    status = models.SmallIntegerField(choices=GarbageStatus.STATUSES.items())
    date = models.DateTimeField(auto_now_add=True)


class GarbageImage(models.Model):
    garbage = models.ForeignKey(Garbage, related_name='photos', null=True)
    photo = models.CharField('Link on photo', max_length=300)
    garbage_status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    added_by = models.ForeignKey(User, null=True, blank=True)


class GarbageDescription(models.Model):
    garbage = models.ForeignKey(Garbage, related_name='descriptions')
    description = models.CharField('Description', max_length=1000)
    garbage_status = models.SmallIntegerField('Status', choices=GarbageStatus.STATUSES.items())
    added_by = models.ForeignKey(User, null=True, blank=True)