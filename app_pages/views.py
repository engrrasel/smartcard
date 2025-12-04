from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def company_pages(request):
    return render(request, "pages/company_pages.html")
