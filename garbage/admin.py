from django.contrib import admin

# Register your models here.
from garbage.models import Garbage


@admin.register(Garbage)
class GarbageAdmin(admin.ModelAdmin):
    pass
