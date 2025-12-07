from django.shortcuts import render, get_object_or_404
from .models import Company
from django.shortcuts import render, redirect

from .forms import CompanyForm



def company_pages(request):
    selected_company = request.GET.get("company")

    companies = list(Company.objects.all())

    # ✅ Selected company কে list-এর প্রথমে আনা
    if selected_company:
        companies.sort(
            key=lambda c: str(c.id) != str(selected_company)
        )

    return render(request, "pages/company_pages.html", {
        "companies": companies,
        "selected_company": selected_company,
    })


# ✅ Permanent Link (Never changes)
def company_public_by_uid(request, uid):
    company = get_object_or_404(Company, uid=uid)
    return render(request, "pages/company_public.html", {"company": company})


# ✅ Name Based Auto Link
def company_public_by_slug(request, slug):
    company = get_object_or_404(Company, slug=slug)
    return render(request, "pages/company_public.html", {"company": company})


def add_company(request):
    from .forms import CompanyForm

    form = CompanyForm()

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("app_pages:company_pages")

    return render(request, "pages/add_company_page.html", {
        "form": form
    })



def edit_company(request, id):
    company = get_object_or_404(Company, id=id)

    if request.method == "POST":
        form = CompanyForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            return redirect("app_pages:company_pages")
    else:
        form = CompanyForm(instance=company)

    return render(request, "pages/add_company_page.html", {
        "form": form,
        "edit_mode": True,
        "company": company,   # ✅ এটা খুব জরুরি
    })
