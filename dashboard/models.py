from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Sum
from django.utils.functional import cached_property
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify


class Client(models.Model):
    """
    A real client record.

    A Client is created only after the client approves
    the videographer's proposal.
    """

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=255, blank=True)
    project_type = models.CharField(max_length=100, blank=True)

    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ],
        help_text="Client rating from 0 to 5."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def total_revenue(self):
    # """Calculate total revenue from all projects"""
        from django.db.models import Sum
        return self.projects.aggregate(
            total=Sum('price')
        )['total'] or 0

    # @property
    # def project_count(self):
    #     """Total number of projects"""
    #     return self.projects.count()
    
    # @property
    # def completed_count(self):
    #     """Number of completed projects"""
    #     return self.projects.filter(status='completed').count()


    # Clear cache when project is saved
    # @receiver(post_save, sender=Project)
    # @receiver(post_delete, sender=Project)
    # def clear_client_cache(sender, instance, **kwargs):
    #     """Clear client's cached revenue when project changes"""
    #     if hasattr(instance.client, '_total_revenue'):
    #         del instance.client._total_revenue

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.email})"






class Project(models.Model):
    """
    Real production project.

    IMPORTANT:
    This should only be created after the client approves
    the proposal.

    Project → Client
    Project → Videographer
    """

    STATUS_CHOICES = [
        ("approved", "Approved"),
        ("in_progress", "In Progress"),
        ("review", "In Review"),
        ("revision", "Awaiting Revisions"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    # ==========================================================
    # PROJECT INFORMATION
    # ==========================================================


    

    name = models.CharField(
        max_length=255
    )

    description = models.TextField(
        blank=True
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    deadline = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default="approved"
    )

    # ==========================================================
    # CLIENT
    # ==========================================================

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="projects"
    )



    # ==========================================================
    # DELIVERABLES
    # ==========================================================

    deliverables = models.TextField(
        blank=True
    )

    revisions_included = models.PositiveIntegerField(
        default=2
    )

    progress = models.PositiveIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        help_text="Project completion percentage."
    )

    # ==========================================================
    # PAYMENT
    # ==========================================================

    deposit_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    deposit_received = models.BooleanField(
        default=False
    )

    deposit_received_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # ==========================================================
    # CLIENT RATING
    # ==========================================================

    client_rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5),
        ]
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.client.name}"


class RevisionRequest(models.Model):
    """
    Revision requests belonging to a project.
    """

    STATUS_CHOICES = [
        ("included", "Included in Package"),
        ("used", "Used Revision"),
        ("billable", "Extra Revision (Billable)"),
        ("completed", "Completed"),
    ]

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="revisions"
    )

    revision_number = models.PositiveIntegerField()

    description = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="included"
    )

    requested_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Client or videographer"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project.name} - Revision #{self.revision_number}"





class MediaCategory(models.Model):
    """Buckets for the public gallery, e.g. Weddings, Corporate, Music Videos."""
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)
    order = models.PositiveIntegerField(default=0, help_text="Lower numbers show first in filter bar")

    class Meta:
        verbose_name_plural = "Media categories"
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MediaItem(models.Model):
    PHOTO = "photo"
    VIDEO_FILE = "video_file"
    VIDEO_EMBED = "video_embed"

    MEDIA_TYPE_CHOICES = [
        (PHOTO, "Photo"),
        (VIDEO_FILE, "Video (uploaded file)"),
        (VIDEO_EMBED, "Video (YouTube/Vimeo link)"),
    ]

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    description = models.TextField(blank=True)

    category = models.ForeignKey(
        MediaCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="items"
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES, default=PHOTO)

    # Storage options — only one of these gets used, depending on media_type
    photo = models.ImageField(upload_to="media_library/photos/%Y/%m/", blank=True, null=True)
    video_file = models.FileField(upload_to="media_library/videos/%Y/%m/", blank=True, null=True)
    embed_url = models.URLField(
        blank=True, help_text="Full YouTube or Vimeo URL, e.g. https://youtu.be/abc123"
    )
    thumbnail = models.ImageField(
        upload_to="media_library/thumbnails/%Y/%m/",
        blank=True, null=True,
        help_text="Required for videos. Optional for photos (falls back to the photo itself)."
    )

    # Optional link back to a client project. Kept as a plain text field here since I don't
    # have your actual Project model/app label — see README for how to swap this for a real
    # ForeignKey to your booking/Project model in a couple of lines.
    project_reference = models.CharField(
        max_length=150, blank=True,
        help_text="Optional — client/project name this media belongs to, e.g. 'Ade & Zara Wedding'."
    )

    is_public = models.BooleanField(
        default=False,
        help_text="Only public items appear in the gallery. Keep off until you're ready to publish."
    )
    is_featured = models.BooleanField(
        default=False, help_text="Featured items appear first / larger in the gallery."
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-uploaded_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while MediaItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                counter += 1
                slug = f"{base_slug}-{counter}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("media_library:item_detail", kwargs={"slug": self.slug})

    @property
    def is_video(self):
        return self.media_type in (self.VIDEO_FILE, self.VIDEO_EMBED)

    @property
    def display_thumbnail_url(self):
        if self.thumbnail:
            return self.thumbnail.url
        if self.media_type == self.PHOTO and self.photo:
            return self.photo.url
        return ""

    @property
    def embed_provider(self):
        """Returns 'youtube', 'vimeo', or None — used by the template to build an embed src."""
        if not self.embed_url:
            return None
        url = self.embed_url.lower()
        if "youtu" in url:
            return "youtube"
        if "vimeo" in url:
            return "vimeo"
        return None

    @property
    def embed_src(self):
        """A ready-to-use iframe src for the video, or '' if it can't be parsed."""
        import re

        if not self.embed_url:
            return ""
        provider = self.embed_provider
        if provider == "youtube":
            match = re.search(r"(?:youtu\.be/|v=|embed/)([\w-]{6,})", self.embed_url)
            return f"https://www.youtube.com/embed/{match.group(1)}" if match else ""
        if provider == "vimeo":
            match = re.search(r"vimeo\.com/(\d+)", self.embed_url)
            return f"https://player.vimeo.com/video/{match.group(1)}" if match else ""
        return ""
