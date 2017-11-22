from django.db import models
from django.contrib.auth.models import User
from garbage.models import GarbageStatus, StatusChanging


class CustomUser(models.Model):
    user = models.OneToOneField(User)

    @property
    def garbage_found(self):
        return len(StatusChanging.objects.filter(changer=self.user, status=GarbageStatus.STATUS_DIRTY))

    @property
    def garbage_cleaned(self):
        return len(StatusChanging.objects.filter(changer=self.user, status=GarbageStatus.STATUS_CLEANED))

    @property
    def garbage_took_out(self):
        return len(StatusChanging.objects.filter(changer=self.user, status=GarbageStatus.STATUS_COMPLETE))