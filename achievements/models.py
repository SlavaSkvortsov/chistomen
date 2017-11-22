from django.db import models
from django.conf import settings


try:
    user_model = getattr(settings, 'ACHIEVEMENTS_USER_MODEL', getattr(settings, 'AUTH_USER_MODEL', None))
    exec('from {} import {} as User'.format('.'.join(user_model.split('.')[:-1]), user_model.split('.')[-1]))
except ImportError:
    from django.contrib.auth.models import User


class AchieveType(models.Model):
    code = models.CharField(max_length=30)
    name = models.CharField(max_length=100)

    def __str__(self):
        return '{}, {}'.format(self.code, self.name)

class Achievement(models.Model):
    achieve_type = models.ForeignKey(AchieveType)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300)
    order = models.SmallIntegerField()
    enable = models.BooleanField(default=True)

    class Meta:
        unique_together = (('achieve_type', 'order'),)


class Attribute(models.Model):
    attribute = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=200)


class AchieveCondition(models.Model):
    MORE = 0
    LESS = 1
    EQUAL = 2
    NOT_EQUAL = 3

    CONDITIONS = {
        MORE: '>',
        LESS: '<',
        EQUAL: '=',
        NOT_EQUAL: '!='
    }

    achievement = models.ForeignKey(Achievement, related_name='conditions')
    attribute = models.ForeignKey(Attribute)
    condition = models.SmallIntegerField(choices=CONDITIONS.items())
    value = models.IntegerField()

    def check_condition(self, user_value):
        if self.condition == self.MORE:
            return user_value > self.value
        elif self.condition == self.LESS:
            return user_value < self.value
        elif self.condition == self.EQUAL:
            return user_value == self.value
        elif self.condition == self.NOT_EQUAL:
            return user_value != self.value


class ReceivedAchievements(models.Model):
    user = models.ForeignKey(User)
    achievement = models.ForeignKey(Achievement, related_name='received')
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'achievement'),)
