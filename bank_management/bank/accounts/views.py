from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm, LoginForm 
from .models import Profile,Account
from django.contrib.auth import logout
from django.contrib import messages
import qrcode
import base64
from io import BytesIO
import random
def generate_unique_account_number():
    while True:
        acc_number = "BANK" + str(random.randint(1000000000, 9999999999))
        if not Account.objects.filter(account_number=acc_number).exists():
            return acc_number
def home(request):
    return render(request, 'home.html')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()  # Signals will create Profile & Account automatically
            profile = Profile.objects.get(user=user)
            profile.branch = form.cleaned_data['branch']  # save selected branch
            profile.role = 'customer'  # ensure default role
            profile.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)

            # 1. Get profile OR create it if missing
            profile, created = Profile.objects.get_or_create(user=user)

            # 2. If role is EMPTY → make customer
            if profile.role is None:
                profile.role = 'customer'
                profile.save()

            # 3. Redirect based on role
            if profile.role == 'customer':
                return redirect('customer_dash')
            elif profile.role in ['admin', 'manager']:
                return redirect('branch_redirect')
            else:
                return redirect('home')

    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})
  

@login_required
def customer_dash(request):
    profile = Profile.objects.get(user=request.user)
    customer_branch = profile.branch

    # Handle UPI ID creation if POST
    if request.method == "POST" and not profile.upi_id:
        # Keep customer name as proper name
        customer_name = profile.user.get_full_name() or profile.user.username
        # Bank name in lowercase without spaces
        bank_name = profile.branch.name.lower().replace(" ", "") if profile.branch else "defaultbank"
        # Generate UPI ID
        profile.upi_id = f"{customer_name}@{bank_name}.ybi"
        profile.save()

    # Get all managers in this branch
    managers = Profile.objects.filter(branch=customer_branch, role='manager')
    manager_names = ", ".join([m.user.get_full_name() or m.user.username for m in managers]) if managers.exists() else "No Manager Assigned"

    # Generate QR code for this customer
    qr_text = f"CustomerID-{request.user.id}"
    qr_img = qrcode.make(qr_text)
    buffered = BytesIO()
    qr_img.save(buffered, format="PNG")
    qr_base64 = base64.b64encode(buffered.getvalue()).decode()

    # Account number
    account_number = profile.user.account.account_number if hasattr(profile.user, 'account') else "Not Assigned"

    context = {
        'customer_name': profile.user.get_full_name() or profile.user.username,
        'customer_email': profile.user.email,
        'customer_branch': customer_branch.name if customer_branch else "Not Assigned",
        'manager_names': manager_names,
        'reply': profile.reply,
        'qr_base64': qr_base64,
        'account_number': account_number,
        'profile': profile,  # profile.upi_id used in template
    }

    return render(request, 'customer/customer_dashboard.html', context)



@login_required
def profile_edit(request):
    user = request.user
    profile = user.profile  # assuming OneToOne

    if request.method == 'POST':
        # Get data from POST
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        image = request.FILES.get('image')  # file upload

        # Simple validation example (add more if needed)
        if not email:
            messages.error(request, "Email is required.")
            return render(request, 'profile_edit.html', {'user': user, 'profile': profile})

        # Update User model
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        # Update Profile model if image uploaded
        if image:
            profile.image = image
            profile.save()

        messages.success(request, "Profile updated successfully.")

        # Redirect based on role
        if profile.role == 'admin':
            return redirect('admin_dash')
        elif profile.role == 'manager':
            return redirect('manager_dash')
        elif profile.role == 'customer':
            return redirect('customer_dash')
        else:
            return redirect('home')

    else:
        # GET request → render form with existing data
        return render(request, 'profile_edit.html', {'user': user, 'profile': profile})
@login_required
def logout_page(request):
    logout(request)  # logs the user out
    return redirect('home') 


@login_required
def send_message(request):
    customer_profile = Profile.objects.get(user=request.user)
    branch = customer_profile.branch

    # Get all managers in this branch
    managers = Profile.objects.filter(branch=branch, role='manager')
    manager_names = ", ".join([m.user.username for m in managers]) if managers.exists() else "No Manager Assigned"

    if request.method == 'POST':
        message_text = request.POST.get('message')
        if message_text and managers.exists():
            for manager in managers:
                manager.message = message_text  # save message to manager profile
                manager.save()
            messages.success(request, "Message sent to manager(s) successfully!")
            return redirect('customer_dash')

    context = {
        'manager_names': manager_names,
        'customer_branch': branch,
    }
    return render(request, 'customer/send_message.html', context)




@login_required
def manager_dash(request):
    profile = Profile.objects.get(user=request.user)
    manager_branch = profile.branch

    # All customers in this branch
    customers = Profile.objects.filter(branch=manager_branch, role='customer')

    context = {
        'manager_branch': manager_branch,
        'customers': customers,  # customer.message will be accessible
    }
    return render(request, 'manager/manager_dashboard.html', context)


@login_required
def open_accounts_redirect(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == 'admin':
        return redirect('admin_dash')

    elif profile.role == 'manager':
        return redirect('manager_dash')

    elif profile.role == 'customer':
        return redirect('customer_dash')

    # fallback safety
#     return redirect('home')

# @login_required
# def customer_dashboard(request):
#     return render(request, 'customer/customer_dashboard.html')

# @login_required
# def manager_dashboard(request):
#     return render(request, 'manager/manager_dashboard.html')

# @login_required
# def admin_dashboard(request):
#     return render(request, 'admin/admin_dashboard.html')