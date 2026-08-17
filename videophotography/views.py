import logging
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.db import models
from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
PAGE_SIZE = 12
from django.utils import timezone

from .forms import BookingForm
from .models import *
from dashboard.models import *
from dashboard.forms import MediaItemForm
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.core.mail import EmailMessage, send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.http import JsonResponse

logger = logging.getLogger(__name__)

ACTIVE_PROJECT_STATUSES = ["approved", "in_progress", "review", "revision"]
 
HERO_CARD_COUNT = 2
 
 
def _days_left_info(deadline):
    days_left = (deadline - timezone.localdate()).days
    return {
        "days_left": days_left,
        "days_overdue": abs(days_left) if days_left < 0 else None,
    }
 
 
def get_showcase_projects(limit=HERO_CARD_COUNT):
    """
    Picks up to `limit` real Projects to feature in the hero card stack —
    the most recently updated ones that are currently active. Returns an
    empty list if there are no active projects yet (e.g. a brand-new site
    with an empty dashboard) — the template falls back to SiteContent's
    curated example card in that case.
 
    Status is deliberately shown to visitors as a flat "Ongoing" rather
    than the internal STATUS_CHOICES label (e.g. "Awaiting Revisions") —
    that's dashboard-facing language, not marketing copy.
    """
    projects = (
        Project.objects.filter(status__in=ACTIVE_PROJECT_STATUSES)
        .select_related("client")
        .order_by("-updated_at")[:limit]
    )
    showcase_list = []
    for project in projects:
        entry = {"project": project, "status_label": "Ongoing"}
        entry.update(_days_left_info(project.deadline))
        showcase_list.append(entry)
    return showcase_list
 
 
def get_live_hero_stats():
    """
    Computes client_count, scopes_signed, and avg_rating straight from
    Client/Project, live, on every request — no dependency on the
    recompute_site_stats management command or a stale cached SiteStat
    snapshot. avg_rating is None when no project has been rated yet, so
    the caller can fall back to the curated SiteStat value in that case.
    """
    client_count = Client.objects.count()
    scopes_signed = Project.objects.filter(status="completed").count()
    avg_rating = Project.objects.filter(
        client_rating__isnull=False
    ).aggregate(avg=Avg("client_rating"))["avg"]
    return client_count, scopes_signed, (round(avg_rating, 1) if avg_rating is not None else None)
 
 
def landing(request):
    site_stats = SiteStat.load()  # curated fallback if live queries ever need one
    content = SiteContent.load()
 
    live_client_count, live_scopes_signed, live_avg_rating = get_live_hero_stats()
    showcase_list = get_showcase_projects()
 
    context = {
        "hero_client_count": live_client_count,
        "hero_scopes_signed": live_scopes_signed,
        "hero_avg_rating": live_avg_rating if live_avg_rating is not None else site_stats.avg_rating,
        "content": content,
        "showcase_list": showcase_list,
        "services": Service.objects.filter(is_active=True),
        "testimonials": Testimonial.objects.filter(is_active=True),
    }
    return render(request, "website/index.html", context)
    
 
@require_POST
@csrf_protect
def contact_submit(request):
    """
    JSON endpoint for the #contactForm in index.html.
    Expects fetch(..., { method: 'POST', body: JSON.stringify({name, email, message}) }).
    See static/media_library/js/contact-form.js for the matching frontend.
 
    On success this does two things by email:
    1. Notifies CONTACT_INBOX_EMAIL, with Reply-To set to the visitor's address
       so you can hit "reply" in your inbox and it goes straight to them.
    2. Sends the visitor a short confirmation so they know it went through.
 
    Requires EMAIL_* settings to be configured — see settings_email_snippet.py.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        data = request.POST
 
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()
 
    errors = {}
    if not name:
        errors["name"] = "Please enter your name."
    if not message:
        errors["message"] = "Please enter a message."
    if not email:
        errors["email"] = "Please enter your email."
    else:
        try:
            validate_email(email)
        except ValidationError:
            errors["email"] = "That email address doesn't look right."
 
    if errors:
        return JsonResponse({"ok": False, "errors": errors}, status=400)
 
    ContactMessage.objects.create(name=name, email=email, message=message)
 
    inbox = getattr(settings, "CONTACT_INBOX_EMAIL", settings.DEFAULT_FROM_EMAIL)
 
    # Notify the team inbox — Reply-To is the visitor's address so a reply
    # from your inbox goes straight back to them.
    try:
        EmailMessage(
            subject=f"New contact form message from {name}",
            body=f"From: {name} <{email}>\n\n{message}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[inbox],
            reply_to=[email],
        ).send(fail_silently=False)
    except Exception:
        # Message is already saved in the DB even if the email send fails —
        # log it so a broken mail server doesn't fail silently forever.
        logger.exception("Failed to send contact-form notification email to %s", inbox)
 
    # Confirmation email back to the visitor. Kept separate and best-effort:
    # a hiccup here shouldn't affect the team notification above.
    try:
        send_mail(
            subject="We got your message",
            message=(
                f"Hi {name},\n\n"
                "Thanks for reaching out — we've received your message and will "
                "get back to you within one business day.\n\n"
                f"What you sent us:\n{message}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=True,
        )
    except Exception:
        logger.exception("Failed to send contact-form confirmation email to %s", email)
 
    return JsonResponse({"ok": True, "message": "Thanks — we'll get back to you within a business day."})
 

User = get_user_model()
 
 
def send_booking_confirmation_email(booking):
    event_date_str = f"{booking.event_date:%b} {booking.event_date.day}, {booking.event_date.year}"
    subject = f"Booking received — {booking.get_project_type_display()} on {event_date_str}"
 
    context = {"booking": booking}
    text_body = render_to_string("booking/email/booking-confirmation.txt", context)
    html_body = render_to_string("booking/email/booking-confirmation.html", context)
 
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.email],
    )
    email.attach_alternative(html_body, "text/html")
    email.send(fail_silently=False)
 
 
def booking_create_view(request):
    """Public, no-login page rendering the 11-step wizard, scoped to one
    freelancer's own public booking link (e.g. /book/victor/). The wizard
    steps are handled entirely client-side; the whole form posts once,
    on the final step."""
 
    form = BookingForm(request.POST or None)
 
    if request.method == "POST":
        if form.is_valid():
            booking = form.save(commit=False)
            booking.save()
 
            try:
                send_booking_confirmation_email(booking)
            except Exception:
                # Don't let a broken email backend take down the booking flow —
                # the booking is already saved; the client still sees success
                # on-screen. Swap this for proper logging in production.
                messages.warning(
                    request,
                    "Your booking was saved, but we couldn't send the confirmation email."
                )
            else:
                messages.success(
                    request,
                    "Your booking request has been submitted. We've sent a confirmation to your email."
                )
 
            return redirect("media_library:booking_success", pk=booking.pk)
 
    return render(
        request,
        "booking/booking.html",
        {"form": form},
    )
 
 
def booking_success_view(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
 
    return render(
        request,
        "booking/booking-successfull.html",
        {"booking": booking},
    )
 


# ---------------------------------------------------------------------------
# Public gallery
# ---------------------------------------------------------------------------

def gallery(request):
    """Public media library page: filterable grid of published photos/videos."""
    items = MediaItem.objects.filter(is_public=True).select_related("category")

    category_slug = request.GET.get("category")
    if category_slug:
        items = items.filter(category__slug=category_slug)

    media_type = request.GET.get("type")
    if media_type in (MediaItem.PHOTO, MediaItem.VIDEO_FILE, MediaItem.VIDEO_EMBED):
        items = items.filter(media_type=media_type)
    elif media_type == "video":
        items = items.filter(media_type__in=[MediaItem.VIDEO_FILE, MediaItem.VIDEO_EMBED])

    paginator = Paginator(items, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "categories": MediaCategory.objects.all(),
        "active_category": category_slug or "",
        "active_type": media_type or "",
    }
    return render(request, "website/gallery.html", context)


def item_detail(request, slug):
    item = get_object_or_404(MediaItem, slug=slug, is_public=True)
    related = (
        MediaItem.objects.filter(is_public=True, category=item.category)
        .exclude(pk=item.pk)[:4]
    )
    return render(request, "website/item_detail.html", {"item": item, "related": related})
