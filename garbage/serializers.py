from rest_framework import serializers
from garbage.models import Garbage, GarbageImage, GarbageStatus
import json


class GarbageBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garbage
        fields = '__all__'

    def create(self, validated_data):
        photos = validated_data.pop('photo')
        garbage = Garbage(status=GarbageStatus.STATUS_DIRTY, **validated_data)
        garbage.save()
        for photo in photos:
            image = GarbageImage(photo=photo, garbage_status=GarbageStatus.STATUS_DIRTY, garbage=garbage)
            image.save()
        return garbage

    def update(self, garbage, validated_data):
        if 'photo' in validated_data:
            for photo in GarbageImage.objects.filter(garbage=garbage, garbage_status=GarbageStatus.STATUS_DIRTY):
                photo.delete()
    
            for photo in validated_data.pop('photo'):
                image = GarbageImage(photo=photo, garbage_status=GarbageStatus.STATUS_DIRTY, garbage=garbage)
                image.save()

        for key, value in validated_data.items():
            setattr(garbage, key, value)
        garbage.save()
        return garbage


class GarbageSerializer(GarbageBaseSerializer):
    photo = serializers.ListField(child=serializers.CharField())
    solo_point = serializers.NullBooleanField(required=False)

    class Meta:
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photo',)


class GarbageShowSerializer(GarbageBaseSerializer):
    photo = serializers.SerializerMethodField()

    def get_photo(self, garbage):
        photos = list()
        for photo in garbage.photos.all():
            photos.append(dict(id=photo.id, photo=photo.photo))
        return photos


class PhotoSerializer(serializers.ModelSerializer):
    garbage_status = serializers.ChoiceField(choices=GarbageStatus.STATUSES.items(), required=False)

    def create(self, validated_data):
        if validated_data.get('garbage_status', None):
            garbage_status = validated_data['garbage_status']
        else:
            garbage_status = validated_data['garbage'].status

        photo = GarbageImage(photo=validated_data['photo'], garbage_status=garbage_status)
        photo.save()
        return photo

    class Meta:
        model = GarbageImage
        fields = ('id', 'photo', 'garbage_status',)