from allauth.account import views as django_authview
from django.conf import settings
from django.urls import include, path, re_path
from django.views import defaults as default_views

from platform_admin import authentication_backend as platform_custom_auth
from platform_admin.decorators import login_required

from . import views

urlpatterns = [
    path("", login_required(views.index), name="index"),
    path("accounts/login/", platform_custom_auth.user_login, name="platform_login"),
    path("accounts/logout/", platform_custom_auth.user_logout, name="platform_logout"),
    path(
        "accounts/password/reset_password/",
        platform_custom_auth.reset_password_new,
        name="platform_reset_password_new",
    ),
    path(
        "accounts/password/reset_p/",
        django_authview.PasswordResetView.as_view(template_name="platform_admin/account/password_reset.html"),
        name="platform_password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        django_authview.PasswordResetDoneView.as_view(
            template_name="platform_admin/account/password_reset_done.html"
        ),
        name="platform_reset_password_done",
    ),
    path("accounts/password/change/", platform_custom_auth.update_password, name="platform_password_change"),
    re_path(
        r"^accounts/password/new_password/(?P<username>\w+)/$",
        platform_custom_auth.reset_update_password,
        name="platform_reset_update_password",
    ),
    re_path(r".*", login_required(views.redirect_index), name="redirect_to_index"),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
