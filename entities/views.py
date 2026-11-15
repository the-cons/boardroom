from rest_framework import viewsets

from rest_framework.permissions import DjangoModelPermissions

from .models import LegalEntity, Ownership
from .serializers import LegalEntitySerializer, OwnershipSerializer
from .permissions import InactiveEntitiesAreReadOnly


class LegalEntityViewSet(viewsets.ModelViewSet):
    queryset = LegalEntity.objects.all()
    serializer_class = LegalEntitySerializer
    permission_classes = [DjangoModelPermissions, InactiveEntitiesAreReadOnly]

    def get_queryset(self):
        qs = super().get_queryset()
        kind = self.request.query_params.get("kind")
        if kind:
            qs = qs.filter(kind=kind)
        return qs


class OwnershipViewSet(viewsets.ModelViewSet):
    queryset = Ownership.objects.all()
    serializer_class = OwnershipSerializer
    permission_classes = [DjangoModelPermissions]