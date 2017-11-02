from rest_framework import serializers
from garbage.models import Garbage, GarbageImage, GarbageStatus
from django.contrib.gis.geos import Point


class GarbageUpdateSerializer(serializers.ModelSerializer):
    photo = serializers.ListField(child=serializers.CharField(), required=False)
    solo_point = serializers.NullBooleanField(required=False)
    lat = serializers.DecimalField(max_digits=10, decimal_places=8, required=False)
    lng = serializers.DecimalField(max_digits=11, decimal_places=8, required=False)

    class Meta:
        model = Garbage
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photo',)

    def update(self, garbage, validated_data):
        if 'lat' in validated_data and 'lng' in validated_data:
            garbage.location = Point((validated_data.pop('lng'), validated_data.pop('lat')))
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


class GarbageCreateSerializer(serializers.ModelSerializer):
    photo = serializers.ListField(child=serializers.CharField(), required=False)
    solo_point = serializers.NullBooleanField(required=False)
    lat = serializers.DecimalField(max_digits=10, decimal_places=8, required=True)
    lng = serializers.DecimalField(max_digits=11, decimal_places=8, required=True)

    class Meta:
        model = Garbage
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photo',)

    def create(self, validated_data):
        photos = validated_data.pop('photo')
        location = Point((validated_data.pop('lng'), validated_data.pop('lat')))
        garbage = Garbage(status=GarbageStatus.STATUS_DIRTY, location=location, **validated_data)
        garbage.save()
        for photo in photos:
            image = GarbageImage(photo=photo, garbage_status=GarbageStatus.STATUS_DIRTY, garbage=garbage)
            image.save()
        return garbage


class GarbageSearchSerializer(GarbageCreateSerializer):
    radius = serializers.DecimalField(max_digits=8, decimal_places=3, required=True)

    class Meta:
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photo', 'radius',)
        model = Garbage


class GarbageShowSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()

    def get_photo(self, garbage):
        photos = list()
        for photo in garbage.photos.all():
            photos.append(dict(id=photo.id, photo=photo.photo))
        return photos

    class Meta:
        model = Garbage
        fields = '__all__'

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