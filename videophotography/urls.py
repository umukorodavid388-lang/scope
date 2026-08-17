"""
URL routing for videography booking API.
Add this to your main urls.py:

    from django.urls import path, include
    urlpatterns = [
        path('api/bookings/', include('videography.urls')),
    ]
"""

from django.urls import path, include
from . import views

app_name = "media_library"


urlpatterns = [
    path("", views.landing, name="landing"),
    path('booking/', views.booking_create_view, name='booking_request'),
    path('booking/success/<int:pk>/', views.booking_success_view, name='booking_success'),
    path("contact/submit/", views.contact_submit, name="contact_submit"),

    path("gallery/", views.gallery, name="gallery"),
    path("gallery/<slug:slug>/", views.item_detail, name="item_detail"),

]

