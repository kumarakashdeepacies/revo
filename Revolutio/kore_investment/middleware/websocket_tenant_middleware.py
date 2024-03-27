import json

from asgiref.sync import sync_to_async
from django_multitenant.utils import set_current_tenant

from config.settings.base import PLATFORM_FILE_PATH, tenant_host_mapper


@sync_to_async
def get_tenant(hostname):
    schema = "public"
    if tenant_host_mapper.get(hostname):
        schema = tenant_host_mapper[hostname]
    else:
        tenants_map = {}
        with open(f"{PLATFORM_FILE_PATH}tenant_host_mapping.json") as json_file:
            tenants_map = json.load(json_file)
            json_file.close()
        if tenants_map.get(hostname):
            schema = tenants_map.get(hostname)
        else:
            pass
    from kore_investment.users.models import Instance

    instance = Instance.objects.get(name=schema)
    return instance


class TenantMiddleware:
    """
    Custom middleware (insecure) that takes user IDs from the query string.
    """

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):
        # Look up tenant from scope
        hostname = {"host": str(v, "utf-8") for i, v in scope["headers"] if i == b"host"}
        hostname = hostname["host"].split(":")[0].lower()
        instance = await get_tenant(hostname)
        set_current_tenant(instance)
        scope["tenant"] = instance.name
        return await self.app(scope, receive, send)
