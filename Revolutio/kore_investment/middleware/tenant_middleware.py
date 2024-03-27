from django.urls import resolve
from django_multitenant.utils import set_current_tenant

from kore_investment.utils.utilities import tenant_schema_from_request


class MultitenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        app_name = resolve(request.path_info).app_names
        tenant = tenant_schema_from_request(request, app_name=app_name)
        from kore_investment.users.models import Instance

        tenant = Instance.objects.get(name=tenant)
        set_current_tenant(tenant)
        response = self.get_response(request)
        return response
