from django.shortcuts import redirect

def login_check(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.has_key('ActiveUserUsername'):
            response=redirect('sign_in_page')
            response.set_cookie('alert_danger', 'You are logged out. Please Login first.', 5)
            return response
        return view_func(request, *args, **kwargs)
    return wrapper