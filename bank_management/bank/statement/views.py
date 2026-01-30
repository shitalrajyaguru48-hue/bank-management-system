from django.shortcuts import render
# Create your views here.
# statement/views.py
from django.contrib.auth.decorators import login_required
from accounts.models import Profile
from .models import Statement
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth.decorators import login_required
from statement.models import Statement
from accounts.models import Profile

@login_required
def customer_statement(request):
    customer = Profile.objects.get(user=request.user)

    statements = Statement.objects.filter(
        customer=customer
    ).order_by('-created_at')

    return render(request, 'customer/customer_statement.html', {
        'statements': statements
    })
@login_required
def download_statement_pdf(request):
    profile = Profile.objects.get(user=request.user)

    # Only customer can download
    if profile.role != 'customer':
        return redirect('login')

    statements = Statement.objects.filter(customer=profile).order_by('-created_at')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="account_statement.pdf"'

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 50

    # Title
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(180, y, "Account Statement")
    y -= 40

    # Customer info
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, y, f"Customer: {profile.user.get_full_name() or profile.user.username}")
    y -= 20
    pdf.drawString(50, y, f"Account Number: {profile.user.account.account_number}")
    y -= 30

    # Table headers
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y, "Date")
    pdf.drawString(180, y, "Type")
    pdf.drawString(260, y, "Amount")
    pdf.drawString(360, y, "Balance After")
    y -= 15

    pdf.setFont("Helvetica", 10)

    for s in statements:
        if y < 50:
            pdf.showPage()
            y = height - 50

        pdf.drawString(50, y, s.created_at.strftime("%d-%m-%Y %H:%M"))
        pdf.drawString(180, y, s.transaction_type.title())
        pdf.drawString(260, y, str(s.amount))
        pdf.drawString(360, y, str(s.balance_after))
        y -= 15

    pdf.showPage()
    pdf.save()

    return response
