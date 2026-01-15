from django.shortcuts import render

def home_loan(request):
    # Default values
    amount = 0
    rate = 8
    years = 10
    interest = 0
    total = 0

    # Check if user provided GET parameters (for dynamic calculation)
    if 'amount' in request.GET and 'rate' in request.GET and 'years' in request.GET:
        try:
            amount = float(request.GET['amount'])
            rate = float(request.GET['rate'])
            years = int(request.GET['years'])
            
            # Simple Interest formula
            interest = (amount * rate * years) / 100
            total = amount + interest
        except ValueError:
            pass  # Keep defaults if input is invalid

    context = {
        'amount': amount,
        'rate': rate,
        'years': years,
        'interest': interest,
        'total': total,
    }
    return render(request, 'home_loan.html', context)
