import json
import os
import shutil

from config.settings.base import MEDIA_ROOT, PLATFORM_FILE_PATH


def moveFiles(source, destination):
    if os.path.exists(source):
        if not os.path.exists(destination):
            os.makedirs(destination)
        shutil.copy(source, destination)


if os.path.exists(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json"):
    tenant_data = {}
    with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json") as json_file:
        tenant_data = json.load(json_file)
        for tenant_name, t_config in tenant_data.items():
            if "static_image_file" in t_config:
                source = f'{MEDIA_ROOT}/tenant/login_screen/asset/background_images/{t_config["static_image_file"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/background_images/"
                moveFiles(source, destination)

            if "totalImages" in t_config:
                for i in range(1, int(t_config["totalImages"]) + 1):
                    image = "image_slider_file" + str(i)
                    source = f"{MEDIA_ROOT}/tenant/login_screen/asset/slider_images/{t_config[image]}"
                    destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/slider_images/"
                    moveFiles(source, destination)

            if "video_file_bg" in t_config:
                source = (
                    f'{MEDIA_ROOT}/tenant/login_screen/asset/background_video/{t_config["video_file_bg"]}'
                )
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/background_video/"
                moveFiles(source, destination)

            if "logo_on_screen" in t_config:
                source = f'{MEDIA_ROOT}/tenant/login_screen/asset/logo/{t_config["logo_on_screen"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/logo/"
                moveFiles(source, destination)

            if "logo_on_form" in t_config:
                source = f'{MEDIA_ROOT}/tenant/login_screen/asset/logo/{t_config["logo_on_form"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/logo/"
                moveFiles(source, destination)

            if "login_favicon_file" in t_config:
                source = f'{MEDIA_ROOT}/tenant/login_screen/asset/favicon/{t_config["login_favicon_file"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/login_screen/favicon/"
                moveFiles(source, destination)

            if "appdrawer_bg_image" in t_config:
                source = f'{MEDIA_ROOT}/tenant/appdrawer/asset/background_images/{t_config["appdrawer_bg_image_name"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/appdrawer/background_images/"
                moveFiles(source, destination)

            if "logo-file-appdrawer" in t_config:
                source = f'{MEDIA_ROOT}/tenant/appdrawer/asset/logo/{t_config["logo-file-appdrawer"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/appdrawer/logo/"
                moveFiles(source, destination)

            if "logo-file-topnavbar" in t_config:
                source = f'{MEDIA_ROOT}/tenant/appdrawer/asset/logo/{t_config["logo-file-topnavbar"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/appdrawer/logo/"
                moveFiles(source, destination)

            if "appdrawer_favicon_file" in t_config:
                source = f'{MEDIA_ROOT}/tenant/appdrawer/asset/favicon/{t_config["appdrawer_favicon_file"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/appdrawer/favicon/"
                moveFiles(source, destination)

            if "logo_file_error_page" in t_config:
                source = (
                    f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/logo/{t_config["logo_file_error_page"]}'
                )
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/logo/"
                moveFiles(source, destination)

            if "subprocess_bg" in t_config:
                source = (
                    f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/background/{t_config["subprocess_bg"]}'
                )
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/background/"
                moveFiles(source, destination)

            if "404bg" in t_config:
                source = f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/background/{t_config["404bg"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/background/"
                moveFiles(source, destination)

            if "500bg" in t_config:
                source = f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/background/{t_config["500bg"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/background/"
                moveFiles(source, destination)

            if "403bg" in t_config:
                source = f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/background/{t_config["403bg"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/background/"
                moveFiles(source, destination)

            if "permission_bg" in t_config:
                source = (
                    f'{MEDIA_ROOT}/tenant/custom_error_pages/asset/background/{t_config["permission_bg"]}'
                )
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/custom_error_pages/background/"
                moveFiles(source, destination)

            if "logo_on_tenant" in t_config:
                source = f'{MEDIA_ROOT}/tenant/tenant_admin/asset/logo/{t_config["logo_on_tenant"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/tenant_admin/logo/"
                moveFiles(source, destination)

            if "tenant_static_image_file" in t_config:
                source = f'{MEDIA_ROOT}/tenant/tenant_admin/asset/background_images/{t_config["tenant_static_image_file"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/tenant_admin/background_images/"
                moveFiles(source, destination)

            if "tenant_totalimage" in t_config:
                for i in range(1, int(t_config["tenant_totalimage"]) + 1):
                    image = "tenant_image_slider_file" + str(i)
                    source = f"{MEDIA_ROOT}/tenant/tenant_admin/asset/slider_images/{t_config[image]}"
                    destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/tenant_admin/slider_images/"
                    moveFiles(source, destination)

            if "video_file_bg_tenant" in t_config:
                source = f'{MEDIA_ROOT}/tenant/tenant_admin/asset/background_video/{t_config["video_file_bg_tenant"]}'
                destination = f"{MEDIA_ROOT}/{tenant_name}/TenantTheme/tenant_admin/background_video/"
                moveFiles(source, destination)

            if "login_slider_style" in t_config:
                new_path = t_config["login_slider_style"].replace(
                    "tenant/login_screen/asset", f"{tenant_name}/TenantTheme/login_screen"
                )
                t_config.update({"login_slider_style": new_path})

            if "tenant_slider_style" in t_config:
                new_path = t_config["tenant_slider_style"].replace(
                    "tenant/tenant_admin/asset", f"{tenant_name}/TenantTheme/tenant_admin"
                )
                t_config.update({"tenant_slider_style": new_path})

            with open(f"{PLATFORM_FILE_PATH}tenant_database_mapping.json", "w") as json_file:
                json.dump(tenant_data, json_file, indent=4)
                json_file.close()


if os.path.exists(f"{PLATFORM_FILE_PATH}app_database_mapping.json"):
    with open(f"{PLATFORM_FILE_PATH}app_database_mapping.json") as json_file:
        app_db_mapping = json.load(json_file)
        json_file.close()

        tenant_app_dict = {}

        # looping through existing apps in existing tenants:
        for key in app_db_mapping:
            tenant_name = key[: key.rindex("_")]
            app_name = key[key.rindex("_") + 1 :]
            if tenant_name in tenant_app_dict:
                tenant_app_dict[tenant_name].append(app_name)
            else:
                tenant_app_dict[tenant_name] = [app_name]

        for tenant, app in tenant_app_dict.items():
            for i in app:
                if os.path.exists(f"{MEDIA_ROOT}/Themefiles/{tenant}/{i}"):
                    source = f"{MEDIA_ROOT}/Themefiles/{tenant}/{i}"
                    destination = f"{MEDIA_ROOT}/{tenant}/{i}/Themefiles/"
                    dest = shutil.copytree(source, destination, dirs_exist_ok=True)


if os.path.exists(f"{MEDIA_ROOT}/tenant/"):
    shutil.rmtree(f"{MEDIA_ROOT}/tenant/", ignore_errors=False)

if os.path.exists(f"{MEDIA_ROOT}/Themefiles/"):
    shutil.rmtree(f"{MEDIA_ROOT}/Themefiles/", ignore_errors=False)
