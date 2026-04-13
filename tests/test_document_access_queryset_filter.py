from types import SimpleNamespace

import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache

from igar.core.document_access import filter_queryset_for_user
from igar.core.models import DocumentAccessGroup, UserDocumentAccessGroup
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.dynamic_search.search_backends import SearchBackend

User = get_user_model()


@pytest.mark.django_db
class TestDocumentQuerysetFiltering:
    def setup_method(self):
        self.user_a = User.objects.create_user(username='user_a', password='test123')
        self.user_b = User.objects.create_user(username='user_b', password='test123')

        self.group_a = DocumentAccessGroup.objects.create(name='Direction')
        self.group_b = DocumentAccessGroup.objects.create(name='Comptabilite')

        UserDocumentAccessGroup.objects.create(user=self.user_a, access_group=self.group_a)

        self.document_type = DocumentType.objects.create(label='Contrat')

        self.public_document = Document.objects.create(
            document_type=self.document_type,
            label='Public document'
        )
        self.group_a_document = Document.objects.create(
            document_type=self.document_type,
            label='Group A document'
        )
        self.group_a_document.access_groups.add(self.group_a)

        self.group_b_document = Document.objects.create(
            document_type=self.document_type,
            label='Group B document'
        )
        self.group_b_document.access_groups.add(self.group_b)

    def test_user_with_group_sees_public_and_allowed_group_documents(self):
        queryset = filter_queryset_for_user(
            queryset=Document.valid.all(), user=self.user_a
        )

        labels = set(queryset.values_list('label', flat=True))
        assert labels == {'Public document', 'Group A document'}

    def test_user_without_group_sees_only_public_documents(self):
        queryset = filter_queryset_for_user(
            queryset=Document.valid.all(), user=self.user_b
        )

        labels = set(queryset.values_list('label', flat=True))
        assert labels == {'Public document'}


@pytest.mark.django_db
class TestSearchIsFilteredByDocumentAccess:
    def setup_method(self):
        cache.clear()

        self.user = User.objects.create_user(username='search_user', password='test123')

        self.group_allowed = DocumentAccessGroup.objects.create(name='Allowed')
        self.group_forbidden = DocumentAccessGroup.objects.create(name='Forbidden')

        UserDocumentAccessGroup.objects.create(user=self.user, access_group=self.group_allowed)

        document_type = DocumentType.objects.create(label='Facture')

        self.allowed_document = Document.objects.create(document_type=document_type, label='Allowed')
        self.allowed_document.access_groups.add(self.group_allowed)

        self.forbidden_document = Document.objects.create(document_type=document_type, label='Forbidden')
        self.forbidden_document.access_groups.add(self.group_forbidden)

    def test_search_backend_applies_user_cloisonnement(self, monkeypatch):
        class DummyInterpreter:
            def do_resolve(self, search_backend):
                return [self_allowed_id, self_forbidden_id]

            def to_explain(self):
                return 'dummy-query'

        self_allowed_id = self.allowed_document.pk
        self_forbidden_id = self.forbidden_document.pk

        monkeypatch.setattr(
            'mayan.apps.dynamic_search.search_backends.SearchInterpreter.init',
            lambda query, search_model: DummyInterpreter()
        )

        search_model = SimpleNamespace(
            permission=None,
            get_queryset=lambda: Document.valid.all()
        )

        backend = SearchBackend()
        _, queryset = backend.search(
            query={'label': 'dummy'},
            search_model=search_model,
            user=self.user
        )

        labels = set(queryset.values_list('label', flat=True))
        assert labels == {'Allowed'}

    def test_search_backend_applies_cloisonnement_for_complex_query_shape(self, monkeypatch):
        allowed_id = self.allowed_document.pk
        forbidden_id = self.forbidden_document.pk

        class DummyInterpreter:
            def do_resolve(self, search_backend):
                # Simulate a broad search hit list that includes forbidden docs.
                return [allowed_id, forbidden_id]

            def to_explain(self):
                return 'complex-query'

        monkeypatch.setattr(
            'mayan.apps.dynamic_search.search_backends.SearchInterpreter.init',
            lambda query, search_model: DummyInterpreter()
        )

        search_model = SimpleNamespace(
            full_name='documents.Document',
            permission=None,
            get_queryset=lambda: Document.valid.all()
        )

        # Complex payload shape: multiple fields and aggregation-like descriptors.
        _, queryset = SearchBackend().search(
            query={
                'label__icontains': 'invoice',
                'document_type__label': 'Facture',
                'facets': {'document_type': True, 'created_at': True},
                'sort': ['-created_at', 'label'],
                'filters': {'status': ['active', 'sealed']},
            },
            search_model=search_model,
            user=self.user
        )

        labels = set(queryset.values_list('label', flat=True))
        assert labels == {'Allowed'}


@pytest.mark.django_db
class TestSearchResultIsolationAndCache:
    def setup_method(self):
        cache.clear()

        self.user_a = User.objects.create_user(username='search_user_a', password='test123')
        self.user_b = User.objects.create_user(username='search_user_b', password='test123')

        self.group_a = DocumentAccessGroup.objects.create(name='A')
        self.group_b = DocumentAccessGroup.objects.create(name='B')

        UserDocumentAccessGroup.objects.create(user=self.user_a, access_group=self.group_a)
        UserDocumentAccessGroup.objects.create(user=self.user_b, access_group=self.group_b)

        document_type = DocumentType.objects.create(label='Facture')

        self.doc_a = Document.objects.create(document_type=document_type, label='facture A')
        self.doc_a.access_groups.add(self.group_a)

        self.doc_b = Document.objects.create(document_type=document_type, label='facture B')
        self.doc_b.access_groups.add(self.group_b)

    def test_same_term_returns_user_specific_documents(self, monkeypatch):
        doc_a_id = self.doc_a.pk
        doc_b_id = self.doc_b.pk

        class DummyInterpreter:
            def do_resolve(self, search_backend):
                return [doc_a_id, doc_b_id]

            def to_explain(self):
                return 'same-term'

        monkeypatch.setattr(
            'mayan.apps.dynamic_search.search_backends.SearchInterpreter.init',
            lambda query, search_model: DummyInterpreter()
        )

        search_model = SimpleNamespace(
            full_name='documents.Document',
            permission=None,
            get_queryset=lambda: Document.valid.all()
        )

        _, queryset_a = SearchBackend().search(
            query={'label': 'facture'},
            search_model=search_model,
            user=self.user_a
        )
        _, queryset_b = SearchBackend().search(
            query={'label': 'facture'},
            search_model=search_model,
            user=self.user_b
        )

        assert set(queryset_a.values_list('label', flat=True)) == {'facture A'}
        assert set(queryset_b.values_list('label', flat=True)) == {'facture B'}

    def test_search_result_cache_is_scoped_per_user_and_query(self, monkeypatch):
        calls = {'count': 0}
        doc_a_id = self.doc_a.pk
        doc_b_id = self.doc_b.pk

        class CountingInterpreter:
            def do_resolve(self, search_backend):
                calls['count'] += 1
                return [doc_a_id, doc_b_id]

            def to_explain(self):
                return 'cache-test'

        monkeypatch.setattr(
            'mayan.apps.dynamic_search.search_backends.SearchInterpreter.init',
            lambda query, search_model: CountingInterpreter()
        )

        search_model = SimpleNamespace(
            full_name='documents.Document',
            permission=None,
            get_queryset=lambda: Document.valid.all()
        )

        backend = SearchBackend()
        backend.search(query={'label': 'facture'}, search_model=search_model, user=self.user_a)
        backend.search(query={'label': 'facture'}, search_model=search_model, user=self.user_a)
        backend.search(query={'label': 'facture'}, search_model=search_model, user=self.user_b)

        # First call for user_a + first call for user_b. Second call user_a should hit cache.
        assert calls['count'] == 2
