from rest_framework import serializers

from core.models import Label, Dataset, Csvfile, Image
from label.serializers import LabelSerializer


class CsvfileSerializer(serializers.ModelSerializer):
    """Serializer for csvfile objects"""

    class Meta:
        model = Csvfile
        fields = ('id',
                  'name',
                  'description',
                  'labelcol',
                  'imgcolstart',
                  'imgcolend',
                  'file'
                  )
        read_only_fields = ('id', 'file',)


class CsvfileFileSerializer(serializers.ModelSerializer):
    """Serializer for uploading csv to csvfile"""

    class Meta:
        model = Csvfile
        fields = ('id', 'name', 'file', 'labelcol', 'imgcolstart', 'imgcolend')
        read_only_fields = ('id',
                            'name',
                            'labelcol',
                            'imgcolstart',
                            'imgcolend'
                            )


class DatasetSerializer(serializers.ModelSerializer):
    """Serializer for dataset objects"""
    labels = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Label.objects.all()
    )
    csvfiles = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Csvfile.objects.all()
    )

    class Meta:
        model = Dataset
        fields = ('id', 'name', 'description', 'labels', 'csvfiles')
        read_only_fields = ('id',)


class DatasetDetailSerializer(DatasetSerializer):
    """Serialize a dataset detail"""
    csvfiles = CsvfileSerializer(read_only=True)
    labels = LabelSerializer(read_only=True)


class ImageSerializer(serializers.ModelSerializer):
    """Serialize an image"""
    class Meta:
        model = Image
        fields = (
            'id', 'name', 'csvfile', 'row', 'label', 'image', 'img_array'
        )
        read_only_fields = ('id',
                            'name',
                            'csvfile',
                            'row',
                            'label',
                            'image',
                            'img_array')


class ImageDetailSerializer(ImageSerializer):
    """Serialize an image detail"""
    csvfile = CsvfileSerializer(read_only=True)
    label = LabelSerializer(read_only=True)
