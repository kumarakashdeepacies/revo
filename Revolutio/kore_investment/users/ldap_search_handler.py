import concurrent.futures
import json
import os

import ldap

from config.settings.base import LDAP_ACTIVATED, PLATFORM_FILE_PATH

ldap_data = {}
if os.path.exists(f"{PLATFORM_FILE_PATH}ldap_configuration.json"):
    with open(f"{PLATFORM_FILE_PATH}ldap_configuration.json") as json_file:
        ldap_data = json.load(json_file)
        json_file.close()
else:
    pass


def ldap_user_processing(details):
    details = details[1]
    user_details = {
        "0": details["sAMAccountName"][0].decode("utf-8"),
    }
    if details.get("givenName"):
        user_details["1"] = details["givenName"][0].decode("utf-8")
    else:
        user_details["1"] = ""
    if details.get("sn"):
        user_details["2"] = details["sn"][0].decode("utf-8")
    else:
        user_details["2"] = ""
    if details.get("mail"):
        user_details["3"] = details["mail"][0].decode("utf-8")
    else:
        user_details["3"] = ""
    if details.get("Department"):
        user_details["4"] = details["Department"][0].decode("utf-8")
    else:
        user_details["4"] = ""
    return user_details


def ldap_user_search(tenant, filter_string):
    result_set = []
    if LDAP_ACTIVATED == "true" and ldap_data.get(tenant):
        ldap_details = ldap_data[tenant]
        conn = ldap.initialize(ldap_details["ldap_server_uri"])
        user_dn = ldap_details["ldap_bind_dn"]
        password = ldap_details["ldap_bind_password"]
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        ldap.set_option(ldap.OPT_PROTOCOL_VERSION, 3)
        conn.simple_bind_s(user_dn, password)
        base_dn = ldap_details["ldap_user_search_domain"]
        result_set = []
        if isinstance(base_dn, list):
            for dn in base_dn:
                ldap_result_set = conn.search_s(
                    dn,
                    ldap.SCOPE_SUBTREE,
                    filter_string,
                    ["sAMAccountName", "givenName", "sn", "mail", "Department"],
                )
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = [executor.submit(ldap_user_processing, rel) for rel in ldap_result_set]
                    result_set += [future.result() for future in futures]
        else:
            ldap_result_set = conn.search_s(
                base_dn,
                ldap.SCOPE_SUBTREE,
                filter_string,
                ["sAMAccountName", "givenName", "sn", "mail", "Department"],
            )
            result_set = []
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = [executor.submit(ldap_user_processing, rel) for rel in ldap_result_set]
                result_set = [future.result() for future in futures]
    else:
        pass
    return result_set
