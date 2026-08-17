"""
Django Admin configuration for Notifications and Projects.
Manages the dashboard message system and active projects.
"""

from django.contrib import admin
from .models import *




admin.site.register(Booking)
admin.site.register(ProjectType)
admin.site.register(CoverageType)
admin.site.register(FinalLength)
admin.site.register(DeliveryDeadline)
admin.site.register(BudgetRange)
admin.site.register(DepositOption)
admin.site.register(PaymentMethod)
admin.site.register(RevisionRound)
admin.site.register(DeliveryMethod)



@admin.register(SiteStat)
class SiteStatAdmin(admin.ModelAdmin):
    list_display = ("client_count", "scopes_signed", "avg_rating", "updated_at")
 
    def has_add_permission(self, request):
        # singleton — only the one row (pk=1) should ever exist
        return not SiteStat.objects.exists()
 
 
@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("hero_title", "about_heading", "updated_at")
    fieldsets = (
        ("Hero", {"fields": ("hero_pill_text", "hero_title", "hero_subtitle")}),
        ("Hero showcase card", {"fields": (
            "showcase_project_label", "showcase_project_name", "showcase_status_label",
            "showcase_completion_percent", "showcase_revisions_used",
            "showcase_revisions_total", "showcase_due_text",
        )}),
        ("About", {"fields": (
            "about_heading", "about_paragraph_1", "about_paragraph_2",
            "about_video", "about_video_poster",
        )}),
        ("Services intro", {"fields": ("services_heading", "services_paragraph")}),
        ("Testimonials intro", {"fields": ("testimonials_heading",)}),
        ("Contact", {"fields": (
            "contact_heading", "contact_paragraph", "contact_email",
            "contact_phone", "contact_locations",
        )}),
    )
 
    def has_add_permission(self, request):
        return not SiteContent.objects.exists()
 
 
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "icon_bg", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)
 
 
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_role", "rating", "order", "is_active")
    list_editable = ("order", "is_active")
    ordering = ("order",)
 
 
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at", "is_read")
    list_filter = ("is_read", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")