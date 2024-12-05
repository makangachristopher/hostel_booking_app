from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User
from hotel_app.models import Guest, Booking, Room, Rating, Payment
from django.forms import ModelForm


# Login Form
class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control',
    }))
    password = forms.CharField(max_length=63, widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter your password',
        'class': 'form-control',
    }))


# Registration Form for Guest Accounts
class RegistrationGuestForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = Guest
        fields = ['first_name', 'last_name', 'email', 'phone', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Guest.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        # Add phone validation logic here, e.g., regex for a specific format
        return phone


# Booking Form
class BookingForm(ModelForm):
    class Meta:
        model = Booking
        fields = ["hotel_code", "room_ID", "checkin_date", "checkout_date", "no_of_guests"]

    def __init__(self, *args, **kwargs):
        super(BookingForm, self).__init__(*args, **kwargs)
        self.fields['room_ID'].queryset = Room.objects.filter(is_available=True)

    def clean(self):
        cleaned_data = super().clean()
        checkin_date = cleaned_data.get("checkin_date")
        checkout_date = cleaned_data.get("checkout_date")
        no_of_guests = cleaned_data.get("no_of_guests")
        room = cleaned_data.get("room_ID")

        if checkin_date and checkout_date:
            if checkin_date >= checkout_date:
                raise forms.ValidationError("Check-in date must be before the check-out date.")
        
        if room and no_of_guests:
            if no_of_guests > room.capacity:
                raise forms.ValidationError("Number of guests exceeds room capacity.")
        return cleaned_data


# Contact Form
class ContactForm(forms.Form):
    contact_name = forms.CharField(
        required=True,
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Your name', 'class': 'form-control'}),
    )
    contact_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Your email', 'class': 'form-control'}),
    )
    content = forms.CharField(
        required=True,
        max_length=500,
        widget=forms.Textarea(attrs={'placeholder': 'What do you want to say?', 'class': 'form-control'}),
    )

    def clean_contact_name(self):
        contact_name = self.cleaned_data.get("contact_name").strip()
        return contact_name

    def clean_content(self):
        content = self.cleaned_data.get("content").strip()
        return content


# Review Form
class ReviewForm(ModelForm):
    class Meta:
        model = Rating
        fields = ['comment']

    def clean_comment(self):
        comment = self.cleaned_data.get("comment")
        if len(comment) > 500:
            raise forms.ValidationError("Comments cannot exceed 500 characters.")
        return comment


# Payment Form
class PaymentForm(ModelForm):
    class Meta:
        model = Payment
        fields = ['card_owner', 'card_number', 'card_cvv', 'exp_month', 'exp_year']

    def clean_card_number(self):
        card_number = self.cleaned_data.get("card_number")
        if not card_number.isdigit() or len(card_number) not in [13, 16]:
            raise forms.ValidationError("Invalid card number.")
        return card_number

    def clean_card_cvv(self):
        card_cvv = self.cleaned_data.get("card_cvv")
        if not card_cvv.isdigit() or len(card_cvv) != 3:
            raise forms.ValidationError("Invalid CVV.")
        return card_cvv

    def clean_exp_month(self):
        exp_month = self.cleaned_data.get("exp_month")
        if not 1 <= exp_month <= 12:
            raise forms.ValidationError("Invalid expiration month.")
        return exp_month

    def clean_exp_year(self):
        exp_year = self.cleaned_data.get("exp_year")
        if exp_year < 2024:  # Adjust for the current year
            raise forms.ValidationError("Expiration year must be in the future.")
        return exp_year
