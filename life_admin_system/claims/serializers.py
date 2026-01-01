from rest_framework import serializers
from claims.models import Claim
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Claim


class ClaimSerializer(serializers.ModelSerializer):
    class Meta:
        model = Claim
        fields = "__all__"

    def create(self, validated_data):
        claim = Claim(**validated_data)

        try:
            claim.full_clean()  # model-level validation
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.message_dict or e.messages)

        claim.save()
        return claim


from rest_framework import serializers

class ClaimApprovalSerializer(serializers.Serializer):
    action = serializers.ChoiceField(choices=["approve", "reject"])
    reject_reason = serializers.CharField(
        required=False,
        allow_blank=True
    )
