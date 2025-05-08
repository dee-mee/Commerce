from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Address, VendorProfile
from .forms import AddressForm, VendorRegistrationForm, UserProfileForm

@login_required
def profile(request):
    """User profile view"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def address_list(request):
    """List all addresses for a user"""
    addresses = Address.objects.filter(user=request.user)
    context = {
        'addresses': addresses,
    }
    return render(request, 'accounts/address_list.html', context)

@login_required
def address_create(request):
    """Create a new address"""
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            
            # If this is set as default, unset any other default of same type
            if address.is_default:
                Address.objects.filter(
                    user=request.user, 
                    address_type=address.address_type, 
                    is_default=True
                ).update(is_default=False)
                
            address.save()
            messages.success(request, 'Address added successfully')
            return redirect('accounts:address_list')
    else:
        form = AddressForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
def address_edit(request, pk):
    """Edit an existing address"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            updated_address = form.save(commit=False)
            
            # If this is set as default, unset any other default of same type
            if updated_address.is_default:
                Address.objects.filter(
                    user=request.user, 
                    address_type=updated_address.address_type, 
                    is_default=True
                ).exclude(pk=pk).update(is_default=False)
                
            updated_address.save()
            messages.success(request, 'Address updated successfully')
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    
    context = {
        'form': form,
        'address': address,
    }
    return render(request, 'accounts/address_form.html', context)

@login_required
def address_delete(request, pk):
    """Delete an address"""
    address = get_object_or_404(Address, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully')
        return redirect('accounts:address_list')
    
    context = {
        'address': address,
    }
    return render(request, 'accounts/address_confirm_delete.html', context)

@login_required
def vendor_register(request):
    """Register as a vendor"""
    # Check if user is already a vendor
    if hasattr(request.user, 'vendor_profile'):
        messages.info(request, 'You are already registered as a vendor')
        return redirect('accounts:vendor_dashboard')
    
    if request.method == 'POST':
        form = VendorRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            vendor_profile = form.save(commit=False)
            vendor_profile.user = request.user
            vendor_profile.save()
            
            # Update user model
            request.user.is_vendor = True
            request.user.save()
            
            messages.success(request, 'Vendor registration successful. Your account is pending approval.')
            return redirect('accounts:vendor_dashboard')
    else:
        form = VendorRegistrationForm()
    
    context = {
        'form': form,
    }
    return render(request, 'accounts/vendor_register.html', context)

@login_required
def vendor_dashboard(request):
    """Vendor dashboard"""
    if not request.user.is_vendor:
        messages.error(request, 'You are not registered as a vendor')
        return redirect('accounts:vendor_register')
    
    # Get vendor profile
    vendor_profile = get_object_or_404(VendorProfile, user=request.user)
    
    context = {
        'vendor_profile': vendor_profile,
    }
    return render(request, 'accounts/vendor_dashboard.html', context)
