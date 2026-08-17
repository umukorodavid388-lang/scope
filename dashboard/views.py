"""
Dashboard Overview View
Complete dashboard with all stats, charts, and data
Matches the dashboard/overview.html template exactly
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum, Avg, F
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from datetime import timedelta, datetime
import json
from decimal import Decimal, InvalidOperation
from django.conf import settings
import calendar

from .models import *
from .forms import MediaItemForm
from videophotography.models import *

PAGE_SIZE = 12

def _json_safe(value):
    """Recursively convert Decimal values to JSON-serializable primitives."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value

"""
Complete 3-Stage Approval Workflow

Stage 1: CLIENT BOOKING REQUEST
    → Booking model created (status: pending)
    → Admin notified

Stage 2: ADMIN APPROVAL + VIDEOGRAPHER PROPOSAL
    → Admin approves booking
    → Videographer adds details/proposal
    → Email sent to client with proposal

Stage 3: CLIENT APPROVAL
    → Client approves proposal
    → Client record created
    → Project record created
    → Client saved to dashboard
"""


# ============================================
# STAGE 2: ADMIN APPROVAL & VIDEOGRAPHER PROPOSAL
# ============================================

@login_required
def booking_detail_view(request, pk):
    """Show booking details"""

    booking = get_object_or_404(Booking, pk=pk)
        
        # Check if user is admin
    if not request.user.is_staff:
        messages.error(request, "Only admins can review bookings")
        return redirect('dashboard_overview')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'approve':
            booking.status = 'approved'
            booking.approved_by = request.user
            booking.approved_at = timezone.now()
            booking.save()
            
            messages.success(request, f"Booking from {booking.full_name} approved!")
            
            # # Send email to videographer(s) to add proposal
            # send_videographer_review_email(booking)
            
            return redirect('videographer_proposal_form', booking_pk=booking.pk)
        
        elif action == 'reject':
            reason = request.POST.get('reason', 'No reason provided')
            booking.status = 'rejected'
            booking.rejection_reason = reason
            booking.save()
            
            messages.success(request, "Booking rejected.")
            
            # Send email to client
            send_client_rejection_email(booking, reason)
            
            return redirect('dashboard_overview')

    
    
    return render(
        request,
        "dashboard/project-details.html",
        {"booking": booking},
    )





@login_required
def booking_approve_view(request, pk):
    """Approve a booking"""
    
    user = request.user
    booking = get_object_or_404(Booking, pk=pk)
    
    
    if request.method == "POST":
        booking.status = Booking.Status.APPROVED
        booking.approved_at = timezone.now()
        booking.save(update_fields=["status", "approved_at", "updated_at"])
        
        messages.success(request, f"Booking from {booking.full_name} approved.")
        
        return redirect("booking_detail", pk=booking.pk)
    
    return redirect("booking_detail", pk=booking.pk)


@login_required
def booking_reject_view(request, pk):
    """Reject a booking"""
    
    user = request.user
    booking = get_object_or_404(Booking, pk=pk)
    
    if request.method == "POST":
        booking.status = Booking.Status.REJECTED
        booking.save(update_fields=["status", "updated_at"])
        
        messages.success(request, f"Booking from {booking.full_name} rejected.")
        
        return redirect("booking_detail", pk=booking.pk)
    
    return redirect("booking_detail", pk=booking.pk)




def send_client_rejection_email(booking, reason):
    """Send rejection email to client"""
    
    subject = f"Booking Request Update: {booking.full_name}"
    
    html_content = f"""
    <!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .header {
            border-bottom: 3px solid #E74C3C;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }
        .header h1 {
            margin: 0;
            color: #E74C3C;
            font-size: 24px;
        }
        .alert-box {
            background-color: #fadbd8;
            border-left: 4px solid #E74C3C;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
            color: #78281f;
        }
        .content {
            margin: 20px 0;
        }
        .content p {
            margin: 10px 0;
        }
        .reason-box {
            background-color: #f8f9fa;
            border-left: 4px solid #E74C3C;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .reason-label {
            font-weight: 600;
            color: #666;
            margin-bottom: 10px;
        }
        .reason-text {
            color: #333;
            line-height: 1.6;
        }
        .alternatives {
            background-color: #e8f8f5;
            border-left: 4px solid #16A085;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .alternatives h3 {
            margin-top: 0;
            color: #16A085;
        }
        .alternatives ol {
            margin: 10px 0;
            padding-left: 20px;
        }
        .alternatives li {
            margin: 8px 0;
        }
        .contact-info {
            background-color: #eaf2f8;
            border-left: 4px solid #3498DB;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .contact-info h3 {
            margin-top: 0;
            color: #3498DB;
        }
        .footer {
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            font-size: 12px;
            color: #666;
        }
        .emoji {
            font-size: 24px;
            margin-right: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Booking Request Status Update</h1>
        </div>
        
        <div class="alert-box">
            <p><strong>Unfortunately,</strong> we are unable to proceed with your {{ booking.project_type }} booking request at this time.</p>
        </div>
        
        <div class="content">
            <p>Hi {{ booking.full_name }},</p>
            
            <p>Thank you for choosing us for your upcoming event. We truly appreciate your interest in our videography services.</p>
            
            <div class="reason-box">
                <div class="reason-label">Reason:</div>
                <div class="reason-text">
                    {{ reason }}
                </div>
            </div>
            
            <div class="alternatives">
                <h3><span class="emoji">💡</span>What You Can Do</h3>
                <ol>
                    <li><strong>Check Different Dates:</strong> If your event date is flexible, we may be available for other dates</li>
                    <li><strong>Adjust Your Scope:</strong> Some clients find success by modifying their project scope or deliverables</li>
                    <li><strong>Get on the Waitlist:</strong> We maintain a waitlist for popular dates and may be able to accommodate you</li>
                    <li><strong>Contact Us:</strong> Reach out directly to discuss alternative solutions or future opportunities</li>
                </ol>
            </div>
            
            <div class="contact-info">
                <h3><span class="emoji">📞</span>Let's Stay Connected</h3>
                <p>While we can't take on this project, we'd love to work with you in the future. Please feel free to:</p>
                <ul>
                    <li>Email us with alternative dates or a revised project scope</li>
                    <li>Call to discuss how we might help with a future project</li>
                    <li>Follow us on social media for updates and new services</li>
                </ul>
                <p>We appreciate the opportunity to have been considered and wish you the very best with your event!</p>
            </div>
            
            <p style="margin-top: 30px; font-style: italic; color: #666;">Best of luck with your upcoming event!</p>
        </div>
        
        <div class="footer">
            <p>This email is in response to your booking request submitted on [date].</p>
            <p>&copy; 2026 Videography Studio. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
    """
    
    send_mail(
        subject=subject,
        message=f"Booking declined",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        html_message=html_content,
        fail_silently=True
    )



from decimal import Decimal, InvalidOperation
@login_required
def videographer_proposal_form(request, booking_pk):
    """
    Videographer adds proposal details to booking
    This turns the booking into a quotation/proposal
    """

    booking = get_object_or_404(Booking, pk=booking_pk)

    if not request.user.is_staff:
        messages.error(request, "Only videographers can add proposals")
        return redirect("dashboard_overview")

    allowed_statuses = {
        getattr(Booking.Status, "APPROVED", "approved"),
        getattr(Booking.Status, "PROPOSAL_SENT", "proposal_sent"),
    }

    if booking.status not in allowed_statuses:
        messages.error(request, "This booking is not ready for a proposal.")
        return redirect("booking_list")

    if request.method == "POST":
        proposed_price_raw = request.POST.get("proposed_price", "").strip()

        if not proposed_price_raw:
            messages.error(request, "Please enter a proposed price.")
            return render(request, "dashboard/proposal_form.html", {"booking": booking})

        try:
            proposed_price = Decimal(proposed_price_raw)
        except (InvalidOperation, ValueError):
            messages.error(request, "Proposed price must be a valid number.")
            return render(request, "dashboard/proposal_form.html", {"booking": booking})

        booking.videographer = request.user
        booking.proposed_price = proposed_price
        booking.proposal_description = request.POST.get("proposal_description", "")
        booking.deliverables = request.POST.get("deliverables", "")
        booking.timeline = request.POST.get("timeline", "")
        booking.revisions_included = request.POST.get("revisions_included", "2")
        booking.status = getattr(Booking.Status, "PROPOSAL_SENT", "proposal_sent")
        booking.proposal_sent_at = timezone.now()
        booking.save()

        messages.success(request, "Proposal sent to client!")
        send_client_proposal_email(booking)

        return redirect("dashboard_overview")

    return render(request, "dashboard/proposal_form.html", {"booking": booking})

def send_client_proposal_email(booking):
    """Send proposal to client for approval"""
    
    subject = f"Your Video Project Proposal - {booking.full_name}"
    
    html_content = f"""
    <h2>Your Video Project Proposal</h2>
    <p>Hi {booking.full_name},</p>
    
    <p>Thank you for your interest! We've reviewed your event and prepared a proposal tailored to your needs.</p>
    
    <h3>Proposal Summary:</h3>
    <p><strong>Event:</strong> {booking.project_type} - {booking.event_date}</p>
    <p><strong>Proposed Price:</strong> ₦{booking.proposed_price:,.0f}</p>
    
    <h3>What's Included:</h3>
    <p>{booking.deliverables}</p>
    
    <h3>Timeline:</h3>
    <p>{booking.timeline}</p>
    
    <h3>Revisions:</h3>
    <p>{booking.revisions_included} revisions included</p>
    
    <h3>Full Proposal Description:</h3>
    <p>{booking.proposal_description}</p>
    
    <p>
        <strong>
            <a href="http://localhost:8000/dashboard/client/approve-proposal/{booking.pk}/">
                ✅ APPROVE PROPOSAL
            </a>
        </strong>
    </p>
    
    <p>If you have any questions, please reply to this email.</p>
    """
    
    send_mail(
        subject=subject,
        message=f"Your proposal is ready", 
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        html_message=html_content,
        fail_silently=True,
    )


# ============================================
# STAGE 3: CLIENT APPROVAL → CREATE CLIENT + PROJECT
# ============================================

def client_approve_proposal(request, booking_pk):
    """
    Client approves proposal
    ⭐ THIS IS WHEN CLIENT & PROJECT ARE CREATED
    """
    
    booking = get_object_or_404(Booking, pk=booking_pk, status='proposal_sent')
    
    if request.method == "POST":
        # ⭐ STAGE 3: CREATE CLIENT RECORD
        client, created = Client.objects.get_or_create(
            email=booking.email,
            defaults={
                'name': booking.full_name, 'phone': booking.phone_number, 'company': getattr(booking, 'company', ''), 'project_type': booking.project_type,
            }
        )
        
        # ⭐ STAGE 3: CREATE PROJECT RECORD
        project = Project.objects.create(
            client=client,
            name=f"{booking.project_type} - {booking.full_name}",
            description=booking.project_description,
            status='approved',
            price=booking.proposed_price or 0,
            deadline=booking.event_date,
            revisions_included=booking.revisions_included,
            deliverables=booking.deliverables,
        )
        
        # Update booking to show client approved
        booking.status = 'client_approved'
        booking.client_approved_at = timezone.now()
        booking.save()
        
        messages.success(request, "Proposal approved! Project created.")
        
        # Send confirmation emails
        send_client_approval_confirmation_email(booking, project)
        send_admin_project_created_email(booking, project)
        
        return redirect('project_detail', pk=project.pk)
    
    return render(request, 'dashboard/approve_proposal.html', {'booking': booking})


def send_client_approval_confirmation_email(booking, project):
    """Send confirmation to client"""
    
    subject = f"✅ Project Approved! - {project.name}"
    
    html_content = f"""
    <h2>Project Approved!</h2>
    <p>Hi {booking.full_name},</p>
    
    <p>Great news! Your proposal has been approved and your project is now active.</p>
    
    <h3>Project Details:</h3>
    <p><strong>Project Name:</strong> {project.name}</p>
    <p><strong>Total Cost:</strong> ₦{project.price:,.0f}</p>
    <p><strong>Deadline:</strong> {project.deadline}</p>
    <p><strong>Revisions Included:</strong> {project.revisions_included}</p>
    
    <p>
        <a href="http://localhost:8000/dashboard/client/project/{project.pk}/">
            View Your Project
        </a>
    </p>
    
    <p>We'll keep you updated throughout the production process.</p>
    """
    
    send_mail(
        subject=subject,
        message=f"Your project {project.name} is approved",
        from_email='settings.DEFAULT_FROM_EMAIL',
        recipient_list=[booking.email],
        html_message=html_content,
        fail_silently=True
    )


def send_admin_project_created_email(booking, project):
    """Send notification to admin that project is now active"""
    
    subject = f"✅ New Active Project: {project.name}"
    
    html_content = f"""
    <h2>New Active Project</h2>
    
    <p><strong>Project:</strong> {project.name}</p>
    <p><strong>Client:</strong> {project.client.name}</p>
    <p><strong>Amount:</strong> ₦{project.price:,.0f}</p>
    <p><strong>Deadline:</strong> {project.deadline}</p>
    
    <p>
        <a href="http://localhost:8000/admin/videophotography/project/{project.pk}/change/">
            View in Admin
        </a>
    </p>
    """
    
    send_mail(
        subject=subject,
        message=f"New project created: {project.name}",
        from_email='settings.DEFAULT_FROM_EMAIL',
        recipient_list=['davidogheneothuke42@gmail.com'],
        html_message=html_content,
        fail_silently=True
    )


# ============================================
# DASHBOARD: ONLY SHOWS APPROVED PROJECTS
# ============================================

@login_required
def dashboard_overview(request):
    """
    Dashboard only shows projects that have been:
    1. Approved by admin
    2. Proposal sent to client
    3. ✅ CLIENT APPROVED (Client + Project created)
    """
    
    user = request.user
    
    # ⭐ ONLY SHOW PROJECTS (Client + Project records created)
    # NOT bookings - bookings are just requests
    projects = Project.objects.all()
    
    # Filter by videographer if multi-user
    # projects = projects.filter(videographer=user)
    
    # ============================================
    # TOP STAT CARDS
    # ============================================
    
    projects_completed_count = projects.filter(status='completed').count()
    active_clients_count = Client.objects.filter(projects__status='in_progress').distinct().count()
    
    avg_rating = projects.filter(
        status='completed',
        client_rating__isnull=False
    ).aggregate(avg=Avg('client_rating'))['avg'] or 0
    
    client_rating = f"{avg_rating:.1f}/5.0" if avg_rating else "—"
    
    # Response time (from booking to project created)
    bookings_completed = Booking.objects.filter(
        status='client_approved',
        created_at__isnull=False,
        client_approved_at__isnull=False
    )
    
    if bookings_completed.exists():
        total_hours = 0
        count = 0
        for booking in bookings_completed:
            delta = booking.client_approved_at - booking.created_at
            hours = delta.total_seconds() / 3600
            total_hours += hours
            count += 1
        
        avg_hours = total_hours / count
        avg_response_time = f"{int(avg_hours)}h" if avg_hours < 24 else f"{avg_hours/24:.1f}d"
    else:
        avg_response_time = "—"
    
    # ============================================
    # DYNAMIC STAT CARDS
    # ============================================
    
    pending_bookings = Booking.objects.filter(status='pending').count()
    in_progress_count = projects.filter(status=['approved','in_progress', 'revision', 'completed']).count()
    
    current_month = timezone.now().month
    current_year = timezone.now().year
    month_revenue = projects.filter(
        created_at__month=current_month,
        created_at__year=current_year
    ).aggregate(total=Sum('price'))['total'] or 0
    
    revenue_display = f"₦{month_revenue / 1_000_000:.1f}M" if month_revenue >= 1_000_000 else f"₦{month_revenue / 1_000:.0f}K"
    
    stat_cards = [
        {
            'label': 'Pending Bookings',
            'value': pending_bookings,
            'icon': 'bi-inbox',
            'accent': 'primary',
            'up': True,
            'trend': 'Awaiting review'
        },
        {
            'label': 'In Progress Projects',
            'value': in_progress_count,
            'icon': 'bi-play-circle',
            'accent': 'info',
            'up': True,
            'trend': 'Active work'
        },
        {
            'label': 'This Month Revenue',
            'value': revenue_display,
            'icon': 'bi-cash-coin',
            'accent': 'success',
            'up': True,
            'trend': 'From approved projects'
        },
        {
            'label': 'Client Satisfaction',
            'value': client_rating,
            'icon': 'bi-hand-thumbs-up',
            'accent': 'warning',
            'up': True,
            'trend': 'Based on reviews'
        }
    ]
    
    # ============================================
    # UPCOMING DEADLINES (Only from Projects)
    # ============================================
    
    today = timezone.now().date()
    upcoming_projects = projects.filter(
        deadline__gte=today
    ).select_related('client').order_by('deadline')[:10]
    
    upcoming = []
    for project in upcoming_projects:
        days_until = (project.deadline - today).days
        status_slug = str(project.status).lower().replace(' ', '-')
        
        upcoming.append({
            'name': project.name,
            'client': project.client,
            'deadline': project.deadline,
            'days_until_deadline': days_until,
            'status': project.get_status_display() if hasattr(project, 'get_status_display') else str(project.status),
            'status_slug': status_slug,
            'completion': getattr(project, 'progress', 0) or 0,
            'get_client_scope_url': getattr(project, 'get_client_scope_url', lambda: None)()
        })
    
    # ============================================
    # RECENT REVISION REQUESTS (From Projects)
    # ============================================
    
    recent_revisions = RevisionRequest.objects.filter(
        project__in=projects
    ).select_related('project', 'project__client').order_by('-created_at')[:5]
    
    recent_revisions_data = []
    for rev in recent_revisions:
        status_badge_slug = str(rev.status).lower().replace(' ', '-')
        
        recent_revisions_data.append({
            'number': getattr(rev, 'revision_number', 1) or 1,
            'project': rev.project,
            'created_at': rev.created_at,
            'description': getattr(rev, 'description', 'Revision request') or 'Revision request',
            'status': rev.get_status_display() if hasattr(rev, 'get_status_display') else str(rev.status),
            'status_badge_slug': status_badge_slug
        })
    
    # ============================================
    # CHART DATA
    # ============================================
    
    monthly_labels = []
    monthly_data = []
    
    for i in range(6, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_str = month_date.strftime('%b')
        monthly_labels.append(month_str)
        
        count = projects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        monthly_data.append(count)
    
    chart_monthly = {
        'labels': monthly_labels,
        'data': monthly_data,
    }
    
    # Revision usage
    revision_counts = {
        'included': RevisionRequest.objects.filter(
            project__in=projects,
            status='included'
        ).count(),
        'used': RevisionRequest.objects.filter(
            project__in=projects,
            status='used'
        ).count(),
        'billable': RevisionRequest.objects.filter(
            project__in=projects,
            status='billable'
        ).count(),
    }
    
    chart_revisions = {
        'labels': ['Included', 'Used', 'Billable'],
        'data': [
            revision_counts['included'],
            revision_counts['used'],
            revision_counts['billable']
        ],
        'colors': ['#0d6efd', '#198754', '#fd7e14']
    }
    
    # Revenue
    revenue_labels = []
    revenue_data = []
    
    for i in range(6, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_str = month_date.strftime('%b %y')
        revenue_labels.append(month_str)
        
        revenue = projects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        revenue_millions = revenue / 1_000_000 if revenue > 0 else 0
        revenue_data.append(float(revenue_millions))
    
    chart_revenue = {
        'labels': revenue_labels,
        'data': revenue_data,
    }
    
    context = {
        'projects_completed_count': projects_completed_count,
        'active_clients_count': active_clients_count,
        'client_rating': client_rating,
        'avg_response_time': avg_response_time,
        'stat_cards': stat_cards,
        'upcoming': upcoming,
        'recent_revisions': recent_revisions_data,
        'chart_monthly': json.dumps(_json_safe(chart_monthly)),
        'chart_revisions': json.dumps(_json_safe(chart_revisions)),
        'chart_revenue': json.dumps(_json_safe(chart_revenue)),
    }
    
    return render(request, "dashboard/overview.html", context)


# ============================================
# ADMIN DASHBOARD: SHOWS PENDING BOOKINGS
# ============================================

@login_required
def admin_dashboard(request):
    """
    Admin dashboard shows:
    - Pending bookings (awaiting review)
    - Proposals sent (awaiting client approval)
    - Active projects
    """
    
    if not request.user.is_staff:
        messages.error(request, "Admin access only")
        return redirect('dashboard')
    
    pending_bookings = Booking.objects.filter(status='pending').order_by('-created_at')
    proposal_bookings = Booking.objects.filter(status='proposal_sent').order_by('-proposal_sent_at')
    approved_projects = Project.objects.filter(status__in=['approved', 'in_progress']).order_by('-created_at')
    active_client = Client.objects.filter(projects__status=['approved','in_progress', 'revision', 'completed']).distinct()
    
    context = {
        'pending_bookings': pending_bookings[:10],
        'proposal_bookings': proposal_bookings[:10],
        'approved_projects': approved_projects[:10],
        'pending_count': pending_bookings.count(),
        'proposal_count': proposal_bookings.count(),
        'project_count': approved_projects.count(),
        'active_client_count': active_client.count(),
    }
    
    return render(request, 'dashboard/overview.html', context)


# ============================================
# BOOKING LIST: Only Pending/APPROVED bookings
# ============================================

@login_required
def booking_list_view(request):

    if not request.user.is_staff:
        messages.error(request, "Videographers only")
        return redirect("dashboard")

    bookings = Booking.objects.filter(
        status__in=["pending", "approved", "rejected", "proposal_sent"]
    ).order_by("-created_at")

    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if query:
        bookings = bookings.filter(
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(event_type__icontains=query)
        )

    if status_filter:
        bookings = bookings.filter(status=status_filter)


    paginator = Paginator(bookings, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/projects.html",
        {
            "page_obj": page_obj,
            "bookings": page_obj,
            "query": query,
            "status_filter": status_filter,
        },
    )




@login_required
def Task_list_view(request):
    ongoing_statuses = ["approved", "in_progress", "review", "revision"]

    projects = Project.objects.select_related("client").filter(
        status__in=ongoing_statuses
    ).order_by("-created_at")

    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    if query:
        projects = projects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(client__name__icontains=query)
        )

    if status_filter:
        projects = projects.filter(status=status_filter)

    paginator = Paginator(projects, 15)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "dashboard/task.html",
        {
            "page_obj": page_obj,
            "projects": page_obj,
            "query": query,
            "status_filter": status_filter,
            "statuses": [("", "All Ongoing Statuses")] + [
                (value, label) for value, label in Project.STATUS_CHOICES
                if value in ongoing_statuses
            ],
            "ongoing_statuses": ongoing_statuses,
        },
    )


@login_required
def task_detail_view(request, pk):
    ongoing_statuses = ["approved", "in_progress", "review", "revision"]
    project = get_object_or_404(Project, pk=pk)

    if project.status not in ongoing_statuses:
        messages.error(request, "Only ongoing tasks can be viewed here.")
        return redirect("dashboard_overview")

    return render(request, "dashboard/task_details.html", {"project": project, "ongoing_statuses": ongoing_statuses})



@login_required
def clients_list(request):
    """
    Show all clients that have projects in the dashboard.
    """

    clients = Client.objects.all().order_by('-created_at').prefetch_related('projects')

    clients = clients.annotate(project_count=Count('projects'))

    context = {
        'clients': clients,
    }

    return render(request, 'dashboard/clients.html', context)
 
 
# ============================================================================
# CLIENT DETAIL VIEW
# ============================================================================
 
@login_required
def client_detail(request, pk):
    """
    Show detailed view of a single client
    
    GET: Show client profile with all their projects
    """
    
    # Get the client
    client = get_object_or_404(Client, pk=pk)
    
    # Make sure user can only see their own clients
    # client_projects = client.projects.filter(request.user)
    
    # if not client_projects.exists():
    #     messages.error(request, "You don't have access to this client")
    #     return redirect('clients_list')
    
    active_projects = client.projects.filter(status__in=['approved', 'in_progress']).order_by('-created_at')
    completed_projects = client.projects.filter(status='completed').order_by('-created_at')
    completed_count = completed_projects.count()

    context = {
        'client': client,
        'completed_count': completed_count,
        'active_projects': active_projects,
        'completed_projects': completed_projects,
    }
    
    return render(request, 'dashboard/client_details.html', context)


# ============================================================================
# CALENDAR VIEW
# ============================================================================

@login_required
def calendar_view(request):
    """
    Display calendar with project deadlines
    
    GET: ?month=MM&year=YYYY to navigate months
    """
    
    # Get current month and year
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    
    # Create month label (e.g., "August 2024")
    month_label = datetime(year, month, 1).strftime("%B %Y")
    
    # Get calendar for the month
    cal = calendar.monthcalendar(year, month)
    
    # Get all projects for this videographer
    projects = Project.objects.filter(
        status__in=['approved', 'in_progress', 'revision']
    )
    
    # Build days list with project data
    days = []
    leading_blanks = cal[0].count(0)  # Empty cells before month starts
    
    for week in cal:
        for day_num in week:
            if day_num == 0:
                continue  # Skip leading/trailing blanks
            
            # Create date object
            day_date = datetime(year, month, day_num).date()
            
            # Check if this day is today
            is_today = (day_date == today)
            
            # Find project(s) with this deadline
            project = projects.filter(deadline=day_date).first()
            
            # Add to days list
            days.append({
                'day': day_num,
                'date': day_date,
                'is_today': is_today,
                'project': project,
            })
    
    # Navigation: previous and next month
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year
    
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year
    
    # Stats for the month
    projects_this_month = projects.filter(
        deadline__year=year,
        deadline__month=month
    )
    
    context = {
        'month_label': month_label,
        'month': month,
        'year': year,
        'leading_blanks': range(leading_blanks),
        'days': days,
        
        # Navigation
        'prev_month': prev_month,
        'prev_year': prev_year,
        'next_month': next_month,
        'next_year': next_year,
        
        # Stats
        'projects_this_month': projects_this_month.count(),
        'due_soon': projects.filter(
            deadline__range=[today, today + timedelta(days=7)],
            status__in=['approved', 'in_progress']
        ).count(),
    }
    
    return render(request, 'dashboard/calendar.html', context)


# ============================================================================
# ADDITIONAL HELPER VIEW: Upcoming Projects List
# ============================================================================

@login_required
def upcoming_projects(request):
    """Show all upcoming projects sorted by deadline"""
    
    from datetime import timedelta
    today = timezone.now().date()
    
    projects = Project.objects.filter(
        deadline__gte=today,
        status__in=['approved', 'in_progress', 'revision']
    ).order_by('deadline')
    
    due_today = projects.filter(deadline=today)
    due_this_week = projects.filter(
        deadline__range=[today + timedelta(days=1), today + timedelta(days=6)]
    )
    due_later = projects.filter(deadline__gte=today + timedelta(days=7))
    
    # ⭐ ADD THIS: Calculate days until deadline
    def add_days_until(project_list):
        for project in project_list:
            project.days_until = (project.deadline - today).days
        return project_list
    
    due_today = add_days_until(due_today)
    due_this_week = add_days_until(due_this_week)
    due_later = add_days_until(due_later)
    
    return render(request, 'dashboard/upcoming_project.html', {
        'due_today': due_today,
        'due_this_week': due_this_week,
        'due_later': due_later,
        'total_upcoming': projects.count(),
    })


@login_required
def analytics(request):
    """
    Dashboard only shows projects that have been:
    1. Approved by admin
    2. Proposal sent to client
    3. ✅ CLIENT APPROVED (Client + Project created)
    """
    
    user = request.user
    
    # ⭐ ONLY SHOW PROJECTS (Client + Project records created)
    # NOT bookings - bookings are just requests
    projects = Project.objects.all()
    
    # ============================================
    # UPCOMING DEADLINES (Only from Projects)
    # ============================================
    
    today = timezone.now().date()
    upcoming_projects = projects.filter(
        deadline__gte=today
    ).select_related('client').order_by('deadline')[:10]
    
    upcoming = []
    for project in upcoming_projects:
        days_until = (project.deadline - today).days
        status_slug = str(project.status).lower().replace(' ', '-')
        
        upcoming.append({
            'name': project.name,
            'client': project.client,
            'deadline': project.deadline,
            'days_until_deadline': days_until,
            'status': project.get_status_display() if hasattr(project, 'get_status_display') else str(project.status),
            'status_slug': status_slug,
            'completion': getattr(project, 'progress', 0) or 0,
            'get_client_scope_url': getattr(project, 'get_client_scope_url', lambda: None)()
        })
    
    # ============================================
    # RECENT REVISION REQUESTS (From Projects)
    # ============================================
    
    recent_revisions = RevisionRequest.objects.filter(
        project__in=projects
    ).select_related('project', 'project__client').order_by('-created_at')[:5]
    
    recent_revisions_data = []
    for rev in recent_revisions:
        status_badge_slug = str(rev.status).lower().replace(' ', '-')
        
        recent_revisions_data.append({
            'number': getattr(rev, 'revision_number', 1) or 1,
            'project': rev.project,
            'created_at': rev.created_at,
            'description': getattr(rev, 'description', 'Revision request') or 'Revision request',
            'status': rev.get_status_display() if hasattr(rev, 'get_status_display') else str(rev.status),
            'status_badge_slug': status_badge_slug
        })
    
    # ============================================
    # CHART DATA
    # ============================================
    
    monthly_labels = []
    monthly_data = []
    
    for i in range(6, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_str = month_date.strftime('%b')
        monthly_labels.append(month_str)
        
        count = projects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).count()
        monthly_data.append(count)
    
    chart_monthly = {
        'labels': monthly_labels,
        'data': monthly_data,
    }
    
    # Revision usage
    revision_counts = {
        'included': RevisionRequest.objects.filter(
            project__in=projects,
            status='included'
        ).count(),
        'used': RevisionRequest.objects.filter(
            project__in=projects,
            status='used'
        ).count(),
        'billable': RevisionRequest.objects.filter(
            project__in=projects,
            status='billable'
        ).count(),
    }
    
    chart_revisions = {
        'labels': ['Included', 'Used', 'Billable'],
        'data': [
            revision_counts['included'],
            revision_counts['used'],
            revision_counts['billable']
        ],
        'colors': ['#0d6efd', '#198754', '#fd7e14']
    }
    
    # Revenue
    revenue_labels = []
    revenue_data = []
    
    for i in range(6, -1, -1):
        month_date = timezone.now() - timedelta(days=30*i)
        month_str = month_date.strftime('%b %y')
        revenue_labels.append(month_str)
        
        revenue = projects.filter(
            created_at__year=month_date.year,
            created_at__month=month_date.month
        ).aggregate(total=Sum('price'))['total'] or 0
        
        revenue_millions = revenue / 1_000_000 if revenue > 0 else 0
        revenue_data.append(float(revenue_millions))
    
    chart_revenue = {
        'labels': revenue_labels,
        'data': revenue_data,
    }
    
    context = {
        'upcoming': upcoming,
        'recent_revisions': recent_revisions_data,
        'chart_monthly': json.dumps(_json_safe(chart_monthly)),
        'chart_revisions': json.dumps(_json_safe(chart_revisions)),
        'chart_revenue': json.dumps(_json_safe(chart_revenue)),
    }
    
    return render(request, "dashboard/analytics.html", context)




# ---------------------------------------------------------------------------
# Admin / dashboard upload management
# ---------------------------------------------------------------------------

@login_required
def dashboard_list(request):
    """Videographer-facing list of all media, published or not."""
    items = MediaItem.objects.select_related("category").all()

    status = request.GET.get("status")
    if status == "public":
        items = items.filter(is_public=True)
    elif status == "draft":
        items = items.filter(is_public=False)

    paginator = Paginator(items, 24)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "gallery/dashboard_list.html", {"page_obj": page_obj})


@login_required
def dashboard_upload(request):
    """Create a new media item."""
    if request.method == "POST":
        form = MediaItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'"{item.title}" was uploaded.')
            return redirect("dashboard_list")
    else:
        form = MediaItemForm()
    return render(request, "gallery/dashboard_upload.html", {"form": form, "is_edit": False})


@login_required
def dashboard_edit(request, pk):
    item = get_object_or_404(MediaItem, pk=pk)
    if request.method == "POST":
        form = MediaItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{item.title}" was updated.')
            return redirect("dashboard_list")
    else:
        form = MediaItemForm(instance=item)
    return render(request, "gallery/dashboard_upload.html", {"form": form, "is_edit": True, "item": item})


@login_required
def dashboard_delete(request, pk):
    item = get_object_or_404(MediaItem, pk=pk)
    if request.method == "POST":
        title = item.title
        item.delete()
        messages.success(request, f'"{title}" was deleted.')
        return redirect("dashboard_list")
    return render(request, "gallery/dashboard_delete_confirm.html", {"item": item})


@login_required
def dashboard_toggle_publish(request, pk):
    """Quick AJAX-free toggle button for is_public, used from the dashboard list."""
    item = get_object_or_404(MediaItem, pk=pk)
    if request.method == "POST":
        item.is_public = not item.is_public
        item.save(update_fields=["is_public"])
    return redirect("dashboard_list")
