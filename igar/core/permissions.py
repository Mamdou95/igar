"""Custom Igar permissions for DRF."""

from rest_framework.permissions import BasePermission, IsAdminUser


class HasDocumentAccess(BasePermission):
    """
    Vérifie qu'un utilisateur peut accéder au document demandé.
    
    Logic:
    - Si document.access_groups est vide → accessible à tous (document publique)
    - Sinon, vérifier que user.allowed_document_groups intersect avec document.access_groups
    - Aussi vérifier la permission Django 'document_vault.view_document'
    """

    message = "Vous n'avez pas accès à ce document."

    def has_object_permission(self, request, view, obj):
        # Admins toujours autorisé
        if request.user and request.user.is_staff:
            return True

        # Vérifier permission Django de base
        if not request.user.has_perm('document_vault.view_document'):
            return False

        # Vérifier cloisonnement documentaire
        if not hasattr(obj, 'access_groups'):
            # Si objet n'a pas access_groups, considérer comme public
            return True

        access_groups = obj.access_groups.all()
        if not access_groups.exists():
            # Document public - accessible à tous utilisateurs authentifiés
            return True

        # Vérifier intersection
        user_groups = request.user.allowed_document_groups.all()
        return access_groups.intersection(user_groups).exists()


class IsAdminUser_Igar(IsAdminUser):
    """Extend DRF IsAdminUser for consistency with Mayan RBAC."""
    pass


class IsSuperUserOrAdmin(BasePermission):
    """Permission nécessaire pour les opérations admin."""
    
    message = "Accès réservé aux administrateurs."

    def has_permission(self, request, view):
        return request.user and (request.user.is_superuser or request.user.is_staff)


class CanManageUsers(BasePermission):
    """Permission pour gérer les utilisateurs."""
    
    message = "Vous n'avez pas la permission de gérer les utilisateurs."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('auth.change_user') or request.user.is_superuser


class CanManageRoles(BasePermission):
    """Permission pour gérer les rôles."""
    
    message = "Vous n'avez pas la permission de gérer les rôles."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('auth.change_group') or request.user.is_superuser


class CanViewAuditLogs(BasePermission):
    """Permission pour voir les logs d'audit."""
    
    message = "Vous n'avez pas la permission de consulter les logs d'audit."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.has_perm('igar_core.view_auditlogentry') or request.user.is_superuser
