from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from dashboard.models import Client, Project
from videophotography.models import Booking


class ProposalSaveTests(TestCase):
    def test_videographer_proposal_form_saves_proposal(self):
        user = get_user_model().objects.create_user(
            username="videographer",
            password="secret123",
            is_staff=True,
        )
        booking = Booking.objects.create(
            full_name="Jane Doe",
            email="jane@example.com",
            phone_number="08000000000",
            event_date="2026-09-01",
            start_time="10:00:00",
            end_time="12:00:00",
            venue_name="Studio Venue",
            venue_address="1 Main Street",
            status=Booking.Status.APPROVED,
        )

        self.client.force_login(user)
        response = self.client.post(
            reverse("videographer_proposal_form", args=[booking.pk]),
            {
                "proposed_price": "250000",
                "proposal_description": "A polished proposal",
                "deliverables": "Highlight video",
                "timeline": "Delivered in 2 weeks",
                "revisions_included": "2",
            },
        )

        self.assertEqual(response.status_code, 302)
        booking.refresh_from_db()
        self.assertEqual(booking.status, Booking.Status.PROPOSAL_SENT)
        self.assertEqual(booking.proposed_price, Decimal("250000"))
        self.assertEqual(booking.proposal_description, "A polished proposal")
        self.assertEqual(booking.deliverables, "Highlight video")


class TaskPageTests(TestCase):
    def test_staff_can_view_task_detail_page(self):
        user = get_user_model().objects.create_user(
            username="admin",
            password="secret123",
            is_staff=True,
        )
        client = Client.objects.create(
            name="Grace Smith",
            email="grace@example.com",
            phone="08000000001",
            company="Studio Co",
            project_type="Wedding",
        )
        project = Project.objects.create(
            name="Wedding Film",
            description="A cinematic wedding edit",
            price=Decimal("250000"),
            deadline="2026-09-01",
            client=client,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("task_detail", args=[project.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wedding Film")

    def test_non_staff_user_can_view_ongoing_task_detail(self):
        user = get_user_model().objects.create_user(
            username="clientuser",
            password="secret123",
            is_staff=False,
        )
        client = Client.objects.create(
            name="Aisha Bello",
            email="aisha@example.com",
            phone="08000000002",
            company="Aisha Media",
            project_type="Wedding",
        )
        project = Project.objects.create(
            name="Ongoing Wedding Edit",
            description="A current project in progress",
            price=Decimal("350000"),
            deadline="2026-09-05",
            status="in_progress",
            client=client,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("task_detail", args=[project.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ongoing Wedding Edit")


class DashboardOverviewTests(TestCase):
    def test_dashboard_overview_renders_with_decimal_revenue_data(self):
        user = get_user_model().objects.create_user(
            username="dashboardviewer",
            password="secret123",
        )
        client = Client.objects.create(
            name="Victor Umeh",
            email="victor@example.com",
            phone="08000000002",
            company="Umeh Studios",
            project_type="Wedding",
        )
        Project.objects.create(
            name="Wedding Film",
            description="A cinematic wedding edit",
            price=Decimal("250000"),
            deadline="2026-09-01",
            client=client,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard_overview"))

        self.assertEqual(response.status_code, 200)
        self.assertIn("chart_revenue", response.context)
        self.assertIsInstance(response.context["chart_revenue"], str)
        self.assertIn("0.25", response.context["chart_revenue"])

    def test_dashboard_overview_includes_chart_data_for_analytics_widgets(self):
        user = get_user_model().objects.create_user(
            username="dashboardcharts",
            password="secret123",
        )
        client = Client.objects.create(
            name="Ada Okafor",
            email="ada@example.com",
            phone="08000000003",
            company="Ada Media",
            project_type="Wedding",
        )
        Project.objects.create(
            name="Wedding Film",
            description="A cinematic wedding edit",
            price=Decimal("250000"),
            deadline="2026-09-01",
            client=client,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("dashboard_overview"))

        self.assertContains(response, "window.chartMonthlyData")
        self.assertContains(response, "window.chartRevenueData")
        self.assertContains(response, "chartMonthly")
        self.assertContains(response, "chartRevenue")


class ClientListTests(TestCase):
    def test_client_list_page_renders_for_authenticated_user(self):
        user = get_user_model().objects.create_user(
            username="clientviewer",
            password="secret123",
        )
        client = Client.objects.create(
            name="Victor Umeh",
            email="victor@example.com",
            phone="08000000002",
            company="Umeh Studios",
            project_type="Wedding",
        )
        Project.objects.create(
            name="Wedding Film",
            description="A cinematic wedding edit",
            price=Decimal("250000"),
            deadline="2026-09-01",
            client=client,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("client_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Victor Umeh")


