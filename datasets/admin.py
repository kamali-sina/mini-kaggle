from django.contrib import admin
from .models import Dataset, Tag, DataSource, Column

# Register your models here.

admin.site.register(Dataset)
admin.site.register(Tag)
admin.site.register(DataSource)
admin.site.register(Column)
