from videophotography.models import *


def notifications(request):
    """Makes pending-booking notification data available in every template
    without every view having to pass it in manually — needed since the
    notification bell lives in the shared dashboard frame, not a single page.
    """
 
    if not request.user.is_authenticated:
        return {}
 
    pending_bookings = (
        Booking.objects
        .filter(status=Booking.Status.PENDING)
        .order_by("-created_at")
    )
 
    return {
        "pending_bookings_count": pending_bookings.count(),
        "recent_pending_bookings": pending_bookings[:6],
    }
 