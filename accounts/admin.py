from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
        "username",
        "full_name",
        "email",
    )

    search_fields = (
        "username",
        "full_name",
        "email",
    )

    list_filter = (
        "is_active",
    )

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "profile_picture",
                    "is_verified",
                )
            },
        ),
    )