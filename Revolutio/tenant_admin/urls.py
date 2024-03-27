from allauth.account import views as django_authview
from django.conf import settings
from django.urls import include, path, re_path
from django.views import defaults as default_views

from kore_investment.users import views as kore_views
from tenant_admin import authentication_backend as tenant_custom_auth
from tenant_admin.decorators import login_required

from . import views

urlpatterns = [
    path("", login_required(views.index), name="index"),
    path("accounts/login/", tenant_custom_auth.user_login, name="tenant_login"),
    path("accounts/logout/", tenant_custom_auth.user_logout, name="tenant_logout"),
    path(
        "accounts/password/reset_password/",
        tenant_custom_auth.reset_password_new,
        name="tenant_reset_password_new",
    ),
    path(
        "accounts/password/reset_p/",
        django_authview.PasswordResetView.as_view(template_name="tenant_admin/account/password_reset.html"),
        name="tenant_password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        django_authview.PasswordResetDoneView.as_view(
            template_name="tenant_admin/account/password_reset_done.html"
        ),
        name="tenant_reset_password_done",
    ),
    path("accounts/password/change/", tenant_custom_auth.update_password, name="tenant_password_change"),
    re_path(
        r"^accounts/password/new_password/(?P<username>\w+)/$",
        tenant_custom_auth.reset_update_password,
        name="tenant_reset_update_password",
    ),
    re_path(
        r"^customizeTheme/(?P<app_mode>\w+)/$", login_required(views.customize_theme), name="customize_theme"
    ),
    path("login_preview/", login_required(views.login_preview), name="login_preview"),
    path("400_preview/", login_required(kore_views.error_404_view), name="400_preview"),
    path("subprocess_preview/", login_required(kore_views.subprocess_not_found), name="subprocess_preview"),
    path("500_preview/", login_required(kore_views.error_500_view), name="500_preview"),
    path("502_preview/", login_required(kore_views.error_502_view), name="502_preview"),
    path("503_preview/", login_required(kore_views.error_503_view), name="503_preview"),
    path("403_preview/", login_required(kore_views.forbidden_403), name="403_preview"),
    path(
        "permission_denied_preview/",
        login_required(kore_views.permission_denied),
        name="permission_denied_preview",
    ),
    path(
        "fetch_user_server_side/", login_required(views.fetch_user_server_side), name="fetch_user_server_side"
    ),
    path("user_management/", login_required(views.user_management), name="user_management"),
    re_path(
        r"^user_management/user_logout/(?P<id>\d+)/$",
        login_required(views.user_logout),
        name="user_logout",
    ),
    re_path(
        r"^(?P<app_code>[\w-]+)/previewTheme/(?P<theme_type>[\w-]+)/$",
        login_required(views.preview_theme),
        name="preview_theme",
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
