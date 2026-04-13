"""Tests for RBAC models and document access groups."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from igar.core.models import (
    DocumentAccessGroup,
    UserDocumentAccessGroup,
    GroupDocumentAccessGroup,
    AuditLogEntry,
)
from igar.core.audit import AuditLogger

User = get_user_model()


@pytest.mark.django_db
class TestDocumentAccessGroup:
    """Tests pour le modèle DocumentAccessGroup."""

    def test_create_document_access_group(self):
        """Test creation d'un groupe d'accès documentaire."""
        group = DocumentAccessGroup.objects.create(
            name="Direction",
            description="Documents de la direction"
        )
        assert group.name == "Direction"
        assert group.description == "Documents de la direction"
        assert group.uuid
        assert group.created_at
        assert group.parent is None

    def test_document_access_group_unique_name(self):
        """Test que les noms doivent être uniques."""
        DocumentAccessGroup.objects.create(name="Direction")
        with pytest.raises(Exception):  # IntegrityError
            DocumentAccessGroup.objects.create(name="Direction")

    def test_document_access_group_hierarchy(self):
        """Test la hiérarchie parent-child de groupes."""
        parent = DocumentAccessGroup.objects.create(name="Administration")
        child = DocumentAccessGroup.objects.create(name="Comptabilité", parent=parent)
        
        assert child.parent == parent
        assert child in parent.children.all()

    def test_document_access_group_str(self):
        """Test la représentation string."""
        group = DocumentAccessGroup.objects.create(name="RH")
        assert str(group) == "RH"


@pytest.mark.django_db
class TestUserDocumentAccessGroup:
    """Tests pour l'association User-DocumentAccessGroup."""

    def test_assign_user_to_document_group(self):
        """Test l'assignation d'un user à un groupe documentaire."""
        user = User.objects.create_user(username="alice", password="test")
        group = DocumentAccessGroup.objects.create(name="Comptabilité")
        
        assignment = UserDocumentAccessGroup.objects.create(
            user=user,
            access_group=group
        )
        
        assert assignment.user == user
        assert assignment.access_group == group
        assert UserDocumentAccessGroup.objects.filter(user=user, access_group=group).exists()

    def test_user_document_group_unique_constraint(self):
        """Test que user+group combo est unique."""
        user = User.objects.create_user(username="bob", password="test")
        group = DocumentAccessGroup.objects.create(name="RH")
        
        UserDocumentAccessGroup.objects.create(user=user, access_group=group)
        
        with pytest.raises(Exception):  # IntegrityError
            UserDocumentAccessGroup.objects.create(user=user, access_group=group)

    def test_multiple_groups_per_user(self):
        """Test qu'un utilisateur peut avoir accès à plusieurs groupes."""
        user = User.objects.create_user(username="charlie", password="test")
        group1 = DocumentAccessGroup.objects.create(name="Comptabilité")
        group2 = DocumentAccessGroup.objects.create(name="RH")
        
        UserDocumentAccessGroup.objects.create(user=user, access_group=group1)
        UserDocumentAccessGroup.objects.create(user=user, access_group=group2)
        
        assignments = UserDocumentAccessGroup.objects.filter(user=user)
        assert assignments.count() == 2
        assert assignments.filter(access_group=group1).exists()
        assert assignments.filter(access_group=group2).exists()


@pytest.mark.django_db
class TestGroupDocumentAccessGroup:
    """Tests pour l'association Role(Group)-DocumentAccessGroup."""

    def test_assign_role_to_document_group(self):
        """Test l'assignation d'un rôle à un groupe documentaire."""
        role = Group.objects.create(name="Comptables")
        group = DocumentAccessGroup.objects.create(name="Comptabilité")
        
        assignment = GroupDocumentAccessGroup.objects.create(
            group=role,
            access_group=group
        )
        
        assert assignment.group == role
        assert assignment.access_group == group

    def test_role_inherits_document_group_access(self):
        """Test que les users du rôle héritent de l'accès au groupe documentaire."""
        # Create role and document group
        role = Group.objects.create(name="RH_Staff")
        doc_group = DocumentAccessGroup.objects.create(name="RH")
        
        # Assign role to document group
        GroupDocumentAccessGroup.objects.create(group=role, access_group=doc_group)
        
        # Create user and add to role
        user = User.objects.create_user(username="diana", password="test")
        user.groups.add(role)
        
        # User should have access via role
        assert role in user.groups.all()
        assert GroupDocumentAccessGroup.objects.filter(
            group__user=user,
            access_group=doc_group
        ).exists()


@pytest.mark.django_db
class TestAuditLogEntry:
    """Tests pour le modèle AuditLogEntry."""

    def test_create_audit_log_entry(self):
        """Test création d'une entrée d'audit."""
        user = User.objects.create_user(username="admin", password="test")
        
        entry = AuditLogEntry.objects.create(
            action="user.created",
            resource_type="user",
            resource_id=123,
            user=user,
            new_values={"username": "newuser", "email": "new@example.com"},
            ip_address="192.168.1.1"
        )
        
        assert entry.action == "user.created"
        assert entry.resource_type == "user"
        assert entry.resource_id == 123
        assert entry.user == user
        assert entry.ip_address == "192.168.1.1"

    def test_audit_log_modification_with_old_and_new_values(self):
        """Test un log d'audit avec avant/après."""
        user = User.objects.create_user(username="admin", password="test")
        
        entry = AuditLogEntry.objects.create(
            action="user.modified",
            resource_type="user",
            resource_id=456,
            user=user,
            old_values={"email": "old@example.com"},
            new_values={"email": "new@example.com"}
        )
        
        assert entry.old_values == {"email": "old@example.com"}
        assert entry.new_values == {"email": "new@example.com"}

    def test_audit_log_query_filter_by_user(self):
        """Test filtrage des logs par utilisateur."""
        admin1 = User.objects.create_user(username="admin1", password="test")
        admin2 = User.objects.create_user(username="admin2", password="test")
        
        AuditLogEntry.objects.create(
            action="user.created",
            resource_type="user",
            resource_id=1,
            user=admin1
        )
        AuditLogEntry.objects.create(
            action="user.created",
            resource_type="user",
            resource_id=2,
            user=admin2
        )
        
        admin1_logs = AuditLogEntry.objects.filter(user=admin1)
        assert admin1_logs.count() == 1

    def test_audit_log_query_filter_by_action(self):
        """Test filtrage des logs par action."""
        user = User.objects.create_user(username="admin", password="test")
        
        AuditLogEntry.objects.create(
            action="user.created",
            resource_type="user",
            resource_id=1,
            user=user
        )
        AuditLogEntry.objects.create(
            action="user.modified",
            resource_type="user",
            resource_id=1,
            user=user
        )
        
        created_logs = AuditLogEntry.objects.filter(action="user.created")
        assert created_logs.count() == 1


@pytest.mark.django_db
class TestAuditLogger:
    """Tests pour le service AuditLogger."""

    def test_audit_logger_log_creation(self):
        """Test l'enregistrement d'un événement via AuditLogger."""
        user = User.objects.create_user(username="admin", password="test")
        
        entry = AuditLogger.log(
            action="user.created",
            resource_type="user",
            resource_id=789,
            user=user,
            new_values={"username": "newuser"},
            ip_address="10.0.0.1",
            reason="Admin créa nouvel utilisateur"
        )
        
        assert entry.action == "user.created"
        assert entry.user == user
        assert AuditLogEntry.objects.filter(id=entry.id).exists()

    def test_audit_logger_get_logs(self):
        """Test la récupération des logs filtrés."""
        admin = User.objects.create_user(username="admin", password="test")
        user1 = User.objects.create_user(username="user1", password="test")
        
        AuditLogger.log(
            action="user.created",
            resource_type="user",
            resource_id=1,
            user=admin,
            new_values={"username": "user1"}
        )
        AuditLogger.log(
            action="user.created",
            resource_type="user",
            resource_id=2,
            user=admin,
            new_values={"username": "user2"}
        )
        
        logs = AuditLogger.get_logs(action="user.created", user=admin)
        assert len(logs) == 2

    def test_audit_logger_get_logs_filter_by_resource(self):
        """Test filtrage des logs par resource_type."""
        admin = User.objects.create_user(username="admin", password="test")
        
        AuditLogger.log(
            action="user.created",
            resource_type="user",
            resource_id=1,
            user=admin
        )
        AuditLogger.log(
            action="role.created",
            resource_type="role",
            resource_id=1,
            user=admin
        )
        
        user_logs = AuditLogger.get_logs(resource_type="user")
        role_logs = AuditLogger.get_logs(resource_type="role")
        
        assert len(user_logs) == 1
        assert len(role_logs) == 1
