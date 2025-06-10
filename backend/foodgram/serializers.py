from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from djoser.serializers import (
    UserSerializer as BaseUserSerializer,
    UserCreateSerializer as BaseUserCreateSerializer
)


from . import models


class UserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = models.User
        fields = (
            'id', 'username', 'email',
            'first_name', 'last_name',
        )
        read_only_fields = ('username', 'is_subscribed', 'avatar')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def get_is_subscribed(self, obj):
        return obj.subscribers.contains(self.context['request'].user)

    def get_avatar(self, obj):
        if obj.profile.avatar is None:
            return ""
        return obj.profile.avatar.url


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta:
        model = models.User
        fields = (
            'username', 'password', 'email',
            'first_name', 'last_name',
        )
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def perform_create(self, validated_data):
        user = super().perform_create(validated_data)
        models.Profile.objects.create(user=user)
        return user


class AvatarSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault())
    avatar = Base64ImageField()

    class Meta:
        model = models.Profile
        fields = ('user', 'avatar')
