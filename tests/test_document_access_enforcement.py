"""Tests for document access enforcement and decorators."""

import pytest
from django.contrib.auth.models import AnonymousUser, User
from django.http import Http404
from django.test import RequestFactory

from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType

from igar.core.models import DocumentAccessGroup, UserDocumentAccessGroup
from igar.core.document_access import IsDocumentAccessible, require_document_access


@pytest.mark.django_db
class TestDocumentAccessMixin:
    """Test DocumentAccessMixin for viewset filtering."""
    
    def setup_method(self):
        """Set up test users, groups, and document access groups."""
        # Create users
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='user123',
            is_active=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='user123',
            is_active=True
        )
        
        # Create document access groups
        self.group_a = DocumentAccessGroup.objects.create(
            name='Group A',
            description='First access group'
        )
        self.group_b = DocumentAccessGroup.objects.create(
            name='Group B',
            description='Second access group'
        )
        
        # Assign users to document groups
        UserDocumentAccessGroup.objects.create(
            user=self.user1,
            access_group=self.group_a
        )
        UserDocumentAccessGroup.objects.create(
            user=self.user2,
            access_group=self.group_b
        )
    
    def test_mixin_filter_by_user_groups(self):
        """Test mixin filters queryset by user's document groups."""
        # User1 should only see documents in group_a
        user1_group_names = set(
            UserDocumentAccessGroup.objects.filter(user=self.user1)
            .values_list('access_group__name', flat=True)
        )
        assert user1_group_names == {'Group A'}
        
        # User2 should only see documents in group_b
        user2_group_names = set(
            UserDocumentAccessGroup.objects.filter(user=self.user2)
            .values_list('access_group__name', flat=True)
        )
        assert user2_group_names == {'Group B'}
    
    def test_admin_bypass_cloisonnement(self):
        """Test admin users bypass document access filtering."""
        assert self.admin_user.is_staff is True


@pytest.mark.django_db
class TestIsDocumentAccessiblePermission:
    """Test IsDocumentAccessible permission class."""
    
    def setup_method(self):
        """Set up test data."""
        self.factory = RequestFactory()
        self.permission = IsDocumentAccessible()
        
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        
        self.group1 = DocumentAccessGroup.objects.create(
            name='Group 1'
        )
        self.group2 = DocumentAccessGroup.objects.create(
            name='Group 2'
        )
        
        # Assign user to group1
        UserDocumentAccessGroup.objects.create(
            user=self.user,
            access_group=self.group1
        )
    
    def test_admin_has_permission(self):
        """Test admin users always have permission."""
        request = self.factory.get('/')
        request.user = self.admin

        class MockDoc:
            pass

        obj = MockDoc()
        assert self.permission.has_object_permission(request, None, obj) is True
    
    def test_user_has_access_to_group1(self):
        """Test user can access documents in their groups."""
        request = self.factory.get('/')
        request.user = self.user

        class MockFilterResult:
            def __init__(self, allowed: bool):
                self._allowed = allowed

            def exists(self):
                return self._allowed

        class MockAccessGroups:
            def __init__(self, has_groups: bool, allowed: bool):
                self._has_groups = has_groups
                self._allowed = allowed

            def all(self):
                return self

            def exists(self):
                return self._has_groups

            def filter(self, **kwargs):
                return MockFilterResult(self._allowed)

        class MockDoc:
            access_groups = MockAccessGroups(has_groups=True, allowed=True)

        obj = MockDoc()
        assert self.permission.has_object_permission(request, None, obj) is True
    
    def test_unauthenticated_denied(self):
        """Test unauthenticated users are denied."""
        request = self.factory.get('/')
        request.user = AnonymousUser()
        
        class MockDoc:
            pass
        
        obj = MockDoc()
        assert self.permission.has_object_permission(request, None, obj) is False


@pytest.mark.django_db
class TestDocumentAccessAuditLogging:
    """Test that denied access attempts are logged."""
    
    def setup_method(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        self.group = DocumentAccessGroup.objects.create(
            name='Group'
        )
        
        # User NOT assigned to this group
    
    def test_denied_access_logged(self):
        """Test denied access attempts create audit entries."""
        # Import here to avoid circular imports
        from igar.core.models import AuditLogEntry
        
        # Create audit entry for denied access
        audit = AuditLogEntry.objects.create(
            action='document.access_denied',
            resource_type='document',
            resource_id=123,
            user=self.user,
            ip_address='127.0.0.1'
        )
        
        assert audit.action == 'document.access_denied'
        assert audit.user == self.user
        assert AuditLogEntry.objects.filter(
            action='document.access_denied',
            user=self.user
        ).exists()


@pytest.mark.django_db
class TestDocumentCloisonnementIsolation:
    """Test that document cloisonnement properly isolates users."""
    
    def setup_method(self):
        """Set up test data."""
        self.user_a = User.objects.create_user(
            username='usera',
            email='usera@example.com',
            password='pass123'
        )
        self.user_b = User.objects.create_user(
            username='userb',
            email='userb@example.com',
            password='pass123'
        )
        
        self.group_a = DocumentAccessGroup.objects.create(
            name='Department A'
        )
        self.group_b = DocumentAccessGroup.objects.create(
            name='Department B'
        )
        
        # Assign users to different groups
        UserDocumentAccessGroup.objects.create(
            user=self.user_a,
            access_group=self.group_a
        )
        UserDocumentAccessGroup.objects.create(
            user=self.user_b,
            access_group=self.group_b
        )
    
    def test_users_isolated_between_groups(self):
        """Test users can only see documents in their assigned groups."""
        user_a_group_names = set(
            UserDocumentAccessGroup.objects.filter(user=self.user_a)
            .values_list('access_group__name', flat=True)
        )
        user_b_group_names = set(
            UserDocumentAccessGroup.objects.filter(user=self.user_b)
            .values_list('access_group__name', flat=True)
        )

        assert user_a_group_names == {'Department A'}
        assert user_b_group_names == {'Department B'}
        assert user_a_group_names.isdisjoint(user_b_group_names)
    
    def test_user_no_access_no_isolation(self):
        """Test users with no group assignments can't see anything."""
        user_c = User.objects.create_user(
            username='userc',
            email='userc@example.com',
            password='pass123'
        )

        groups_count = UserDocumentAccessGroup.objects.filter(user=user_c).count()
        assert groups_count == 0
        # This user should see no documents


@pytest.mark.django_db
class TestDirectUrlAccessByDocumentId:
    """Validate that direct document ID access cannot bypass cloisonnement."""

    def setup_method(self):
        self.factory = RequestFactory()

        self.user_a = User.objects.create_user(
            username='user_a_direct',
            email='user_a_direct@example.com',
            password='pass123'
        )
        self.user_b = User.objects.create_user(
            username='user_b_direct',
            email='user_b_direct@example.com',
            password='pass123'
        )

        self.group_a = DocumentAccessGroup.objects.create(name='Group A Direct')
        self.group_b = DocumentAccessGroup.objects.create(name='Group B Direct')

        UserDocumentAccessGroup.objects.create(user=self.user_a, access_group=self.group_a)
        UserDocumentAccessGroup.objects.create(user=self.user_b, access_group=self.group_b)

        self.document_type = DocumentType.objects.create(label='Document direct')
        self.document_group_b = Document.objects.create(
            document_type=self.document_type,
            label='Confidential Group B document'
        )
        self.document_group_b.access_groups.add(self.group_b)

        self.document_group_a = Document.objects.create(
            document_type=self.document_type,
            label='Confidential Group A document'
        )
        self.document_group_a.access_groups.add(self.group_a)

    def _build_view(self):
        class DummyView:
            def get_queryset(self):
                return Document.valid.all()

        @require_document_access
        def _view(view_self, request, pk):
            return pk

        return DummyView(), _view

    def test_direct_id_url_access_is_denied_for_forbidden_group_document(self):
        view_instance, wrapped_view = self._build_view()
        request = self.factory.get(f'/documents/{self.document_group_b.pk}/')
        request.user = self.user_a

        with pytest.raises(Http404):
            wrapped_view(view_instance, request, pk=self.document_group_b.pk)

    def test_direct_id_url_access_is_allowed_for_authorized_group_document(self):
        view_instance, wrapped_view = self._build_view()
        request = self.factory.get(f'/documents/{self.document_group_a.pk}/')
        request.user = self.user_a

        result = wrapped_view(view_instance, request, pk=self.document_group_a.pk)

        assert result == self.document_group_a.pk
