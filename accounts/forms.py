from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


class LoginForm(forms.Form):
    """Mirrors the fields login_view() already reads off request.POST."""

    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Username",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        }),
    )
    remember = forms.BooleanField(
        label="Remember me",
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    def clean_username(self):
        # login_view() lowercases/strips before calling authenticate()
        return self.cleaned_data["username"].strip().lower()


class RegisterForm(forms.ModelForm):
    """Backs register_view(). Password is handled separately from Meta.fields
    since it needs hashing via create_user(), not a raw model field write."""

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Password",
        }),
    )

    class Meta:
        model = User
        fields = ["full_name", "username", "email", "phone_number"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Name",
            }),
            "username": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Username",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control", "placeholder": "Email",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "Phone no",
            }),
        }

    def clean_username(self):
        return self.cleaned_data["username"].strip()

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        # create_user() handles password hashing; Meta.fields alone can't do that.
        return User.objects.create_user(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password"],
            full_name=self.cleaned_data["full_name"],
            phone_number=self.cleaned_data.get("phone_number", ""),
            is_verified=True,  # matches the current register_view() behavior
        )


class EditProfileForm(forms.ModelForm):
    """Backs edit_profile_view(). Reproduces the view's current behavior:
    username is kept in sync with email, and profile_picture is optional."""

    class Meta:
        model = User
        fields = ["full_name", "email","username", "phone_number", "profile_picture"]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control", "placeholder": "+234 800 000 0000",
            }),
            "profile_picture": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        already_taken = (
            User.objects
            .filter(email=email)
            .exclude(pk=self.instance.pk)
            .exists()
        )
        if already_taken:
            raise ValidationError("Another account is already using this email.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Keep username == email, same as the current view logic
        user.username = user.email
        if commit:
            user.save()
        return user