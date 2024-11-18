from django.utils.text import slugify
from rest_framework import serializers

from categories.models import ProductCategory, RoomCategory


class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomCategory
        fields = ["name", "image", "slug"]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def validate(self, data):
        if "name" in data:
            if RoomCategory.objects.filter(name=data["name"]).exists():
                raise serializers.ValidationError(
                    "A room category with this name already exists."
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


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ["name", "image", "slug"]
        read_only_fields = ["slug", "created_at", "updated_at"]

    def validate(self, data):
        if "name" in data:
            if ProductCategory.objects.filter(name=data["name"]).exists():
                raise serializers.ValidationError(
                    "A product category with this name already exists."
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
