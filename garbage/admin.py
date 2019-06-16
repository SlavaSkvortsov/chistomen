from django.contrib import admin

# Register your models here.
from garbage.models import Garbage, GarbageImage, GarbageDescription, StatusChanging, MediaObject


class GarbageGarbageImageInline(admin.TabularInline):
    model = GarbageImage
    extra = 0


class GarbageDescriptionInline(admin.TabularInline):
    model = GarbageDescription
    extra = 0


class StatusChangingInline(admin.TabularInline):
    model = StatusChanging
    extra = 0


@admin.register(Garbage)
class GarbageAdmin(admin.ModelAdmin):
    list_display = ['pk', 'status', 'size', 'lat', 'lng']
    inlines = [GarbageGarbageImageInline, StatusChangingInline, GarbageDescriptionInline]


@admin.register(MediaObject)
class MediaObjectAdmin(admin.ModelAdmin):
    list_display = ['pk', 'file', 'created']
