from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin

from .forms import RegistrationForm

class RegisterView(SuccessMessageMixin, CreateView):
    form_class = RegistrationForm
    template_name = 'auth/register.html'
    success_url = reverse_lazy('login')
    success_message = "Your account was created successfully. You can now log in."
    
    def form_valid(self, form):
        response = super().form_valid(form)
        # Auto-login after registration
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect('core:home')
