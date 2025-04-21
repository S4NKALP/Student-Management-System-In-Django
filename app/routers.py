from django.conf import settings
from django.db import models
from django.core.cache import cache

class DatabaseRouter:
    """
    A router to control database operations and optimize query routing
    """
    
    def db_for_read(self, model, **hints):
        """
        Route read operations to the appropriate database
        """
        # Check if model has a cached query
        cache_key = f"db_read_{model._meta.model_name}"
        cached_db = cache.get(cache_key)
        if cached_db:
            return cached_db
            
        # Default to primary database
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Route write operations to the appropriate database
        """
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations between objects
        """
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Allow migrations on the default database
        """
        return db == 'default'

    def optimize_query(self, queryset, **hints):
        """
        Optimize the query based on model and hints
        """
        # Add select_related for foreign key relationships
        if hasattr(queryset.model, '_meta'):
            related_fields = [
                f.name for f in queryset.model._meta.get_fields()
                if f.is_relation and not f.many_to_many
            ]
            if related_fields:
                queryset = queryset.select_related(*related_fields)

        # Add prefetch_related for many-to-many relationships
        m2m_fields = [
            f.name for f in queryset.model._meta.get_fields()
            if f.many_to_many
        ]
        if m2m_fields:
            queryset = queryset.prefetch_related(*m2m_fields)

        # Add caching for frequently accessed queries
        if hints.get('cache', True):
            cache_key = f"query_{queryset.model._meta.model_name}_{hash(str(queryset.query))}"
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

        return queryset 