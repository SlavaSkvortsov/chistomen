from django.contrib import admin
from .models import AchieveType, Achievement, AchieveCondition, ReceivedAchievements


class AchieveTypeAdmin(admin.ModelAdmin):
    model = AchieveType
    list_display = ['code', 'name']


class AchieveConditionAdmin(admin.StackedInline):
    model = AchieveCondition
    list_display = ['achievement', 'attribute', 'condition', 'value']


class AchievementAdmin(admin.ModelAdmin):
    model = Achievement
    list_display = ['achieve_type', 'name', 'description', 'order', 'enable']
    inlines = [AchieveConditionAdmin]


admin.site.register(AchieveType, AchieveTypeAdmin)
admin.site.register(Achievement, AchievementAdmin)
