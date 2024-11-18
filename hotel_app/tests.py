from django.test import TestCase
from .models import Guest, hotel, Room, Booking, Rating, Payment
from datetime import datetime, timedelta
from decimal import Decimal

class GuestModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(
            email="guest@example.com",
            password="password123",
            date_of_birth="1990-01-01",
            phone="+630000000000",
        )

    def test_guest_creation(self):
        self.assertEqual(self.guest.email, "guest@example.com")

class HotelRoomBookingTest(TestCase):
    def setUp(self):
        self.hotel = hotel.objects.create(
            name="Test Hotel",
            location="Test City",
            phone="+630000000001",
            hotel_email="hotel@example.com"
        )
        self.room = Room.objects.create(
            room_no=101,
            hotel_code=self.hotel,
            room_type="standard",
            rate=Decimal("150.00"),
            is_available=True,
            no_of_beds=2,
        )
        self.guest = Guest.objects.create(email="guest2@example.com", password="password123")
        self.booking = Booking.objects.create(
            guest_ID=self.guest,
            hotel_code=self.hotel,
            room_ID=self.room,
            checkin_date=datetime.now(),
            checkout_date=datetime.now() + timedelta(days=3),
            no_of_guests=1
        )

    def test_room_booking(self):
        self.assertEqual(self.booking.room_ID, self.room)

    def test_compute_charges(self):
        charges = self.booking.compute_charges()
        expected_charges = 3 * self.room.rate
        self.assertEqual(charges, expected_charges)

    def test_room_availability_on_booking(self):
        self.assertFalse(self.room.is_available)

class RatingModelTest(TestCase):
    def setUp(self):
        self.guest = Guest.objects.create(email="guest3@example.com", password="password123")
        self.rating = Rating.objects.create(
            guest_ID=self.guest,
            comment="Excellent stay!",
            rating="5"
        )

    def test_rating_creation(self):
        self.assertEqual(self.rating.comment, "Excellent stay!")
        self.assertEqual(self.rating.rating, "5")

class PaymentModelTest(TestCase):
    def setUp(self):
        self.hotel = hotel.objects.create(
            name="Test Hotel 2",
            location="Test City 2",
            phone="+630000000002",
            hotel_email="hotel2@example.com"
        )
        self.room = Room.objects.create(
            room_no=102,
            hotel_code=self.hotel,
            room_type="family",
            rate=Decimal("200.00"),
            is_available=True,
        )
        self.guest = Guest.objects.create(email="guest4@example.com", password="password123")
        self.booking = Booking.objects.create(
            guest_ID=self.guest,
            hotel_code=self.hotel,
            room_ID=self.room,
            checkin_date=datetime.now(),
            checkout_date=datetime.now() + timedelta(days=5),
        )
        self.payment = Payment.objects.create(
            booking_num=self.booking,
            card_owner="Guest Owner",
            card_number=1234567890123456,
            card_cvv=123,
            exp_month=12,
            exp_year=2025,
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.card_owner, "Guest Owner")
        self.assertEqual(self.payment.booking_num, self.booking)
