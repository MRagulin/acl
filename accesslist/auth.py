from django.contrib.auth.backends import BaseBackend

class MyAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        if username is not None and password is not None:
            request.session['GIT_USERNAME'] = username
            request.session['GIT_PASSWORD'] = password
