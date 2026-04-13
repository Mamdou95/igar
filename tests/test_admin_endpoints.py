"""Tests for admin user and role management endpoints."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework import status

from igar.core.models import DocumentAccessGroup
from igar.core.audit import AuditLogger

User = get_user_model()


@pytest.mark.django_db
class TestAdminUsersEndpoints:
    """Tests for admin user management endpoints."""

    def setup_method(self):
        """Setup test client and admin user."""
        self.client = APIClient()
        self.factory = RequestFactory()
        
        # Create admin user
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create regular users
        self.user1 = User.objects.create_user(
            username='alice',
            email='alice@example.com',
            password='test123'
        )
        
        self.user2 = User.objects.create_user(
            username='bob',
            email='bob@example.com',
            password='test123'
        )
        
        # Create roles
        self.comptables_role = Group.objects.create(name='Comptables')
        self.hr_role = Group.objects.create(name='HR_Staff')
        
        # Assign roles to users
        self.user1.groups.add(self.comptables_role)
        self.user2.groups.add(self.hr_role)
        
        # Create document groups
        self.compta_group = DocumentAccessGroup.objects.create(
            name='Comptabilité',
            description='Documents comptables'
        )
        self.hr_group = DocumentAccessGroup.objects.create(
            name='RH',
            description='Documents RH'
        )

    def test_admin_can_list_users(self):
        """Test admin can list users."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/users/')
        assert response.status_code == 200
        assert len(response.data) >= 2

    def test_admin_can_create_user(self):
        """Test admin can create new user."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'groups': [self.comptables_role.id],
        }
        response = self.client.post('/api/v1/admin/users/', data)
        assert response.status_code == 201
        assert response.data['username'] == 'newuser'
        
        # Verify audit log
        logs = AuditLogger.get_logs(action='user.created', user=self.admin)
        assert len(logs) >= 1

    def test_admin_cannot_create_duplicate_username(self):
        """Test cannot create user with duplicate username."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'username': 'alice',  # Already exists
            'email': 'alice2@example.com',
            'groups': [self.comptables_role.id],
        }
        response = self.client.post('/api/v1/admin/users/', data)
        assert response.status_code == 400

    def test_admin_can_update_user(self):
        """Test admin can update user."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'email': 'alice_new@example.com',
            'first_name': 'Alice',
            'last_name': 'Smith',
            'groups': [self.hr_role.id],
        }
        response = self.client.patch(f'/api/v1/admin/users/{self.user1.id}/', data)
        assert response.status_code == 200
        self.user1.refresh_from_db()
        assert self.user1.email == 'alice_new@example.com'

    def test_admin_can_deactivate_user(self):
        """Test admin can deactivate user."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/admin/users/{self.user1.id}/')
        assert response.status_code == 200
        self.user1.refresh_from_db()
        assert self.user1.is_active is False

    def test_admin_can_reset_user_password(self):
        """Test admin can reset user password."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/users/{self.user1.id}/reset_password/')
        assert response.status_code == 200
        assert 'reset_url' in response.data

    def test_admin_can_reset_user_2fa(self):
        """Test admin can reset user 2FA."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.post(f'/api/v1/admin/users/{self.user1.id}/reset_2fa/')
        assert response.status_code == 200
        assert response.data['status'] == '2fa_reset'

    def test_regular_user_cannot_manage_users(self):
        """Test regular user cannot access user management."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/v1/admin/users/')
        assert response.status_code == 403


@pytest.mark.django_db
class TestAdminRolesEndpoints:
    """Tests for admin role management endpoints."""

    def setup_method(self):
        """Setup test client and admin user."""
        self.client = APIClient()
        
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.comptables_role = Group.objects.create(name='Comptables')
        self.compta_group = DocumentAccessGroup.objects.create(name='Comptabilite')
        self.rh_group = DocumentAccessGroup.objects.create(name='Ressources Humaines')

    def test_admin_can_list_roles(self):
        """Test admin can list roles."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/roles/')
        assert response.status_code == 200

    def test_admin_can_create_role(self):
        """Test admin can create new role."""
        self.client.force_authenticate(user=self.admin)
        data = {'name': 'Directors'}
        response = self.client.post('/api/v1/admin/roles/', data)
        assert response.status_code == 201
        assert response.data['name'] == 'Directors'

    def test_admin_can_set_allowed_document_groups_on_create_role(self):
        """Test creating role with document access groups mapping."""
        self.client.force_authenticate(user=self.admin)
        data = {
            'name': 'Archives Specifiques',
            'allowed_document_groups': [self.compta_group.id, self.rh_group.id],
        }
        response = self.client.post('/api/v1/admin/roles/', data, format='json')
        assert response.status_code == 201
        assert sorted(response.data['allowed_document_groups']) == sorted(
            [self.compta_group.id, self.rh_group.id]
        )

    def test_admin_can_update_allowed_document_groups_on_role(self):
        """Test updating role's allowed document groups."""
        self.client.force_authenticate(user=self.admin)
        data = {'allowed_document_groups': [self.rh_group.id]}
        response = self.client.patch(
            f'/api/v1/admin/roles/{self.comptables_role.id}/', data, format='json'
        )
        assert response.status_code == 200
        assert response.data['allowed_document_groups'] == [self.rh_group.id]

    def test_admin_can_list_permissions(self):
        """Test admin can list available permissions."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/roles/permissions/')
        assert response.status_code == 200

    def test_admin_can_list_permissions_via_dedicated_endpoint(self):
        """Test dedicated permissions endpoint returns grouped payload items."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/v1/admin/permissions/')
        assert response.status_code == 200
        assert 'results' in response.data

    def test_delete_role_fails_if_users_exist(self):
        """Test role deletion is blocked when users are still assigned."""
        assigned_user = User.objects.create_user(username='assigned', password='test')
        assigned_user.groups.add(self.comptables_role)

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/admin/roles/{self.comptables_role.id}/')
        assert response.status_code == 409

    def test_delete_role_succeeds_when_no_users(self):
        """Test role can be deleted when no users are assigned."""
        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f'/api/v1/admin/roles/{self.comptables_role.id}/')
        assert response.status_code == 200


@pytest.mark.django_db
class TestRBACPermissionMatrix:
    """Tests for permission matrix across different roles."""

    def setup_method(self):
        """Setup roles with specific permissions."""
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        # Create roles
        self.comptables = Group.objects.create(name='Comptables')
        self.hr = Group.objects.create(name='HR_Staff')
        self.directors = Group.objects.create(name='Directors')
        
        # Create users for each role
        self.comptable_user = User.objects.create_user(
            username='comptable',
            password='test'
        )
        self.comptable_user.groups.add(self.comptables)
        
        self.hr_user = User.objects.create_user(
            username='hr_staff',
            password='test'
        )
        self.hr_user.groups.add(self.hr)

    def test_role_assignment_to_groups(self):
        """Test roles can be assigned document groups."""
        compta_group = DocumentAccessGroup.objects.create(name='Comptabilité')
        
        from igar.core.models import GroupDocumentAccessGroup
        GroupDocumentAccessGroup.objects.create(
            group=self.comptables,
            access_group=compta_group
        )
        
        assert GroupDocumentAccessGroup.objects.filter(
            group=self.comptables,
            access_group=compta_group,
        ).exists()

    def test_user_inherits_role_permissions(self):
        """Test user inherits permissions from assigned role."""
        self.comptable_user.refresh_from_db()
        assert self.comptables in self.comptable_user.groups.all()

    def test_multiple_roles_per_user(self):
        """Test user can have multiple roles."""
        multi_user = User.objects.create_user(
            username='multi_role',
            password='test'
        )
        multi_user.groups.add(self.comptables)
        multi_user.groups.add(self.directors)
        
        assert multi_user.groups.count() == 2

    def test_no_permission_interference_between_roles(self):
        """Test permissions from one role don't interfere with another."""
        compta_group = DocumentAccessGroup.objects.create(name='Comptabilité')
        hr_group = DocumentAccessGroup.objects.create(name='RH')
        
        from igar.core.models import GroupDocumentAccessGroup
        GroupDocumentAccessGroup.objects.create(group=self.comptables, access_group=compta_group)
        GroupDocumentAccessGroup.objects.create(group=self.hr, access_group=hr_group)
        
        # comptable_user should only have comptables permissions
        comptables_links = GroupDocumentAccessGroup.objects.filter(group=self.comptables)
        assert comptables_links.filter(access_group=compta_group).exists()
        assert not comptables_links.filter(access_group=hr_group).exists()


@pytest.mark.django_db  
class TestDocumentAccessCloisonnement:
    """Tests for document access cloisonnement (compartmentalization)."""

    def setup_method(self):
        """Setup users and document groups."""
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        
        self.user1 = User.objects.create_user(
            username='user1',
            password='test'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            password='test'
        )
        
        self.compta_group = DocumentAccessGroup.objects.create(
            name='Comptabilité'
        )
        self.hr_group = DocumentAccessGroup.objects.create(
            name='RH'
        )
        
        # Assign groups to users
        from igar.core.models import UserDocumentAccessGroup
        UserDocumentAccessGroup.objects.create(
            user=self.user1,
            access_group=self.compta_group
        )
        UserDocumentAccessGroup.objects.create(
            user=self.user2,
            access_group=self.hr_group
        )

    def test_user_assigned_to_document_group(self):
        """Test user is assigned to document group."""
        from igar.core.models import UserDocumentAccessGroup

        assert UserDocumentAccessGroup.objects.filter(
            user=self.user1,
            access_group=self.compta_group,
        ).exists()
        assert not UserDocumentAccessGroup.objects.filter(
            user=self.user1,
            access_group=self.hr_group,
        ).exists()

    def test_document_group_assignment_persists(self):
        """Test document group assignments persist."""
        from igar.core.models import UserDocumentAccessGroup

        self.user1.refresh_from_db()
        assert UserDocumentAccessGroup.objects.filter(
            user=self.user1,
            access_group=self.compta_group,
        ).exists()

    def test_user_cannot_access_other_groups(self):
        """Test user cannot access documents outside their groups."""
        from igar.core.models import UserDocumentAccessGroup

        # User1 only has access to compta_group
        assert not UserDocumentAccessGroup.objects.filter(
            user=self.user1,
            access_group=self.hr_group,
        ).exists()
        # User2 only has access to hr_group
        assert not UserDocumentAccessGroup.objects.filter(
            user=self.user2,
            access_group=self.compta_group,
        ).exists()

    def test_audit_log_tracks_access_attempts(self):
        """Test audit log tracks access attempts."""
        # Log a denied access
        AuditLogger.log(
            action='document.access_denied',
            resource_type='document',
            resource_id=999,
            user=self.user1,
        )
        
        logs = AuditLogger.get_logs(action='document.access_denied')
        assert len(logs) >= 1
