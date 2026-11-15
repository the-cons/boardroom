from rest_framework import serializers

from .models import LegalEntity, Ownership

class LegalEntitySerializer(serializers.ModelSerializer):
    kind_display = serializers.CharField(source="get_kind_display", read_only=True)

    class Meta:
        model = LegalEntity
        fields = [
            "id", "name", "kind", "kind_display", "legal_form", "jurisdiction",
            "rcs_number", "incorporated_on", "is_active", "extra",
            "created_at", "updated_at",
        ]

        read_only_fields = ["created_at", "updated_at"]


class OwnershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ownership
        fields = ["id", "parent", "child", "percentage"]


    def validate_percentage(self, value):
        if not 0 < value <= 100:
            raise serializers.ValidationError("Percentage must be between 0 and 100")
        return value

    def validate(self, attrs):
        parent = attrs.get("parent", getattr(self.instance, "parent", None))
        child = attrs.get("child", getattr(self.instance, "child", None))

        if parent is not None and parent == child:
            raise serializers.ValidationError("An entity cannot own itself.")

        return attrs