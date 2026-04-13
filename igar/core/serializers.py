"""Serializers for admin user management endpoints."""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from rest_framework import serializers

from igar.core.models import (
    DocumentAccessGroup,
    GroupDocumentAccessGroup,
    UserDocumentAccessGroup,
)

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    """Simple user serializer for list views."""

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
        )
        read_only_fields = ('id',)


class GroupSimpleSerializer(serializers.ModelSerializer):
    """Simple group serializer."""

    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )
    allowed_document_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=DocumentAccessGroup.objects.all(),
        required=False,
    )

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions', 'allowed_document_groups')
        read_only_fields = ('id',)

    def create(self, validated_data):
        permissions = validated_data.pop('permissions', [])
        allowed_groups = validated_data.pop('allowed_document_groups', [])
        group = Group.objects.create(**validated_data)
        if permissions:
            group.permissions.set(permissions)
        if allowed_groups:
            GroupDocumentAccessGroup.objects.bulk_create(
                [
                    GroupDocumentAccessGroup(group=group, access_group=access_group)
                    for access_group in allowed_groups
                ]
            )
        return group

    def update(self, instance, validated_data):
        permissions = validated_data.pop('permissions', None)
        allowed_groups = validated_data.pop('allowed_document_groups', None)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        if permissions is not None:
            instance.permissions.set(permissions)
        if allowed_groups is not None:
            GroupDocumentAccessGroup.objects.filter(group=instance).delete()
            GroupDocumentAccessGroup.objects.bulk_create(
                [
                    GroupDocumentAccessGroup(group=instance, access_group=access_group)
                    for access_group in allowed_groups
                ]
            )
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['allowed_document_groups'] = list(
            GroupDocumentAccessGroup.objects.filter(group=instance).values_list(
                'access_group_id', flat=True
            )
        )
        return data


class DocumentAccessGroupSerializer(serializers.ModelSerializer):
    """Serializer for document access groups."""

    class Meta:
        model = DocumentAccessGroup
        fields = ('id', 'uuid', 'name', 'description', 'parent', 'created_at')
        read_only_fields = ('id', 'uuid', 'created_at')


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for create/update operations."""

    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Group.objects.all(),
        help_text="List of group IDs to assign to the user"
    )
    allowed_document_groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'allowed_document_groups',
            'date_joined',
            'last_login',
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'allowed_document_groups')
        extra_kwargs = {
            'username': {
                'validators': [],  # Remove unique validator, we'll handle it
            },
        }

    def validate_username(self, value):
        """Validate username is unique (excluding current user on update)."""
        if self.instance:
            # On update, exclude current user
            if User.objects.filter(username=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("This username is already in use.")
        else:
            # On create
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("This username is already in use.")
        return value

    def validate_email(self, value):
        """Validate email is unique."""
        email = value
        if email:
            if self.instance:
                if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
                    raise serializers.ValidationError("This email is already in use.")
            else:
                if User.objects.filter(email=email).exists():
                    raise serializers.ValidationError("This email is already in use.")
        return email

    def get_allowed_document_groups(self, obj):
        assignments = UserDocumentAccessGroup.objects.filter(user=obj).select_related('access_group')
        groups = [assignment.access_group for assignment in assignments]
        return DocumentAccessGroupSerializer(groups, many=True).data

    def validate_groups(self, value):
        """Validate at least one group is assigned."""
        if not value:
            raise serializers.ValidationError("User must be assigned to at least one group.")
        return value

    def create(self, validated_data):
        """Create a new user."""
        groups = validated_data.pop('groups', [])
        user = User.objects.create_user(**validated_data)
        user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        """Update user."""
        groups = validated_data.pop('groups', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update groups if provided
        if groups is not None:
            instance.groups.set(groups)

        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users."""

    password = serializers.CharField(write_only=True, required=False)
    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Group.objects.all()
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'groups',
            'is_active',
        )

    def create(self, validated_data):
        """Create user with password."""
        groups = validated_data.pop('groups', [])
        password = validated_data.pop('password', None)
        
        user = User.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        user.groups.set(groups)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating users."""

    groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Group.objects.all()
    )
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = (
            'email',
            'first_name',
            'last_name',
            'groups',
            'is_active',
        )

    def update(self, instance, validated_data):
        """Update user."""
        groups = validated_data.pop('groups', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if groups is not None:
            instance.groups.set(groups)

        return instance


class AuditLogEntrySerializer(serializers.Serializer):
    """Serializer for audit log entries."""

    id = serializers.IntegerField(read_only=True)
    uuid = serializers.UUIDField(read_only=True)
    action = serializers.CharField(read_only=True)
    resource_type = serializers.CharField(read_only=True)
    resource_id = serializers.IntegerField(read_only=True)
    old_values = serializers.JSONField(read_only=True)
    new_values = serializers.JSONField(read_only=True)
    ip_address = serializers.IPAddressField(read_only=True, allow_null=True)
    reason = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        if not obj.user:
            return None
        return {
            'id': obj.user.id,
            'username': obj.user.get_username(),
        }
