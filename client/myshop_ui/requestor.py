import time
import requests
import traceback

USER_AGENT_HEADER_TAG = 'User-Agent'

class ServiceFailedException(Exception):
    def __init__(self, error_msg, status_code):
        self.error_msg = error_msg
        self.status_code = status_code


def add_headers(kwargs):
    kwargs.setdefault('headers', {})['User-Agent'] = "myshop-ui"
    kwargs.setdefault('headers', {})['Content-type'] = "application/json"

def is_ok_code_response(code):
    return 200 <= code < 400

def _make_request(func, url, retries, delay, backoff, *args, **kwargs):

    if retries <= 0:
        retries = 1

    retry = False
    response = None
    last_raised_exception = None
    last_raised_exception_tb = None

    for _ in range(retries):
        try:
            response = func(url, *args, **kwargs)
            if response.status_code in [408, 502, 503, 504]:
                retry = True
            else:
                retry = False
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout
        ) as e:
            retry = True
            last_raised_exception = e
            last_raised_exception_tb = traceback.format_exc()

        if retry:
            time.sleep(delay)
            delay *= backoff
        else:
            break

    if response and is_ok_code_response(response.status_code):
        return response

    if response is not None:
        raise ServiceFailedException(response.text, response.status_code)
    else:
        error_msg = type(last_raised_exception).__name__
        raise ServiceFailedException(error_msg, 500)


def get(url, retries=5, delay=1, backoff=1, *args, **kwargs):
    return _make_request(
        requests.get,
        url,
        retries,
        delay,
        backoff,
        *args,
        **kwargs
    )


def post(url, retries=0, delay=1, backoff=1, *args, **kwargs):
    return _make_request(
        requests.post,
        url,
        retries,
        delay,
        backoff,
        *args,
        **kwargs
    )
