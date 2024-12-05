# utils/session_validation.py
from django.contrib.sessions.models import Session

def validate_user_session(request):
    """Validate the session for the current logged-in user."""
    user = request.user
    session_key = request.session.session_key

    # Check if the session key matches the one in the database for the user
    if not Session.objects.filter(session_key=session_key, session_data__contains=str(user.id)).exists():
        return False
    return True
