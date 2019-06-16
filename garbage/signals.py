from django.db.models.signals import post_save, post_delete, pre_delete
from django.dispatch import receiver

from garbage.models import Garbage
from garbage.mongo import MongoGarbagePoint


@receiver(post_save, sender=Garbage)
def sync_with_mongo(sender, instance: Garbage, **kwargs):
    MongoGarbagePoint.objects.filter(garbage_ptr=instance.pk).delete()
    MongoGarbagePoint.objects.create(
        garbage_ptr=instance.pk,
        point=[float(instance.lng), float(instance.lat)]
    )


@receiver(pre_delete, sender=Garbage)
def sync_with_mongo_delete(sender, instance: Garbage, **kwargs):
    MongoGarbagePoint.objects.filter(garbage_ptr=instance.pk).delete()
