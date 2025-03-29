from django.utils.text import slugify
from rest_framework import serializers

from .models import Manufacturer


class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = ["name", "description", "image", "slug"]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def validate(self, data):
        if "name" in data:
            if Manufacturer.objects.filter(name=data["name"]).exists():
                raise serializers.ValidationError(
                    "A product category with this name already exists."
                )
        if "description" in data:
            if len(data["description"]) > 500:
                raise serializers.ValidationError(
                    "The description should not exceed 500 characters."
                )
        if "image" in data:
            if data["image"].size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    "The image size should not exceed 2MB."
                )
        return data

    def create(self, validated_data):
        validated_data["slug"] = slugify(validated_data["name"])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "name" in validated_data:
            validated_data["slug"] = slugify(validated_data["name"])
        if "image" in validated_data:
            if instance.image:
                instance.image.delete(save=False)
        return super().update(instance, validated_data)
