from django.urls import path
from . import views


# URL Configuration for 3-Stage Booking Workflow

# Stage 1: PUBLIC (Client) → Booking Request
# Stage 2: ADMIN → Review & Approve
# Stage 3: VIDEOGRAPHER → Add Proposal
# Stage 4: CLIENT → Approve Proposal → Creates Client + Project

urlpatterns = [
    # ============================================
    # STAGE 2: ADMIN REVIEW
    # ============================================
    path('admin/bookings/', views.admin_dashboard, name='admin_dashboard'),
    
    # ============================================
    # STAGE 3: VIDEOGRAPHER PROPOSAL
    # ============================================
    path('booking/', views.booking_list_view, name='booking_list'),
    path('booking/<int:pk>/', views.booking_detail_view, name='booking_detail'),
    path('proposal/<int:booking_pk>/', views.videographer_proposal_form, name='videographer_proposal_form'),
    path('task/', views.Task_list_view, name='task_list'),
    path('task/<int:pk>/', views.task_detail_view, name='task_detail'),
    
    # ============================================
    # STAGE 4: CLIENT APPROVAL
    # ============================================
    path('client/approve-proposal/<int:booking_pk>/', views.client_approve_proposal, name='client_approve_proposal'),
    
    # ============================================
    # DASHBOARD (Shows only approved projects)
    # ============================================
    path('index/', views.dashboard_overview, name='dashboard_overview'),



    # ================================  Client ================================= #
    path('client/', views.clients_list, name='client_list'),
    path('dashboard/client/<int:pk>/', views.client_detail, name='client_detail'),



    path('calender/', views.calendar_view, name='calender'),
    path('analytics/', views.analytics, name='analytics'),
    path('dashboard/upcoming/', views.upcoming_projects, name='upcoming_projects'),



    # Dashboard (admin upload management)
    path("dashboard/media/", views.dashboard_list, name="dashboard_list"),
    path("dashboard/media/upload/", views.dashboard_upload, name="dashboard_upload"),
    path("dashboard/media/<int:pk>/edit/", views.dashboard_edit, name="dashboard_edit"),
    path("dashboard/media/<int:pk>/delete/", views.dashboard_delete, name="dashboard_delete"),
    path("dashboard/media/<int:pk>/toggle/", views.dashboard_toggle_publish, name="dashboard_toggle"),
]