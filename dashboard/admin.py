from django.contrib import admin
from .models import *
from django.utils.html import format_html

# =====================================================
# CLIENT
# =====================================================

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "email",
        "phone",
        "company",
        "rating",
        "created_at",
    )

    search_fields = (
        "name",
        "email",
        "phone",
        "company",
    )

    list_filter = (
        "rating",
        "created_at",
    )

    ordering = ("-created_at",)

    readonly_fields = (
        "created_at",
        "updated_at",
    )




# =====================================================
# REVISION INLINE
# =====================================================

# class RevisionInline(admin.TabularInline):
#     model = RevisionRequest
#     extra = 0


# =====================================================
# PROJECT
# =====================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "client",
        "status",
        "price",
        "progress",
        "deadline",
        "deposit_received",
    )

    search_fields = (
        "name",
        "client__name",
        "client__email",
    )

    list_filter = (
        "status",
        "deposit_received",
        "deadline",
        "created_at",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    autocomplete_fields = (
        "client",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    # inlines = [RevisionInline]

    fieldsets = (
        (
            "Project",
            {
                "fields": (
                    "name",
                    "description",
                    "status",
                    "progress",
                )
            },
        ),
        (
            "Client & Team",
            {
                "fields": (
                    "client",
                )
            },
        ),
        (
            "Pricing",
            {
                "fields": (
                    "price",
                    "deposit_amount",
                    "deposit_received",
                    "deposit_received_at",
                )
            },
        ),
        (
            "Production",
            {
                "fields": (
                    "deadline",
                    "deliverables",
                    "revisions_included",
                )
            },
        ),
        (
            "Feedback",
            {
                "fields": (
                    "client_rating",
                )
            },
        ),
        (
            "System",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = (
        "mark_in_progress",
        "mark_completed",
    )

    @admin.action(description="Mark selected projects as In Progress")
    def mark_in_progress(self, request, queryset):
        queryset.update(status="in_progress")

    @admin.action(description="Mark selected projects as Completed")
    def mark_completed(self, request, queryset):
        queryset.update(status="completed")


# =====================================================
# REVISION REQUEST
# =====================================================

# @admin.register(RevisionRequest)
# class RevisionRequestAdmin(admin.ModelAdmin):

#     list_display = (
#         "project",
#         "revision_number",
#         "status",
#         "requested_by",
#         "created_at",
#     )

#     search_fields = (
#         "project__name",
#         "description",
#         "requested_by",
#     )

#     list_filter = (
#         "status",
#         "created_at",
#     )

#     ordering = ("-created_at",)

#     autocomplete_fields = (
#         "project",
#     )

#     readonly_fields = (
#         "created_at",
#     )



@admin.register(MediaCategory)
class MediaCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "item_count")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("order", "name")

    def item_count(self, obj):
        return obj.items.count()
    item_count.short_description = "Items"


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = (
        "thumb_preview", "title", "category", "media_type",
        "is_public", "is_featured", "uploaded_at",
    )
    list_display_links = ("thumb_preview", "title")
    list_filter = ("media_type", "category", "is_public", "is_featured")
    search_fields = ("title", "description", "project_reference")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("is_public", "is_featured")
    readonly_fields = ("uploaded_at", "updated_at", "preview")

    fieldsets = (
        (None, {
            "fields": ("title", "slug", "description", "category", "project_reference")
        }),
        ("Media", {
            "fields": ("media_type", "photo", "video_file", "embed_url", "thumbnail", "preview"),
            "description": "Fill in only the field that matches the media type you picked above.",
        }),
        ("Publishing", {
            "fields": ("is_public", "is_featured"),
        }),
        ("Timestamps", {
            "fields": ("uploaded_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def thumb_preview(self, obj):
        url = obj.display_thumbnail_url
        if url:
            return format_html(
                '<img src="{}" style="height:40px;width:60px;object-fit:cover;border-radius:4px;" />',
                url,
            )
        return "—"
    thumb_preview.short_description = ""

    def preview(self, obj):
        url = obj.display_thumbnail_url
        if url:
            return format_html('<img src="{}" style="max-height:200px;border-radius:6px;" />', url)
        return "Save the item to see a preview."
    preview.short_description = "Preview"
