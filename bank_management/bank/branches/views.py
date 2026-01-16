from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import Profile,Account
from .models import Branch
# from .forms import BalanceUpdateForm


@login_required
def branch_redirect(request):
    profile = Profile.objects.get(user=request.user)

    if profile.role == 'admin':
        return redirect('admin_dash')
    elif profile.role == 'manager':
        return redirect('manager_dash')
    else:
        return redirect('home')  # fallback, should not happen

@login_required
def admin_dash(request):
    profile = Profile.objects.get(user=request.user)

    # Ensure only admins can access
    if profile.role != 'admin':
        return redirect('home')

    # Get all branches, managers, and customers
    branches = Branch.objects.all()
    managers = Profile.objects.filter(role='manager')
    customers = Profile.objects.filter(role='customer')

    if request.method == "POST":
        customer_id = request.POST.get("customer_id")
        new_branch_id = request.POST.get("branch_id")
        new_role = request.POST.get("new_role")

        try:
            # Fetch the customer/manager to update
            user_profile = Profile.objects.get(id=customer_id)

            # Update branch if selected
            if new_branch_id:
                new_branch = Branch.objects.get(id=new_branch_id)
                user_profile.branch = new_branch

            # Update role if selected
            if new_role in ['customer', 'manager']:
                user_profile.role = new_role

            user_profile.save()

        except Profile.DoesNotExist:
            pass
        except Branch.DoesNotExist:
            pass

        return redirect('admin_dash')

    # Prepare customer_data for table
    customer_data = []
    for customer in customers:
        branch = customer.branch

        # Get managers of the branch
        if branch:
            branch_managers = Profile.objects.filter(branch=branch, role='manager')
            manager_names = [m.user.get_full_name() or m.user.username for m in branch_managers]
        else:
            manager_names = []

        account_number = getattr(getattr(customer.user, 'account', None), 'account_number', 'Not Assigned')

        customer_data.append({
            'customer': customer,
            'branch': branch,
            'managers': manager_names,
            'account_number': account_number,
        })

    # Prepare branch-wise counts
    branch_data = []
    for branch in branches:
        managers_count = Profile.objects.filter(branch=branch, role='manager').count()
        customers_count = Profile.objects.filter(branch=branch, role='customer').count()
        branch_data.append({
            'branch': branch,
            'managers_count': managers_count,
            'customers_count': customers_count,
        })

    context = {
        'branches': branches,
        'branch_data': branch_data,  # pass this to template
        'managers': managers,
        'customers': Profile.objects.filter(role='customer'),
        'customer_data': customer_data,
        'total_branches': branches.count(),
        'total_managers': Profile.objects.filter(role='manager').count(),
        'total_customers': Profile.objects.filter(role='customer').count(),
    }

    return render(request, 'admin/admin_dashboard.html', context)



@login_required
def manager_dash(request):
    profile = Profile.objects.get(user=request.user)

    # Branch of this manager
    manager_branch = profile.branch

    # All customers in this branch
    customers = Profile.objects.filter(branch=manager_branch, role='customer')

    context = {
        'manager_branch': manager_branch,
        'customers': customers,
    }
    return render(request, 'manager/manager_dashboard.html', context)

from decimal import Decimal
from statement.models import Statement

@login_required
def edit_balance(request, profile_id):
    manager_profile = Profile.objects.get(user=request.user)

    customer = Profile.objects.filter(
        id=profile_id,
        role='customer',
        branch=manager_profile.branch
    ).first()

    if not customer:
        return redirect('manager_dash')

    if request.method == 'POST':
        transaction_type = request.POST.get('transaction_type')
        amount = Decimal(request.POST.get('amount'))

        if transaction_type == 'credit':
            customer.balance += amount
        elif transaction_type == 'debit':
            customer.balance -= amount

        customer.save()

        # ✅ Save statement
        Statement.objects.create(
            customer=customer,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=customer.balance
        )

        return redirect('manager_dash')

    return render(request, 'manager/edit_balance.html', {'customer': customer})


@login_required
def reply(request, profile_id):
    
    manager_profile = Profile.objects.get(user=request.user)

    # Ensure only managers can reply
    if manager_profile.role != 'manager':
        return redirect('login')

    customer = Profile.objects.filter(
        id=profile_id,
        role='customer',
        branch=manager_profile.branch
    ).first()

    if not customer:
        return redirect('manager_dash')

    if request.method == "POST":
        message = request.POST.get("message")

        customer.reply = message
        customer.save()

        return redirect('manager_dash')

    return render(request, 'manager/reply_message.html', {
        'customer': customer
    })
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages


@login_required
def approve_disable_account(request, profile_id):
    # Only manager can approve
    manager_profile = Profile.objects.get(user=request.user)
    if manager_profile.role != 'manager':
        messages.error(request, "You are not allowed to do this.")
        return redirect('manager_dash')

    # Get customer
    customer = get_object_or_404(Profile, id=profile_id, role='customer', branch=manager_profile.branch)

    # Delete customer account
    user = customer.user
    customer.delete()  # deletes Profile
    user.delete()      # deletes User

    messages.success(request, "Customer account has been deleted successfully.")
    return redirect('manager_dash')
