from django import forms
from .models import ExchangeProposalModel, ItemsModel
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ExchangeProposalForm(forms.ModelForm):
    class Meta:
        model = ExchangeProposalModel
        fields = ["ad_sender", "ad_receiver", "comment"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user is not None:
            self.fields["ad_sender"].queryset = self.fields[
                "ad_sender"
            ].queryset.filter(user=self.user)

    def clean(self):
        cleaned_data = super().clean()
        ad_sender = cleaned_data.get("ad_sender")
        ad_receiver = cleaned_data.get("ad_receiver")

        if ad_sender and ad_sender.owner != self.user:
            raise forms.ValidationError(
                "Вы можете отправить предложение только от своего объявления."
            )

        if ad_sender == ad_receiver:
            raise forms.ValidationError("Нельзя отправить предложение самому себе.")

        return cleaned_data


class ItemCreateForm(forms.ModelForm):
    class Meta:
        model = ItemsModel
        fields = ["title", "description", "image_url", "category", "condition"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
