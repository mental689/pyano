from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SystemSetting)
admin.site.register(Topic)
admin.site.register(Keyword)
admin.site.register(SearchResult)
admin.site.register(Invitation)
admin.site.register(Alternative)
admin.site.register(Credit)
admin.site.register(VATICJobGroup)
admin.site.register(VATICJob)
admin.site.register(VATICVideo)
admin.site.register(VATICSegment)
admin.site.register(VATICLabel)
admin.site.register(VATICAttribute)
admin.site.register(AttributeAnnotation)
admin.site.register(VATICPath)
admin.site.register(VATICBox)
admin.site.register(VATICBid)
admin.site.register(VATICWorkerJob)
admin.site.register(BannedVideo)