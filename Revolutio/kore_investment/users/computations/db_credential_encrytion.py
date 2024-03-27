import base64
import logging
import random
import string

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes  # only for AES CBC mode
from Crypto.Util.Padding import pad, unpad


def decrypt_db_credential(request):
    encrypted_username = request.POST["username"]
    encrypted_secret_key = request.POST["password"]
    encrypted_password = encrypted_secret_key[: len(encrypted_secret_key) - 16]
    encrypted_server = request.POST["server"]
    encrypted_port = request.POST["port"]
    encrypted_db_name = request.POST["database"]
    key = encrypted_secret_key[len(encrypted_secret_key) - 16 :]
    iv = key
    iv = key.encode("utf-8")  # 16 char for AES128
    key = key.encode("utf-8")  # 16 char for AES128
    enc = pad(encrypted_password.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    user_secret_key = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_username.encode("utf-8"), 16)
    username = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_server.encode("utf-8"), 16)
    server = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_port.encode("utf-8"), 16)
    port = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_db_name.encode("utf-8"), 16)
    database = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    connection_code = key.decode("utf-8", "ignore")
    return server, port, database, username, user_secret_key, connection_code


def decrypt_existing_db_credentials(server, port, database, username, user_secret_key, connection_code):
    encrypted_username = username
    encrypted_password = user_secret_key
    encrypted_server = server
    encrypted_port = port
    encrypted_db_name = database
    key = connection_code
    iv = key.encode("utf-8")  # 16 char for AES128
    key = key.encode("utf-8")  # 16 char for AES128
    enc = pad(encrypted_password.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    user_secret_key = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_username.encode("utf-8"), 16)
    username = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_server.encode("utf-8"), 16)
    server = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_port.encode("utf-8"), 16)
    port = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = pad(encrypted_db_name.encode("utf-8"), 16)
    database = unpad(cipher.decrypt(base64.b64decode(enc)), 16).decode("utf-8", "ignore")
    connection_code = key.decode("utf-8", "ignore")
    return server, port, database, username, user_secret_key


def encrypt_db_credentials(server, port, database, username, user_secret_key):
    key = "".join(random.choices(string.ascii_uppercase + string.digits, k=16))
    iv = key.encode("utf-8")  # 16 char for AES128
    key = key.encode("utf-8")  # 16 char for AES128
    data = pad(server.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    server = base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")
    data = pad(port.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    port = base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")
    data = pad(database.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    database = base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")
    data = pad(username.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    username = base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")
    data = pad(user_secret_key.encode("utf-8"), 16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    user_secret_key = base64.b64encode(cipher.encrypt(data)).decode("utf-8", "ignore")
    connection_code = key.decode("utf-8", "ignore")
    return server, port, database, username, user_secret_key, connection_code
