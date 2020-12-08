from django.contrib import admin
from .models import Query

class QueryAdmin(admin.ModelAdmin):
    readonly_fields = ('created',)

admin.site.register(Query, QueryAdmin)

