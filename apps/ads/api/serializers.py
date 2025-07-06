from ..models import ItemsModel, CategoryModel, ExchangeProposalModel
from rest_framework import serializers


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryModel
        fields = ["id", "title"]


class ItemPreviewSerializer(serializers.ModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = ItemsModel
        fields = [
            "id",
            "user",
            "title",
            "description",
            "image_url",
            "category",
            "condition",
            "created_at",
        ]


class ItemCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=CategoryModel.objects.all())

    class Meta:
        model = ItemsModel
        fields = ["title", "description", "image_url", "category", "condition"]


class ExchangeProposalSerializer(serializers.ModelSerializer):
    ad_sender = ItemPreviewSerializer(read_only=True)
    ad_receiver = ItemPreviewSerializer(read_only=True)
    ad_sender_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemsModel.objects.all(), write_only=True
    )
    ad_receiver_id = serializers.PrimaryKeyRelatedField(
        queryset=ItemsModel.objects.all(), write_only=True
    )

    class Meta:
        model = ExchangeProposalModel
        fields = [
            "id",
            "ad_sender",
            "ad_receiver",
            "comment",
            "status",
            "created_at",
            "ad_sender_id",
            "ad_receiver_id",
        ]

    def create(self, validated_data):
        ad_sender = validated_data.pop("ad_sender_id")
        ad_receiver = validated_data.pop("ad_receiver_id")
        return ExchangeProposalModel.objects.create(
            ad_sender=ad_sender, ad_receiver=ad_receiver, **validated_data
        )
