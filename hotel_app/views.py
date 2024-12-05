from django.shortcuts import render, redirect, reverse
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, authenticate, logout
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
import requests
from datetime import datetime
import pickle
import nltk
from hotel_app.models import Booking, Room, hotel, Guest as User
from hotel_app.forms import (
    LoginForm, RegistrationGuestForm, BookingForm, ContactForm, PaymentForm, ReviewForm
)
from hotel_app.session_validation import validate_user_session


# Home View
def home_view(request, *args, **kwargs):
    print(args, kwargs)
    print(request.user)
    return render(request, 'home.html', {})


# Hotel List View
def hotel_list(request):
    hotels = hotel.objects.all()
    return render(request, 'hotel_list.html', {'hotels': hotels})


# Booking Create View
class BookingView(LoginRequiredMixin, CreateView):
    model = Booking
    template_name = "booking.html"
    success_url = '/payment/'
    form_class = BookingForm

    def dispatch(self, request, *args, **kwargs):
        if not validate_user_session(request):
            return HttpResponseForbidden("Invalid session. Please log in again.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.guest_ID = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        content = super(BookingView, self).get_context_data(**kwargs)
        content['rooms'] = Room.objects.filter(is_available=True)
        return content


# Booking List View
class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "bookinglist.html"

    def dispatch(self, request, *args, **kwargs):
        if not validate_user_session(request):
            return HttpResponseForbidden("Invalid session. Please log in again.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        content = super(BookingListView, self).get_context_data(**kwargs)
        content['object'] = self.model.objects.filter(guest_ID=self.request.user)
        return content


# Receipt View
@login_required
def receipt_view(request, *args, **kwargs):
    if not validate_user_session(request):
        return HttpResponseForbidden("Invalid session. Please log in again.")
    last_booking_obj = Booking.objects.filter(guest_ID=request.user).last()
    return render(request, 'receipt.html', {'object': last_booking_obj})


# Login View
def login_view(request):
    form = LoginForm()
    message = ''
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                request.session.cycle_key()  # Prevent session fixation
                message = f'Hello {user.email}, you have been logged in.'
                return redirect('home')
            else:
                message = 'Login failed. Please check your email and password.'
    return render(request, 'login.html', context={'form': form, 'message': message})


# Logout View
def logout_view(request):
    logout(request)
    return redirect('home')


# Register View
def register_view(request, *args, **kwargs):
    if request.method == "POST":
        form = RegistrationGuestForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationGuestForm()
    return render(request, 'register.html', {'form': form})


# Contact View
def contactView(request):
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_name = form.cleaned_data['contact_name']
            contact_email = form.cleaned_data['contact_email']
            content = form.cleaned_data['content']
            try:
                send_mail(contact_name, contact_email, content, ['admin@example.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            return redirect('home')
    return render(request, "contact.html", {'form': form})


# Google Login
def google_login(request):
    redirect_uri = "%s://%s%s" % (
        request.scheme, request.get_host(), reverse('google_login')
    )
    if 'code' in request.GET:
        params = {
            'grant_type': 'authorization_code',
            'code': request.GET.get('code'),
            'redirect_uri': redirect_uri,
            'client_id': settings.GP_CLIENT_ID,
            'client_secret': settings.GP_CLIENT_SECRET
        }
        url = 'https://accounts.google.com/o/oauth2/token'
        response = requests.post(url, data=params)
        access_token = response.json().get('access_token')
        user_data = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'access_token': access_token}
        ).json()
        email = user_data.get('email')
        if email:
            user, _ = User.objects.get_or_create(email=email)
            user.__dict__.update({
                'first_name': user_data.get('name', '').split()[0],
                'last_name': user_data.get('family_name'),
                'google_avatar': user_data.get('picture'),
                'gender': user_data.get('gender', 'O').upper(),
                'is_active': True
            })
            user.save()
            login(request, user)
        else:
            messages.error(request, 'Unable to log in with Gmail. Please try again.')
        return redirect('booking')
    else:
        scope = " ".join([
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email"
        ])
        url = f"https://accounts.google.com/o/oauth2/auth?client_id={settings.GP_CLIENT_ID}&response_type=code&scope={scope}&redirect_uri={redirect_uri}"
        return redirect(url)


# Review View
@login_required
def reviewViews(request):
    if not validate_user_session(request):
        return HttpResponseForbidden("Invalid session. Please log in again.")
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            comment = form.cleaned_data['comment']
            loaded_model = pickle.load(open("hotel_app/review_model.pkl", 'rb'))
            ratings = loaded_model.classify({word: True for word in nltk.word_tokenize(comment)})
            form.instance.guest_ID = request.user
            form.instance.rating = ratings
            form.save()
            return redirect('home')
    else:
        form = ReviewForm()
    return render(request, 'review.html', {'form': form})


# Payment View
@login_required
def paymentView(request):
    if not validate_user_session(request):
        return HttpResponseForbidden("Invalid session. Please log in again.")
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.instance.booking_num = Booking.objects.filter(guest_ID=request.user).last()
            form.save()
            return redirect('receipt')
    else:
        form = PaymentForm()
    return render(request, 'payment.html', {'form': form})


# Rooms List View
class RoomsLists(ListView):
    model = Room
    template_name = "booking-noauth.html"

    def get_context_data(self, **kwargs):
        content = super(RoomsLists, self).get_context_data(**kwargs)
        content['rooms'] = Room.objects.filter(is_available=True)
        return content
