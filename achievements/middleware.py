from .models import Achievement, AchieveType, ReceivedAchievements
from django.conf import settings


class AchievementMiddleware(object):
    attributes = None

    def __init__(self, get_response):
        self.get_response = get_response
        self.attributes = {}

    def __call__(self, request):
        added_achieves = []
        if not request.user.is_anonymous():
            for achieve_type in AchieveType.objects.all():
                for achieve in Achievement.objects.filter(achieve_type=achieve_type, enable=True).exclude(received__user=request.user).order_by('order'):
                    add_achieve = True
                    for condition in achieve.conditions:
                        if not condition.check_condition(self.get_attr(request.user, condition.attribute)):
                            add_achieve = False
                            break
                    if add_achieve:
                        received_achieve = ReceivedAchievements(user=request.user, achievement=achieve)
                        received_achieve.save()
                        if settings.ACHIEVEMENTS_ADD_IN_RESPONSE:
                            added_achieves.append(achieve)
                    else:
                        break
        response = self.get_response(request)
        if settings.ACHIEVEMENTS_ADD_IN_RESPONSE:
            response.data.update({
                'added_achieves': self.achieves_to_dict(added_achieves)
            })
        return response

    def achieves_to_dict(self, achieves):
        return [dict(id=achieve.pk, name=achieve.name, description=achieve.description) for achieve in achieves]

    def get_attr(self, user, attr):
        """
        Caching attributes
        """
        result = getattr(self.attributes, attr, None)
        if result:
            return result
        result = getattr(user, attr, None)
        self.attributes.update({attr, result})
        return result