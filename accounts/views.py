from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EditProfileForm, LoginForm, RegisterForm
from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard_overview")

    form = LoginForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            remember = form.cleaned_data["remember"]

            user = authenticate(
                request,
                username=username,
                password=password,
            )

            if user is not None:
                if not user.is_verified:
                    messages.error(request, "Your account has not been verified.")
                    return redirect("login")

                login(request, user)

                if not remember:
                    request.session.set_expiry(0)

                messages.success(request, f"Welcome back, {user.full_name}!")
                return redirect("dashboard_overview")

            messages.error(request, "Invalid email or password.")

    return render(request, "auth/login.html", {"form": form})

def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard_overview")

    form = RegisterForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Account created successfully. Please login."
            )

            return redirect("login")

    return render(request, "auth/register.html", {"form": form})


@login_required
def profile_view(request):

    return render(
        request,
        "auth/profile.html",
        {
            "user": request.user
        }
    )


@login_required
def edit_profile_view(request, pk):

    user = get_object_or_404(User, pk=pk)

    if request.method == "POST" and request.POST.get("remove_picture"):
        user.profile_picture.delete(save=False)
        user.profile_picture = None
        user.save()

        messages.success(
            request,
            "Profile photo removed." 
        )

        return redirect("edit_profile", pk=user.pk)

    form = EditProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=user,
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
    
            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    return render(
        request,
        "auth/edit-profile.html",
        {"form": form},
    )


@login_required
def logout_view(request):

    logout(request)

    messages.success(
        request,
        "You have successfully logged out."
    )

    return redirect("login")