from django import forms

from .models import *


class MediaItemForm(forms.ModelForm):
    class Meta:
        model = MediaItem
        fields = [
            "title", "description", "category", "project_reference",
            "media_type", "photo", "video_file", "embed_url", "thumbnail",
            "is_public", "is_featured",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "project_reference": forms.TextInput(attrs={"class": "form-control"}),
            "media_type": forms.Select(attrs={"class": "form-select", "id": "id_media_type"}),
            "photo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "video_file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "embed_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://youtu.be/..."}),
            "thumbnail": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_public": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean(self):
        cleaned = super().clean()
        media_type = cleaned.get("media_type")
        photo, video_file, embed_url = (
            cleaned.get("photo"), cleaned.get("video_file"), cleaned.get("embed_url")
        )
        thumbnail = cleaned.get("thumbnail")

        if media_type == MediaItem.PHOTO and not (photo or self.instance.photo):
            self.add_error("photo", "Upload a photo for this media type.")
        if media_type == MediaItem.VIDEO_FILE and not (video_file or self.instance.video_file):
            self.add_error("video_file", "Upload a video file for this media type.")
        if media_type == MediaItem.VIDEO_EMBED and not embed_url:
            self.add_error("embed_url", "Paste a YouTube or Vimeo URL for this media type.")
        if media_type in (MediaItem.VIDEO_FILE, MediaItem.VIDEO_EMBED) and not (
            thumbnail or self.instance.thumbnail
        ):
            self.add_error("thumbnail", "Videos need a thumbnail image for the gallery grid.")
        return cleaned


class MediaCategoryForm(forms.ModelForm):
    class Meta:
        model = MediaCategory
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
        }
