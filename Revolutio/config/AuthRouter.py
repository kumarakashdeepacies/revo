class AuthRouter:
    """
    A router to control all database operations on models in the
    auth application.
    """

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth models go to auth_db.
        """
        if model._meta.app_label not in [
            "users",
        ]:
            return "default"
        elif model._meta.app_label in ["users"] and model._meta.model_name in [
            "user",
            "profile",
            "configuration_parameter",
            "userpermission_master",
            "permissionaccess",
            "usergroup_approval",
            "user_approval",
            "allocated_licences",
            "user_model",
            "userpermission_interim",
            "group_details",
            "user_navbar",
            "failed_login_alerts",
            "dashboard_config",
            "login_trail",
            "audit_trail",
            "instance",
            "notification_management",
            "applicationaccess",
        ]:
            return "default"
        else:
            return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth models go to default.
        """
        if model._meta.app_label not in [
            "users",
        ]:
            return "default"
        elif model._meta.app_label in ["users"] and model._meta.model_name in [
            "user",
            "profile",
            "configuration_parameter",
            "userpermission_master",
            "permissionaccess",
            "usergroup_approval",
            "user_approval",
            "allocated_licences",
            "user_model",
            "userpermission_interim",
            "group_details",
            "user_navbar",
            "failed_login_alerts",
            "dashboard_config",
            "login_trail",
            "audit_trail",
            "instance",
            "notification_management",
            "applicationaccess",
        ]:
            return "default"
        else:
            return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth app is involved.
        """
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth app only appears in the 'default'
        database.
        """
        if app_label not in [
            "users",
        ]:
            return db == "default"
        elif app_label in ["users"] and model_name in [
            "user",
            "profile",
            "configuration_parameter",
            "userpermission_master",
            "permissionaccess",
            "usergroup_approval",
            "user_approval",
            "allocated_licences",
            "user_model",
            "userpermission_interim",
            "group_details",
            "user_navbar",
            "failed_login_alerts",
            "dashboard_config",
            "login_trail",
            "audit_trail",
            "instance",
            "notification_management",
            "applicationaccess",
        ]:
            return db == "default"
        else:
            return False
