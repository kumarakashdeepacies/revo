import pickle

from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django_multitenant.utils import get_current_tenant

from config.settings.base import redis_instance


class sessionCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        instance = get_current_tenant()
        tenant = instance.name
        if redis_instance.exists(tenant + "mulsession" + request.user.username) == 1:
            user_login_info = pickle.loads(redis_instance.get(tenant + "mulsession" + request.user.username))
            old_session_id = user_login_info["session_key"]
            if request.session.session_key == old_session_id:
                logout(request)
                redis_instance.delete(tenant + "mulsession" + request.user.username)
                return HttpResponseRedirect("/applicationlogin/")
            else:
                pass
        else:
            pass
        if redis_instance.exists(tenant + f"force_logout{request.user.id}") == 1:
            redis_instance.delete(tenant + f"force_logout{request.user.id}")
            logout(request)
            return HttpResponseRedirect("/applicationlogin/")
        else:
            pass
        response = self.get_response(request)
        return response
