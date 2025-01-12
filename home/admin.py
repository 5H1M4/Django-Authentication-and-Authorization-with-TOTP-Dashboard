from django.contrib import admin
from .models import Member

class MemberAdmin(admin.ModelAdmin):
    list_display = ("firstname", "lastname", "country")  # Ensure correct indentation

# Register the Member model with the MemberAdmin
admin.site.register(Member, MemberAdmin)
