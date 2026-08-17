from django import forms

from .models import Booking


class BookingForm(forms.ModelForm):
    """Backs the public 11-step booking wizard. Steps are purely a front-end
    concern (the wizard JS shows/hides .wizard-step blocks) — this is a
    single form submitted once, on the final step."""

    class Meta:
        model = Booking
        fields = [
            # Step 1
            "full_name", "email", "phone_number", "company", "project_type",
            # Step 2
            "project_description",
            # Step 3
            "coverage_type",
            "coverage_ceremony", "coverage_speeches", "coverage_performances",
            "coverage_interviews", "coverage_product_shots", "coverage_drone_footage",
            "coverage_behind_the_scenes", "coverage_guest_reactions", "coverage_decoration",
            "coverage_social_media_content", "coverage_highlight_moments", "coverage_other",
            "special_requests",
            # Step 4
            "event_date", "start_time", "end_time", "coverage_hours",
            # Step 5
            "venue_name", "venue_address", "city", "state", "country", "maps_link",
            # Step 6
            "deliverable_highlight_video", "deliverable_full_event_video",
            "deliverable_social_reels", "deliverable_youtube_version",
            "deliverable_short_documentary", "deliverable_raw_footage",
            "deliverable_edited_photos", "deliverable_promo_trailer",
            "final_length", "deadline",
            # Step 7
            "budget", "deposit", "payment_method", "revision_round",
            # Step 8
            "drone_coverage", "livestream", "extra_camera_operator", "photography",
            "same_day_edit", "teleprompter", "lighting_setup", "audio_recording",
            "subtitle_captions", "motion_graphics",
            # Step 9
            "delivery_method",
            # Step 10
            "additional_notes",
            # Step 11
            "confirm_information", "agree_booking_policy", "confirm_deposit_policy",
        ]
        widgets = {
            # Step 1
            "full_name": forms.TextInput(attrs={
                "class": "form-control", "id": "bName", "placeholder": "Full name",
            }),
            "email": forms.EmailInput(attrs={
                "class": "form-control", "id": "bEmail", "placeholder": "Email address",
            }),
            "phone_number": forms.TextInput(attrs={
                "class": "form-control", "id": "bPhone", "placeholder": "Phone number",
            }),
            "company": forms.TextInput(attrs={
                "class": "form-control", "id": "bCompany", "placeholder": "Company",
            }),
            "project_type": forms.Select(attrs={"class": "form-select", "id": "bProjectType"}),

            # Step 2
            "project_description": forms.Textarea(attrs={
                "class": "form-control", "id": "bProjectDesc",
                "placeholder": "Project description", "style": "height:130px",
            }),

            # Step 3
            "coverage_type": forms.Select(attrs={"class": "form-select", "id": "bcoverage"}),
            "coverage_ceremony": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covCeremony"}),
            "coverage_speeches": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covSpeeches"}),
            "coverage_performances": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covPerformances"}),
            "coverage_interviews": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covInterviews"}),
            "coverage_product_shots": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covProduct"}),
            "coverage_drone_footage": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covDrone"}),
            "coverage_behind_the_scenes": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covBts"}),
            "coverage_guest_reactions": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covReactions"}),
            "coverage_decoration": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covDecoration"}),
            "coverage_social_media_content": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covSocial"}),
            "coverage_highlight_moments": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covHighlights"}),
            "coverage_other": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "covOther"}),
            "special_requests": forms.Textarea(attrs={
                "class": "form-control", "id": "bSpecialRequests",
                "placeholder": "Special requests", "style": "height:90px",
            }),

            # Step 4
            "event_date": forms.DateInput(attrs={"class": "form-control", "id": "bEventDate", "type": "date"}),
            "start_time": forms.TimeInput(attrs={"class": "form-control", "id": "bStartTime", "type": "time"}),
            "end_time": forms.TimeInput(attrs={"class": "form-control", "id": "bEndTime", "type": "time"}),
            "coverage_hours": forms.NumberInput(attrs={
                "class": "form-control", "id": "bCoverageHours", "min": "1", "step": "0.5",
                "placeholder": "Coverage hours",
            }),

            # Step 5
            "venue_name": forms.TextInput(attrs={
                "class": "form-control", "id": "bVenueName", "placeholder": "Venue name",
            }),
            "venue_address": forms.TextInput(attrs={
                "class": "form-control", "id": "bVenueAddress", "placeholder": "Venue address",
            }),
            "city": forms.TextInput(attrs={"class": "form-control", "id": "bCity", "placeholder": "City"}),
            "state": forms.TextInput(attrs={"class": "form-control", "id": "bState", "placeholder": "State"}),
            "country": forms.TextInput(attrs={"class": "form-control", "id": "bCountry", "placeholder": "Country"}),
            "maps_link": forms.URLInput(attrs={
                "class": "form-control", "id": "bMapsLink", "placeholder": "Google Maps link",
            }),

            # Step 6
            "deliverable_highlight_video": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delHighlight"}),
            "deliverable_full_event_video": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delFull"}),
            "deliverable_social_reels": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delReels"}),
            "deliverable_youtube_version": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delYoutube"}),
            "deliverable_short_documentary": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delDoc"}),
            "deliverable_raw_footage": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delRaw"}),
            "deliverable_edited_photos": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delPhotos"}),
            "deliverable_promo_trailer": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "delTrailer"}),
            "final_length": forms.Select(attrs={"class": "form-select", "id": "bFinalLength"}),
            "deadline": forms.Select(attrs={"class": "form-select", "id": "bDeadline"}),

            # Step 7
            "budget": forms.Select(attrs={"class": "form-select", "id": "bBudget"}),
            "deposit": forms.Select(attrs={"class": "form-select", "id": "bDeposit"}),
            "payment_method": forms.Select(attrs={"class": "form-select", "id": "bPaymentMethod"}),
            "revision_round": forms.Select(attrs={"class": "form-select", "id": "bRevisionRounds"}),

            # Step 8
            "drone_coverage": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addDrone"}),
            "livestream": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addLivestream"}),
            "extra_camera_operator": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addCamOp"}),
            "photography": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addPhotography"}),
            "same_day_edit": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addSameDay"}),
            "teleprompter": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addTeleprompter"}),
            "lighting_setup": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addLighting"}),
            "audio_recording": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addAudio"}),
            "subtitle_captions": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addCaptions"}),
            "motion_graphics": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "addMotion"}),

            # Step 9
            "delivery_method": forms.Select(attrs={"class": "form-select", "id": "bDeliveryMethod"}),

            # Step 10
            "additional_notes": forms.Textarea(attrs={
                "class": "form-control", "id": "bAdditionalNotes",
                "placeholder": "Anything else", "style": "height:120px",
            }),

            # Step 11
            "confirm_information": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "termAccurate"}),
            "agree_booking_policy": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "termPolicy"}),
            "confirm_deposit_policy": forms.CheckboxInput(attrs={"class": "form-check-input", "id": "termDeposit"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # The template marks these `required` in the HTML — a plain BooleanField
        # with default=False becomes required=False on a ModelForm by default,
        # which would let someone submit without agreeing. Force them true here.
        for field_name in ("confirm_information", "agree_booking_policy", "confirm_deposit_policy"):
            self.fields[field_name].required = True
                    # Apply Bootstrap classes and highlight invalid fields
            for name, field in self.fields.items():

                if isinstance(field.widget, forms.CheckboxInput):
                    css = "form-check-input"

                elif isinstance(field.widget, forms.Select):
                    css = "form-select"

                elif isinstance(field.widget, forms.Textarea):
                    css = "form-control"

                else:
                    css = "form-control"

                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing} {css}".strip()

                # Add Bootstrap invalid class if this field has errors
                if self.is_bound and name in self.errors:
                    field.widget.attrs["class"] += " is-invalid"

    def clean(self):
        cleaned_data = super().clean()

        end_time = cleaned_data.get("end_time")
        start_time = cleaned_data.get("start_time")
        if end_time and start_time and end_time <= start_time:
            self.add_error("end_time", "End time must be after the start time.")

        return cleaned_data

    