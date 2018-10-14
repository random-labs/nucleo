import datetime, hashlib, hmac, math, time

from django.conf import settings


def create_request_signature(unix_time, method, path, body=''):
    """
    Generate Stronghold request signature HMAC using SHA256.

    Encoded data is a concatenation of UNIX timestamp for request,
    HTTP request method, request path and request body.
    """
    hmac_obj = hmac.new(settings.STRONGHOLD_SECRET_KEY, digestmod=hashlib.sha256)
    hmac_obj.update(unix_time + method + path + body)
    return hmac_obj.hexdigest()

def create_request_headers(method, path, body=''):
    """
    Generate Stronghold request headers.

    Returns dictionary for header values.
    """
    unix_time = str(int(math.floor(time.time())))
    return {
        'SH-CRED-ID': settings.STRONGHOLD_CREDENTIAL_ID,
        'SH-CRED-SIG': create_request_signature(unix_time, method, path, body),
        'SH-CRED-TIME': unix_time,
        'SH-CRED-PASS': settings.STRONGHOLD_CREDENTIAL_PASSPHRASE,
    }
