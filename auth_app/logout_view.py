from django.contrib.auth import logout
from django.shortcuts import redirect, render
from django.views import View
from django.contrib import messages

class CustomLogoutView(View):
    """
    Custom logout view that handles both GET and POST methods
    """
    def get(self, request):
        # Show the logout confirmation page
        return render(request, 'auth/logout.html')
    
    def post(self, request):
        # Log the user out
        logout(request)
        messages.success(request, "You have been successfully logged out.")
        return redirect('core:home')
