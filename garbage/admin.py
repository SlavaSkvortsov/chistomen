from django.contrib import admin

# Register your models here.
from garbage.models import Garbage, GarbageImage


class GarbageGarbageImageInline(admin.TabularInline):
    model = GarbageImage
    extra = 0


@admin.register(Garbage)
class GarbageAdmin(admin.ModelAdmin):
    list_display = ['status', 'size', 'lat', 'lng']
    inlines = [GarbageGarbageImageInline]
