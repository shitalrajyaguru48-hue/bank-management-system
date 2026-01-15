from django.shortcuts import render
# Create your views here.
# statement/views.py
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from .models import Statement

@login_required
def customer_statement(request):
    customer = Profile.objects.get(user=request.user)

    statements = Statement.objects.filter(
        customer=customer
    ).order_by('-created_at')

    return render(request, 'customer/customer_statement.html', {
        'statements': statements
    })
