from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(SystemSetting)
admin.site.register(Topic)
admin.site.register(Keyword)
admin.site.register(SearchResult)