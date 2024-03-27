import ftplib
import glob
import json
import logging
import os
import re
import stat

from azure.storage.blob import BlobClient, ContainerClient
import boto3
import pandas as pd
import paramiko

from config.settings.base import DISKSTORE_PATH, PLATFORM_FILE_PATH
from kore_investment.users.computations.file_storage import to_diskstorage


def connect_to_sftp(config_dict, elementid):
    connection = config_dict["inputs"]["connection"]
    filename = "sftp_remote_info.json"
    hostname = ""
    username = ""
    user_secret_key = ""
    file_type = config_dict["inputs"]["file_type"]
    file_path = config_dict["inputs"]["file_path"]
    file_regex = config_dict["inputs"]["file_regex"]
    newlist = []
    rename_list = []
    rename_config = config_dict["inputs"]["renameConfig"]
    selected_files = config_dict["inputs"]["files"]
    if os.path.exists(f"{PLATFORM_FILE_PATH}{filename}"):
        with open(f"{PLATFORM_FILE_PATH}{filename}", "r+") as fout:
            content = json.load(fout)
            hostname = content[connection]["hostname"]
            username = content[connection]["username"]
            user_secret_key = content[connection]["user_secret_key"]
            fout.close()
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(hostname=hostname, username=username, password=user_secret_key)
        sftp_client = ssh_client.open_sftp()
        try:
            sftp_client.stat(file_path)
            sftp_client.chdir(file_path)
            file_attr = sftp_client.listdir_attr()
            file_sftp_list = sftp_client.listdir()
            filtered_sftp_list = []
            for i, sftp_attr in zip(file_sftp_list, file_attr):
                if stat.S_ISREG(sftp_attr.st_mode):
                    filtered_sftp_list.append(i)
            if file_regex:
                sftp_regex = re.compile(f"{file_regex}.*{file_type}")
            else:
                sftp_regex = re.compile(f".*{file_type}")
            newlist = list(filter(sftp_regex.search, filtered_sftp_list))
            for f in newlist:
                rfile = f
                rfile2 = rfile
                if rename_config and rfile in rename_config:
                    rfile = rename_config[rfile]
                else:
                    rfile = rfile.split(".")[0]
                if rfile2 in selected_files:
                    rename_list.append(rfile)
                    sftp_client.get(f"{file_path}/{f}", f"{DISKSTORE_PATH}{f}")

            if file_type == "csv":
                if os.path.exists(f"{DISKSTORE_PATH}"):
                    list_of_files = glob.glob(f"{DISKSTORE_PATH}*.csv")
                    for i in list_of_files:
                        rfile = i.split("/")[-1]
                        rfile2 = rfile
                        if rfile in selected_files:
                            if rename_config and rfile in rename_config:
                                rfile = rename_config[rfile]
                            else:
                                rfile = rfile.split(".")[0]
                            try:
                                data_csv = pd.read_csv(i, skip_blank_lines=True)
                                file_name = f"{elementid}_{rfile}"
                                to_diskstorage(data_csv, file_name)
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            except Exception as e:
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                                logging.warning(f"Following exception occured - {e}")
                        else:
                            os.remove(i)
            elif file_type == "xlsx":
                if os.path.exists(f"{DISKSTORE_PATH}"):
                    list_of_files = glob.glob(f"{DISKSTORE_PATH}*.xlsx")
                    for i in list_of_files:
                        rfile = i.split("/")[-1]
                        rfile2 = rfile
                        if rfile in selected_files:
                            if rename_config and rfile in rename_config:
                                rfile = rename_config[rfile]
                            else:
                                rfile = rfile.split(".")[0]
                            try:
                                data_csv = pd.read_excel(i, engine="openpyxl")
                                file_name = f"{elementid}_{rfile}"
                                to_diskstorage(data_csv, file_name)
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            except Exception as e:
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                                logging.warning(f"Following exception occured - {e}")
                        else:
                            os.remove(i)

        except Exception as e:
            logging.warning(f"Exception occured when downloading file")
            return newlist, rename_list
        ssh_client.close()
    except paramiko.AuthenticationException as e:
        logging.warning(f"Exception occured when connecting to Server")
        return newlist, rename_list

    return newlist, rename_list


def findFTPfiles(ftp, directory):
    ftp.cwd(directory)
    filenames = []
    act_file = []
    ftp.retrlines("NLST", filenames.append)
    for name in filenames:
        try:
            findFTPfiles(ftp, name)
        except ftplib.error_perm:
            act_file.append(name)
    return act_file


def connect_to_ftp(config_dict, elementid):
    connection = config_dict["inputs"]["connection"]
    filename = "ftp_remote_info.json"
    hostname = ""

    file_type = config_dict["inputs"]["file_type"]
    file_path = config_dict["inputs"]["file_path"]
    file_regex = config_dict["inputs"]["file_regex"]

    newlist = []
    rename_list = []

    rename_config = config_dict["inputs"]["renameConfig"]
    selected_files = config_dict["inputs"]["files"]

    if os.path.exists(f"{PLATFORM_FILE_PATH}{filename}"):
        with open(f"{PLATFORM_FILE_PATH}{filename}", "r+") as fout:
            content = json.load(fout)
            hostname = content[connection]["hostname"]
            fout.close()
    try:
        ftp = ftplib.FTP(hostname)
        ftp.login()
        try:
            ftp.cwd(file_path)
            act_files = findFTPfiles(ftp, file_path)
            os.chdir(DISKSTORE_PATH)
            ftp.cwd(file_path)
            if file_regex:
                r = re.compile(f"{file_regex}.*{file_type}")
            else:
                r = re.compile(f".*{file_type}")
            newlist = list(filter(r.search, act_files))
            for f in newlist:
                if rename_config and f in rename_config:
                    rfile = rename_config[f]
                else:
                    rfile = f.split(".")[0]
                if f in selected_files:
                    with open(f, "wb") as fp:
                        ftp.retrbinary(f"RETR {f}", fp.write)
                    rename_list.append(rfile)

            if file_type == "csv":
                if os.path.exists(f"{DISKSTORE_PATH}"):
                    list_of_files = glob.glob(f"{DISKSTORE_PATH}*.csv")
                    for i in list_of_files:
                        rfile = i.split("/")[-1]
                        rfile2 = rfile
                        if rfile in selected_files:
                            if rename_config and rfile in rename_config:
                                rfile = rename_config[rfile]
                            else:
                                rfile = rfile.split(".")[0]
                            try:
                                data_csv = pd.read_csv(i, skip_blank_lines=True)
                                file_name = f"{elementid}_{rfile}"
                                to_diskstorage(data_csv, file_name)
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            except Exception as e:
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                                logging.warning(f"Following exception occured - {e}")
                        else:
                            os.remove(i)
            elif file_type == "xlsx":
                if os.path.exists(f"{DISKSTORE_PATH}"):
                    list_of_files = glob.glob(f"{DISKSTORE_PATH}*.xlsx")
                    for i in list_of_files:
                        rfile = i.split("/")[-1]
                        rfile2 = rfile
                        if rfile in selected_files:
                            if rename_config and rfile in rename_config:
                                rfile = rename_config[rfile]
                            else:
                                rfile = rfile.split(".")[0]
                            try:
                                data_csv = pd.read_excel(i, engine="openpyxl")
                                file_name = f"{elementid}_{rfile}"
                                to_diskstorage(data_csv, file_name)
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            except Exception as e:
                                os.remove(f"{DISKSTORE_PATH}{rfile2}")
                                logging.warning(f"Following exception occured - {e}")
                        else:
                            os.remove(i)

        except Exception as e:
            logging.warning(f"Following exception occured - {e}")
        ftp.close()
    except Exception as e:
        ftp.close()
        logging.warning(f"Following exception occured - {e}")

    return newlist, rename_list


def connect_to_awsS3(config_dict, elementid):
    connection = config_dict["inputs"]["connection"]
    filename = "awsS3_remote_info.json"
    username = ""
    user_secret_key = ""
    file_type = config_dict["inputs"]["file_type"]
    file_path = config_dict["inputs"]["file_path"]
    file_regex = config_dict["inputs"]["file_regex"]
    newlist = []
    rename_list = []
    rename_config = config_dict["inputs"]["renameConfig"]
    selected_files = config_dict["inputs"]["files"]
    if os.path.exists(f"{PLATFORM_FILE_PATH}{filename}"):
        with open(f"{PLATFORM_FILE_PATH}{filename}", "r+") as fout:
            content = json.load(fout)
            content[connection]["hostname"]
            username = content[connection]["username"]
            user_secret_key = content[connection]["user_secret_key"]
            fout.close()

    try:
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=username,
            aws_secret_access_key=user_secret_key,
        )

        s3_resource = boto3.resource(
            "s3",
            aws_access_key_id=username,
            aws_secret_access_key=user_secret_key,
        )
        response = s3_client.list_objects_v2(Bucket=file_path)
        act_files = list(obj["Key"] for obj in response["Contents"] if "/" not in obj["Key"])
        if file_regex:
            r = re.compile(f"{file_regex}.*{file_type}")
        else:
            r = re.compile(f".*{file_type}")
        newlist = list(filter(r.search, act_files))
        os.chdir(DISKSTORE_PATH)
        for f in newlist:
            if rename_config and f in rename_config:
                rfile = rename_config[f]
            else:
                rfile = f.split(".")[0]
            if f in selected_files:
                rename_list.append(rfile)
                try:
                    s3_resource.Object(file_path, f).download_file(f"{DISKSTORE_PATH}{f}")
                except Exception as e:
                    logging.warning(f"Exception occured when downloading file")

        if file_type == "csv":
            if os.path.exists(f"{DISKSTORE_PATH}"):
                list_of_files = glob.glob(f"{DISKSTORE_PATH}*.csv")
                for i in list_of_files:
                    rfile = i.split("/")[-1]
                    rfile2 = rfile
                    if rfile in selected_files:
                        if rename_config and rfile in rename_config:
                            rfile = rename_config[rfile]
                        else:
                            rfile = rfile.split(".")[0]
                        try:
                            data_csv = pd.read_csv(i, skip_blank_lines=True)
                            file_name = f"{elementid}_{rfile}"
                            to_diskstorage(data_csv, file_name)
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                        except Exception as e:
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            logging.warning(f"Following exception occured - {e}")
                    else:
                        os.remove(i)
        elif file_type == "xlsx":
            if os.path.exists(f"{DISKSTORE_PATH}"):
                list_of_files = glob.glob(f"{DISKSTORE_PATH}*.xlsx")
                for i in list_of_files:
                    rfile = i.split("/")[-1]
                    rfile2 = rfile
                    if rfile in selected_files:
                        if rename_config and rfile in rename_config:
                            rfile = rename_config[rfile]
                        else:
                            rfile = rfile.split(".")[0]
                        try:
                            data_csv = pd.read_excel(i, engine="openpyxl")
                            file_name = f"{elementid}_{rfile}"
                            to_diskstorage(data_csv, file_name)
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                        except Exception as e:
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            logging.warning(f"Following exception occured - {e}")
                    else:
                        os.remove(i)

    except Exception as e:
        logging.warning(f"Following exception occured - {e}")

    return newlist, rename_list


def connect_to_azure(config_dict, elementid):
    connection = config_dict["inputs"]["connection"]
    filename = "azure_remote_info.json"
    username = ""
    user_secret_key = ""
    file_type = config_dict["inputs"]["file_type"]
    file_path = config_dict["inputs"]["file_path"]
    file_regex = config_dict["inputs"]["file_regex"]
    newlist = []
    rename_list = []
    rename_config = config_dict["inputs"]["renameConfig"]
    selected_files = config_dict["inputs"]["files"]
    if os.path.exists(f"{PLATFORM_FILE_PATH}{filename}"):
        with open(f"{PLATFORM_FILE_PATH}{filename}", "r+") as fout:
            content = json.load(fout)
            content[connection]["hostname"]
            username = content[connection]["username"]
            user_secret_key = content[connection]["user_secret_key"]
            fout.close()

    try:
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={username};AccountKey={user_secret_key};EndpointSuffix=core.windows.net"

        container = ContainerClient.from_connection_string(
            conn_str=connection_string, container_name=file_path
        )
        act_files = []
        blob_list = container.list_blobs()
        for blob in blob_list:
            act_files.append(blob.name)

        if file_regex:
            r = re.compile(f"{file_regex}.*{file_type}")
        else:
            r = re.compile(f".*{file_type}")
        newlist = list(filter(r.search, act_files))
        os.chdir(DISKSTORE_PATH)
        for f in newlist:
            if rename_config and f in rename_config:
                rfile = rename_config[f]
            else:
                rfile = f.split(".")[0]
            if f in selected_files:
                rename_list.append(rfile)
                try:
                    blob = BlobClient.from_connection_string(
                        conn_str=connection_string, container_name=file_path, blob_name=f
                    )

                    with open(f"./{f}", "wb") as my_blob:
                        blob_data = blob.download_blob()
                        blob_data.readinto(my_blob)

                except Exception as e:
                    logging.warning(f"Exception occured when downloading file")

        if file_type == "csv":
            if os.path.exists(f"{DISKSTORE_PATH}"):
                list_of_files = glob.glob(f"{DISKSTORE_PATH}*.csv")
                for i in list_of_files:
                    rfile = i.split("/")[-1]
                    rfile2 = rfile
                    if rfile in selected_files:
                        if rename_config and rfile in rename_config:
                            rfile = rename_config[rfile]
                        else:
                            rfile = rfile.split(".")[0]
                        try:
                            data_csv = pd.read_csv(i, skip_blank_lines=True)
                            file_name = f"{elementid}_{rfile}"
                            to_diskstorage(data_csv, file_name)
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                        except Exception as e:
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            logging.warning(f"Following exception occured - {e}")
                    else:
                        os.remove(i)
        elif file_type == "xlsx":
            if os.path.exists(f"{DISKSTORE_PATH}"):
                list_of_files = glob.glob(f"{DISKSTORE_PATH}*.xlsx")
                for i in list_of_files:
                    rfile = i.split("/")[-1]
                    rfile2 = rfile
                    if rfile in selected_files:
                        if rename_config and rfile in rename_config:
                            rfile = rename_config[rfile]
                        else:
                            rfile = rfile.split(".")[0]
                        try:
                            data_csv = pd.read_excel(i, engine="openpyxl")
                            file_name = f"{elementid}_{rfile}"
                            to_diskstorage(data_csv, file_name)
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                        except Exception as e:
                            os.remove(f"{DISKSTORE_PATH}{rfile2}")
                            logging.warning(f"Following exception occured - {e}")
                    else:
                        os.remove(i)
    except Exception as e:
        logging.warning(f"Following exception occured - {e}")

    return newlist, rename_list
