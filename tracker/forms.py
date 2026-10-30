from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Checkin, User


class SignUpForm(UserCreationForm):
    usable_password = None

    class Meta:
        model = User
        fields = ["name", "email"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name", "autofocus": True}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs["placeholder"] = "Password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"
        for field in self.fields.values():
            field.help_text = ""


class CheckinForm(forms.ModelForm):
    class Meta:
        model = Checkin
        fields = ["status", "mood", "note"]
        widgets = {
            "status": forms.RadioSelect,
            "mood": forms.RadioSelect,
            "note": forms.Textarea(
                attrs={"rows": 4, "placeholder": "What happened today? Any triggers, wins, or things on your mind."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Drop the "---------" empty choice the model field adds for blank=True.
        self.fields["mood"].choices = Checkin.Mood.choices
        self.fields["mood"].required = False
        self.fields["status"].choices = Checkin.Status.choices
