from allauth.account import views as django_authview
from django.conf import settings
from django.conf.urls import handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView

from kore_investment.users import authentication_backend as custom_authentication_views, views as userviews

urlpatterns = [
    path("", userviews.LandingView, name="applicationlanding"),
    # Custom redirects for Login Page and Password Change Pages
    path("accounts/login/", custom_authentication_views.user_login, name="login"),
    path("accounts/logout/", custom_authentication_views.user_logout, name="logout"),
    path(
        "accounts/password/reset_password/",
        custom_authentication_views.reset_password_new,
        name="reset_password_new",
    ),
    path(
        "accounts/password/reset_p/",
        django_authview.PasswordResetView.as_view(template_name="account/password_reset.html"),
        name="password_reset",
    ),
    path(
        "accounts/password_reset/done/",
        django_authview.PasswordResetDoneView.as_view(template_name="account/password_reset_done.html"),
        name="reset_password_done",
    ),
    path("accounts/password/change/", custom_authentication_views.update_password, name="password_change"),
    re_path(
        r"^accounts/password/new_password/(?P<username>\w+)/$",
        custom_authentication_views.reset_update_password,
        name="reset_update_password",
    ),
    path(
        "accounts/username_validation/",
        custom_authentication_views.check_username_validation,
        name="check_username_validation",
    ),
    path(
        "accounts/password_validation/",
        custom_authentication_views.check_password_validation,
        name="check_password_validation",
    ),
    path(
        "accounts/email_validation/",
        custom_authentication_views.check_email_validation,
        name="check_email_validation",
    ),
    path("accounts/signup/", custom_authentication_views.user_sign_up, name="user_sign_up"),
    path("admin_login/", custom_authentication_views.admin_login, name="admin_login"),
    path("applicationlogin/", custom_authentication_views.new_user_login, name="applicationlogin"),
    path("microsoftadsignin/", userviews.microsoftadsignin, name="microsoftsignin"),
    path("microsoftadsignout/", userviews.microsoftadsignout, name="microsoftsignout"),
    path("callback", userviews.callback, name="callback"),
    path("about/", TemplateView.as_view(template_name="pages/about.html"), name="about"),
    path("char_count", userviews.char_count, name="char_count"),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path(r"users/", include("kore_investment.users.urls", namespace="users")),
    # Tenant URLs
    path(r"tenant_admin/", include(("tenant_admin.urls", "tenant_admin"), namespace="tenant_admin")),
    # Platform URLs
    path(r"platform_admin/", include(("platform_admin.urls", "platform_admin"), namespace="platform_admin")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path(r"^search/", include("haystack.urls")),
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
        path("403/", userviews.forbidden_403),
        path("404/", userviews.error_404_view),
        path("500/", userviews.error_500_view),
        path("502/", userviews.error_502_view),
        path("503/", userviews.error_503_view),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
urlpatterns += [re_path(r"403/", userviews.forbidden_403)]
urlpatterns += [re_path(r"502/", userviews.error_502_view)]
urlpatterns += [re_path(r"503/", userviews.error_503_view)]
urlpatterns += [re_path(r".*", userviews.error_404_view)]

handler500 = userviews.error_500_view
handler403 = userviews.forbidden_403
