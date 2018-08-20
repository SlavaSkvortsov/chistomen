from rest_framework import serializers
from garbage.models import Garbage, GarbageImage, GarbageStatus, GarbageDescription, StatusChanging
from django.contrib.gis.geos import Point
from django.db import connection


class GarbageSerializer(serializers.ModelSerializer):
    photos = serializers.ListField(child=serializers.CharField(), required=False)
    solo_point = serializers.NullBooleanField(required=False)
    lat = serializers.DecimalField(max_digits=10, decimal_places=8, required=False)
    lng = serializers.DecimalField(max_digits=11, decimal_places=8, required=False)

    class Meta:
        model = Garbage
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photos',)

    def create(self, validated_data):
        photos = validated_data.pop('photos')
        location = Point((validated_data.pop('lng'), validated_data.pop('lat')))
        user = validated_data.pop('user')
        garbage = Garbage(status=GarbageStatus.STATUS_PREPARING, location=location, **validated_data)
        garbage.save()
        for photo in photos:
            image = GarbageImage(photo=photo, garbage_status=GarbageStatus.STATUS_PREPARING, garbage=garbage)
            image.save()

        status_change = StatusChanging(garbage=garbage, changer=user, status=GarbageStatus.STATUS_PREPARING)
        status_change.save()

        return garbage

    def update(self, garbage, validated_data):
        if 'lat' in validated_data and 'lng' in validated_data:
            garbage.location = Point((validated_data.pop('lng'), validated_data.pop('lat')))
        if 'photo' in validated_data:
            for photo in GarbageImage.objects.filter(garbage=garbage, garbage_status=garbage.status):
                photo.delete()

            for photo in validated_data.pop('photo'):
                image = GarbageImage(photo=photo, garbage=garbage,
                                     garbage_status=validated_data.get('status', None) if validated_data.get('status', None) else garbage.status)
                image.save()

        for key, value in validated_data.items():
            setattr(garbage, key, value)
        garbage.save()
        return garbage


class GarbageSearchSerializer(GarbageSerializer):
    radius = serializers.DecimalField(max_digits=8, decimal_places=3, required=False)
    status = serializers.CharField(required=False)
    size = serializers.CharField(required=False)

    class Meta:
        fields = ('id', 'lat', 'lng', 'size', 'solo_point', 'photo', 'radius', 'status')
        model = Garbage


class GarbageShowSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    lat = serializers.SerializerMethodField()
    lng = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    status_history = serializers.SerializerMethodField()

    def get_photo(self, garbage):
        photos = list()
        for photo in garbage.photos.all():
            photos.append(dict(id=photo.id, photo=photo.photo, status=photo.garbage_status))
        return photos

    def get_lng(self, garbage):
        return garbage.location.x

    def get_lat(self, garbage):
        return garbage.location.y

    def get_status(self, garbage):
        return garbage.status

    def get_description(self, garbage):
        return [dict(id=desc.id, description=desc.description, status=desc.garbage_status) for desc in garbage.descriptions.all()]

    def get_status_history(self, garbage):
        if connection.vendor == 'mysql':
            return ['Give me back my oracle plz... P.S. Does not support on MySQL. ']
        else:
            statuses = StatusChanging.objects.raw(
                ' select t.* '
                '   from garbage_statuschanging t '
                '       ,(select tt.id '
                '               ,row_number() over(partition by tt.status order by date desc) as rownum '
                '           from (select distinct t.status '
                '                   from garbage_statuschanging t '
                '                  where t.garbage_id = {}) a '
                '                       ,garbage_statuschanging tt '
                '          where a.status = tt.status) a '
                '   where t.id = a.id '
                '     and a.rownum = 1 '.format(garbage.id))
        return [dict(status=status.status, user=status.changer.id, date=status.date) for status in statuses]

    class Meta:
        model = Garbage
        fields = ('lat', 'lng', 'size', 'solo_point', 'photo', 'status', 'description', 'status_history')


class PhotoSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        photo = GarbageImage(photo=validated_data['photo'], garbage_status=validated_data['garbage'].status, garbage=validated_data['garbage'])
        photo.save()
        return photo

    class Meta:
        model = GarbageImage
        fields = ('photo',)


class DescriptionSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        # Deleting the old one description
        try:
            description = GarbageDescription.objects.get(garbage=validated_data['garbage'], garbage_status=validated_data['garbage'].status)
            description.delete()
        except GarbageDescription.DoesNotExist:
            pass
        description = GarbageDescription(garbage=validated_data['garbage'], description=validated_data['description'], garbage_status=validated_data['garbage'].status)
        description.save()
        return description

    class Meta:
        model = GarbageDescription
        fields = ('description',)


class ChangeStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusChanging
        fields = ('status',)
