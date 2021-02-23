from django.shortcuts import render
from django.views.generic import View

class login(View):
    def get(self, request):
        return render(request, 'login.html')