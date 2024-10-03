from django.contrib import admin
from .models import Members,Hostels,Blocks,Beds,Leaved_person,In_out
# Register your models here.
admin.site.register(Members)
admin.site.register(Hostels)
admin.site.register(Blocks)
admin.site.register(Beds)
admin.site.register(Leaved_person)
admin.site.register(In_out)