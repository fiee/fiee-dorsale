from django.contrib import admin
from siteprofile.models import Module, SiteProfile

class ModuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')
    ordering = ('code',)
    search_fields = ('name', 'code', 'description')

class SiteProfileAdmin(admin.ModelAdmin):
    list_display = ('site', 'code', 'baselanguage', 'admingroup', 'ownstyle', 'homeurl',)
    list_filter = ('baselanguage','admingroup','ownstyle')
    ordering = ('code',)
    search_fields = ('code',)

admin.site.register(Module, ModuleAdmin)
admin.site.register(SiteProfile, SiteProfileAdmin)
