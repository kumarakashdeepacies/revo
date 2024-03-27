from storages.backends.azure_storage import AzureStorage


class PrivateAzureStorageUAT(AzureStorage):
    account_name = "revolutiouatdatastore"
    account_key = "ztIN0J1z+QfNRP+YItGimdULuwqktL7rxS9lcORwD5KyhSQJlXBQ6Ffc6NQtGkfw0E84eM7qYnJHxgFZjngusw=="
    azure_container = "$web"
    expiration_secs = 300


class PrivateAzureStorage(AzureStorage):
    account_name = "revolutiodatastore"
    account_key = "rXHujD88ddf26Gw+Elq2uhazawVY2mcgLtd5R3U6scY9c03SOs/ucEvTIo4BI63Abg2xGRDwxqeTHIgN4Ax9hQ=="
    azure_container = "$web"
    expiration_secs = 300
