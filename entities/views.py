from rest_framework import viewsets

from .models import LegalEntity, Ownership
from .serializers import LegalEntitySerializer, OwnershipSerializer


class LegalEntityViewSet(viewsets.ModelViewSet):
    queryset = LegalEntity.objects.all()
    serializer_class = LegalEntitySerializer

    def get_queryset(self):
        qs = super().get_queryset()
        kind = self.request.query_params.get("kind")
        if kind:
            qs = qs.filter(kind=kind)
        return qs


class OwnershipViewSet(viewsets.ModelViewSet):
    queryset = Ownership.objects.all()
    serializer_class = OwnershipSerializer
