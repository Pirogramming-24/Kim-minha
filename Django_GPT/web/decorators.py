from functools import wraps
from django.shortcuts import render

def login_required_with_alert(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)

        return render(request, "alert_redirect.html", {
            "next_url": request.get_full_path(),
        })
    return _wrapped