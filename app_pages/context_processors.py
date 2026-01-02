from .models import Company

def company_context(request):
    """
    Global company context:
    - user_companies  → logged-in user-এর সব company
    - selected_company → বর্তমানে selected company (if any)
    """

    if not request.user.is_authenticated:
        return {}

    companies = Company.objects.filter(owner=request.user)

    selected_company = None
    company_id = request.GET.get("company")

    if company_id:
        selected_company = companies.filter(id=company_id).first()

    return {
        "user_companies": companies,
        "selected_company": selected_company,
    }
