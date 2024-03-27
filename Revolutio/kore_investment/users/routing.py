from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/run_process_multi_run/(?P<model_name>\w+(\s*\w+))/",
        consumers.run_process_multi_run.as_asgi(),
    ),
    re_path(
        r"ws/run_process_multi_run_inter/(?P<model_name>\w+(\s*\w+))/",
        consumers.run_process_multi_run_inter.as_asgi(),
    ),
    re_path(
        r"ws/run_model_multi_run/(?P<model_name>\w+(\s*\w+))/",
        consumers.run_model_multi_run.as_asgi(),
    ),
    re_path(
        r"ws/run_model_multi_run_inter/(?P<model_name>\w+(\s*\w+))/",
        consumers.run_model_multi_run_inter.as_asgi(),
    ),
    re_path(
        r"ws/queued_job_output/(?P<job_id>\w+(\s*\w+))/",
        consumers.queued_job_output.as_asgi(),
    ),
    re_path(
        r"ws/queued_upload_output/(?P<job_id>\w+(\s*\w+))/",
        consumers.queued_upload_output.as_asgi(),
    ),
    re_path(
        r"ws/queued_audit_filter_output/(?P<job_id>\w+(\s*\w+))/",
        consumers.queued_audit_filter_output.as_asgi(),
    ),
    re_path(
        r"ws/queued_navbar_update/",
        consumers.queued_navbar_job_output.as_asgi(),
    ),
    re_path(
        r"ws/queued_tenant_deletion/(?P<job_id>\w+(\s*\w+))/",
        consumers.queued_tenant_deletion.as_asgi(),
    ),
]
