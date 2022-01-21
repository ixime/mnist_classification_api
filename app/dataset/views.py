import csv
import math
import io
import numpy as np
from PIL import Image as Img

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Label, Csvfile, Dataset, Image

from dataset import serializers


class BaseDatasetAttrViewSet(viewsets.GenericViewSet,
                             mixins.ListModelMixin,
                             mixins.CreateModelMixin):
    """Base viewset for user owned dataset attributes"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(dataset__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def perform_create(self, serializer):
        """Create a new object"""
        serializer.save(user=self.request.user)


class CsvfileViewSet(BaseDatasetAttrViewSet):
    """Manage csvfiles in the database"""
    queryset = Csvfile.objects.all()
    serializer_class = serializers.CsvfileSerializer

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'upload_csvfile':
            return serializers.CsvfileFileSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-csvfile')
    def upload_csvfile(self, request, pk=None):
        """Upload a csvfile to populate a dataset"""
        csvfilefile = self.get_object()
        serializer = self.get_serializer(
            csvfilefile,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            csvid = csvfilefile.id
            csvfile = Csvfile.objects.filter(id=csvid)
            user = csvfile[0].user
            file = csvfilefile.file
            labelcol = csvfilefile.labelcol
            start = csvfilefile.imgcolstart
            end = csvfilefile.imgcolend + 1
            size = int(math.sqrt(end-start))
            if size**2 != (end-start):
                raise ValueError('size is not valid!')
            csvf = file.open(mode='r')
            reader = csv.reader(csvf, delimiter=',')
            next(reader, None)  # skip the headers
            for i, row in enumerate(reader):
                label = Label.objects.filter(name=row[labelcol])
                if label is None:
                    raise ValueError('label is not valid!')
                img = np.array(row[start:end]).reshape(size, size)
                image = Img.fromarray(img.astype(np.uint8), 'L')
                img_array = img.astype(float)/255
                params = {
                          'name': f'{csvid}_{i}',
                          'csvfile': csvfile[0],
                          'row': i,
                          'label': label[0]
                          }
                newimg, _ = Image.objects.get_or_create(user=user, **params)
                fimg = io.BytesIO()
                image.save(fimg, 'bmp')
                newimg.image.save("image.bmp", fimg, save=True)
                fimg.close()
                fnp = io.BytesIO()
                np.save(fnp, img_array)
                newimg.img_array.save("image.npy", fnp, save=True)
                fimg.close()
                newimg.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
                )
            file.close()
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )


class DatasetViewSet(BaseDatasetAttrViewSet):
    """Manage datasets in the database"""
    queryset = Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.DatasetDetailSerializer

        return self.serializer_class


class ImageViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    """Manage images in the database"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    queryset = Image.objects.all()
    serializer_class = serializers.ImageSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(dataset__isnull=False)

        return queryset.filter(
            user=self.request.user
        ).order_by('-name').distinct()

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.ImageDetailSerializer

        return self.serializer_class
