
# ---------------------------------------------------------------------------
# Landing page models — add these classes to your existing media_library/models.py
# (or leave this as a separate models_landing.py and add
#  `from .models_landing import *` at the bottom of models.py)
# ---------------------------------------------------------------------------
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class ProjectType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Project Type"
        verbose_name_plural = "Project Types"

    def __str__(self):
        return self.name


class CoverageType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Coverage Type"
        verbose_name_plural = "Coverage Types"

    def __str__(self):
        return self.name


class FinalLength(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Final Video Length"
        verbose_name_plural = "Final Video Lengths"

    def __str__(self):
        return self.name


class DeliveryDeadline(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Delivery Deadline"
        verbose_name_plural = "Delivery Deadlines"

    def __str__(self):
        return self.name


class BudgetRange(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Budget Range"
        verbose_name_plural = "Budget Ranges"

    def __str__(self):
        return self.name


class DepositOption(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Deposit Option"
        verbose_name_plural = "Deposit Options"

    def __str__(self):
        return self.name


class PaymentMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RevisionRound(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "Revision Round"
        verbose_name_plural = "Revision Rounds"

    def __str__(self):
        return self.name


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Booking(models.Model):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        PROPOSAL_SENT = "proposal_sent", "Proposal Sent"
        CLIENT_APPROVED = "client_approved", "Client Approved"
        COMPLETED = "completed", "Completed"
        REJECTED = "rejected", "Rejected"



    # ---- Step 1: Client Information ----
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone_number = models.CharField(max_length=30)
    company = models.CharField(max_length=255, blank=True)
    project_type = models.ForeignKey(
        ProjectType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # ---- Step 2: Project Details ----
    project_description = models.TextField(blank=True)

    # ---- Step 3: Coverage Requirements ----
    coverage_type = models.ForeignKey(
        CoverageType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    coverage_ceremony = models.BooleanField(default=False)
    coverage_speeches = models.BooleanField(default=False)
    coverage_performances = models.BooleanField(default=False)
    coverage_interviews = models.BooleanField(default=False)
    coverage_product_shots = models.BooleanField(default=False)
    coverage_drone_footage = models.BooleanField(default=False)
    coverage_behind_the_scenes = models.BooleanField(default=False)
    coverage_guest_reactions = models.BooleanField(default=False)
    coverage_decoration = models.BooleanField(default=False)
    coverage_social_media_content = models.BooleanField(default=False)
    coverage_highlight_moments = models.BooleanField(default=False)
    coverage_other = models.BooleanField(default=False)
    special_requests = models.TextField(blank=True)

    # ---- Step 4: Event Schedule ----
    event_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    coverage_hours = models.DecimalField(max_digits=4, decimal_places=1, blank=True, null=True)

    # ---- Step 5: Venue Information ----
    venue_name = models.CharField(max_length=255)
    venue_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    maps_link = models.URLField(blank=True)

    # ---- Step 6: Deliverables ----
    # NOTE: template checkboxes currently have no `name=` attrs — add these:
    deliverable_highlight_video = models.BooleanField(default=False)     # name="deliverable_highlight_video"
    deliverable_full_event_video = models.BooleanField(default=False)    # name="deliverable_full_event_video"
    deliverable_social_reels = models.BooleanField(default=False)        # name="deliverable_social_reels"
    deliverable_youtube_version = models.BooleanField(default=False)     # name="deliverable_youtube_version"
    deliverable_short_documentary = models.BooleanField(default=False)   # name="deliverable_short_documentary"
    deliverable_raw_footage = models.BooleanField(default=False)         # name="deliverable_raw_footage"
    deliverable_edited_photos = models.BooleanField(default=False)       # name="deliverable_edited_photos"
    deliverable_promo_trailer = models.BooleanField(default=False)       # name="deliverable_promo_trailer"
    final_length = models.ForeignKey(
        FinalLength,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    deadline = models.ForeignKey(
    DeliveryDeadline,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
)

    # ---- Step 7: Budget & Payment ----
    budget = models.ForeignKey(
        BudgetRange,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    deposit = models.ForeignKey(
        DepositOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    payment_method = models.ForeignKey(
        PaymentMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    revision_round = models.ForeignKey(
        RevisionRound,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # ---- Step 8: Additional Services ----
    drone_coverage = models.BooleanField(default=False)
    livestream = models.BooleanField(default=False)
    extra_camera_operator = models.BooleanField(default=False)
    photography = models.BooleanField(default=False)
    same_day_edit = models.BooleanField(default=False)
    teleprompter = models.BooleanField(default=False)
    lighting_setup = models.BooleanField(default=False)
    audio_recording = models.BooleanField(default=False)
    subtitle_captions = models.BooleanField(default=False)
    motion_graphics = models.BooleanField(default=False)

    # ---- Step 9: File Delivery ----
    delivery_method = models.ForeignKey(
        DeliveryMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # ---- Step 10: Additional Notes ----
    additional_notes = models.TextField(blank=True)

    # ---- Step 11: Terms & Agreement ----
    confirm_information = models.BooleanField(default=False)
    agree_booking_policy = models.BooleanField(default=False)
    confirm_deposit_policy = models.BooleanField(default=False)

    # ---- Internal tracking ----
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.PENDING,
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_bookings",
    )
    rejection_reason = models.TextField(blank=True)

    videographer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="videographer_bookings",
    )
    proposed_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
    )
    proposal_description = models.TextField(blank=True)
    deliverables = models.TextField(blank=True)
    timeline = models.TextField(blank=True)
    revisions_included = models.PositiveIntegerField(default=2)
    proposal_sent_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    client_approved_at = models.DateTimeField(
    null=True,
    blank=True
)

    approved_at = models.DateTimeField(
    null=True,
    blank=True
)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.project_type} ({self.event_date})"

    @property
    def days_until_event(self):
        from django.utils import timezone
        return (self.event_date - timezone.now().date()).days

class SiteStat(models.Model):
    """
    Singleton row holding the numbers shown in the hero section
    (hero_client_count, hero_scopes_signed, hero_avg_rating).
 
    client_count and scopes_signed are computed live in views_landing.py
    on every request (get_live_hero_stats) — the fields here act as a
    curated fallback / cache only, kept in sync by recompute_from_data()
    if you ever want to run it on a schedule instead of computing live.
    """
    client_count = models.PositiveIntegerField(default=0)
    scopes_signed = models.PositiveIntegerField(default=0)
    avg_rating = models.DecimalField(max_digits=2, decimal_places=1, default=5.0)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name = "Site stat"
        verbose_name_plural = "Site stats"
 
    def __str__(self):
        return f"Site stats (updated {self.updated_at:%Y-%m-%d})"
 
    def save(self, *args, **kwargs):
        # enforce singleton — always row pk=1
        self.pk = 1
        super().save(*args, **kwargs)
 
    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
 
    @classmethod
    def recompute_from_data(cls):
        """
        Call this from a management command or cron to refresh the cached
        fallback values from real data (client_count, scopes_signed,
        avg_rating). Not required for the live hero display, which reads
        straight from Client/Project on every request — this just keeps
        the fallback row current in case live computation is ever swapped
        out for a cached read.
 
        - client_count: total Client rows.
        - scopes_signed: completed Project rows.
        - avg_rating: average of Project.client_rating (only counts projects
          that have actually been rated — unrated projects don't drag the
          average down to 0).
        """
        from django.db.models import Avg
        from .models import Client, Project  # adjust import path if these live elsewhere
 
        stat = cls.load()
        stat.client_count = Client.objects.count()
        stat.scopes_signed = Project.objects.filter(status="completed").count()
 
        avg = Project.objects.filter(
            client_rating__isnull=False
        ).aggregate(avg=Avg("client_rating"))["avg"]
        if avg is not None:
            stat.avg_rating = round(avg, 1)
 
        stat.save()
        return stat
 
 
class SiteContent(models.Model):
    """
    Singleton row holding the editable copy for the hero, the hero's
    example project card, and the About write-up. Everything here is
    text a non-developer should be able to change from /admin/ without
    touching the template.
    """
    # Hero
    hero_pill_text = models.CharField(
        max_length=100, default="Built for freelance videographers"
    )
    hero_title = models.CharField(
        max_length=150, default="Never argue over revisions again."
    )
    hero_subtitle = models.TextField(
        default="Scope Agreement helps freelance videographers clearly define "
                "project scope, track revisions automatically, and keep every "
                "client on the same page."
    )
 
    # Hero showcase card (the "Ade & Kemi — Wedding Film" example)
    showcase_project_label = models.CharField(max_length=50, default="Active Project")
    showcase_project_name = models.CharField(max_length=150, default="Ade & Kemi — Wedding Film")
    showcase_status_label = models.CharField(max_length=50, default="On Track")
    showcase_completion_percent = models.PositiveSmallIntegerField(
        default=72, validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    showcase_revisions_used = models.PositiveSmallIntegerField(default=2)
    showcase_revisions_total = models.PositiveSmallIntegerField(default=3)
    showcase_due_text = models.CharField(max_length=50, default="Due in 9 days")
 
    # About section
    about_heading = models.CharField(
        max_length=150, default="Built by a videographer, for videographers"
    )
    about_paragraph_1 = models.TextField(
        default="Scope Agreement started as a fix for my own frustration — endless "
                "\"just one more tweak\" requests, clients unclear on how many "
                "revisions were left, and revenue quietly slipping through the "
                "cracks. After years shooting weddings, corporate work, and music "
                "videos, I built the tool I wished I'd had from day one: one place "
                "to set scope, track revisions, and get paid for the extra work."
    )
    about_paragraph_2 = models.TextField(
        default="Today it's used by videographers across Lagos, Johannesburg, and "
                "Accra to keep every project on track and every client on the same page."
    )
    about_video = models.FileField(
        upload_to="site_content/videos/",
        blank=True,
        null=True,
        help_text="MP4 (or other browser-supported video format) for the About section. "
                   "Falls back to the default static video if empty and about_video_url is also empty.",
    )
    about_video_poster = models.ImageField(
        upload_to="site_content/video_posters/",
        blank=True,
        null=True,
        help_text="Poster image shown before the video plays / while it loads. Optional.",
    )
 
    # Services section intro
    services_heading = models.CharField(max_length=100, default="What I render")
    services_paragraph = models.TextField(
        default="From first consultation to final delivery, here's what I produce for "
                "clients — all managed through Scope Agreement so nothing gets lost "
                "along the way."
    )
 
    # Testimonials section intro
    testimonials_heading = models.CharField(max_length=100, default="What videographers are saying")
 
    # Contact section
    contact_heading = models.CharField(max_length=100, default="Talk to the team")
    contact_paragraph = models.TextField(
        default="Questions about Scope Agreement, enterprise, or partnerships? "
                "Send us a message and we'll respond within one business day."
    )
    contact_email = models.EmailField(default="hello@scopeagreement.app")
    contact_phone = models.CharField(max_length=30, default="+234 803 000 0000")
    contact_locations = models.CharField(
        max_length=150, default="Lagos · Johannesburg · Accra",
        help_text="Free text, shown as-is next to the location pin icon.",
    )
 
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name = "Site content"
        verbose_name_plural = "Site content"
 
    def __str__(self):
        return f"Site content (updated {self.updated_at:%Y-%m-%d})"
 
    def save(self, *args, **kwargs):
        self.pk = 1  # singleton
        super().save(*args, **kwargs)
 
    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
 
 
class Service(models.Model):
    """One card in the "What I render" services grid."""
    ICON_BG_CHOICES = [
        ("bg-primary-soft", "Primary"),
        ("bg-success-soft", "Success"),
        ("bg-warning-soft", "Warning"),
        ("bg-info-soft", "Info"),
        ("bg-danger-soft", "Danger"),
    ]
 
    icon_class = models.CharField(
        max_length=50,
        help_text="Bootstrap icon class, e.g. 'bi-heart', 'bi-camera-reels'",
    )
    icon_bg = models.CharField(max_length=20, choices=ICON_BG_CHOICES, default="bg-primary-soft")
    title = models.CharField(max_length=100)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
 
    class Meta:
        ordering = ["order", "id"]
 
    def __str__(self):
        return self.title
 
 
class Testimonial(models.Model):
    """One card in the "Loved by creators" section."""
    quote = models.TextField()
    author_name = models.CharField(max_length=100)
    author_role = models.CharField(max_length=150, help_text="e.g. 'Wedding Filmmaker, Lagos'")
    rating = models.PositiveSmallIntegerField(
        default=5, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
 
    class Meta:
        ordering = ["order", "id"]
 
    def __str__(self):
        return f"{self.author_name} ({self.rating}★)"
 
    @property
    def avatar_letter(self):
        return self.author_name[:1].upper() if self.author_name else "?"
 
    @property
    def stars_range(self):
        """Lets the template do {% for _ in t.stars_range %} to draw N filled stars."""
        return range(self.rating)
 
 
class ContactMessage(models.Model):
    """Submissions from the #contactForm on the landing page."""
    name = models.CharField(max_length=150)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
 
    class Meta:
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%Y-%m-%d}"
 