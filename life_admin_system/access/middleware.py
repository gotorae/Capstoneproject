
# access/middleware.py
import time
from django.conf import settings
from django.contrib.auth import logout

IDLE_TIMEOUT_SECONDS = getattr(settings, "SESSION_COOKIE_AGE", 1800)

class IdleTimeoutMiddleware:
    """
    Logs out authenticated users after IDLE_TIMEOUT_SECONDS of inactivity.
    Works for session-auth (admin + browser requests).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_ts = int(time.time())
            last_activity = request.session.get("_last_activity_ts", current_ts)
            if current_ts - last_activity > IDLE_TIMEOUT_SECONDS:
                logout(request)
                # Optionally: clear session
                for key in list(request.session.keys()):
                    del request.session[key]
            request.session["_last_activity_ts"] = current_ts

