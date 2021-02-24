import inspect
import sys
import json
import logging


class Handler(object):
    def __init__(self, headers, body):
        self.headers = headers
        self.body = body


def list_module_classes(module):
    ans = {}
    for name, obj in inspect.getmembers(sys.modules[module.__name__], inspect.isclass):
        if inspect.isclass(obj):
            ans[name] = obj
    return ans


def is_valid_body(body_text):
    try:
        body = json.loads(body_text)
    except Exception as e:
        logging.error(str(e))
        return None, {
            "message": "Invalid json format.",
            "details": str(e)
        }
    return body, None


def is_invalid_request(body):
    if 'method' not in body:
        return {"message": "Method not found in request."}

    if body["method"].count(".") != 1:
        return {"message": "The format of `method` is <class_name>.<method_name>"}

    if 'args' in body and type(body['args']) != list:
        return {'message': "<args> should be an array."}

    if 'kwargs' in body and type(body['kwargs']) != dict:
        return {'message': '<kwargs> should be an dictionary.'}

    return None


def get_class_method(method):
    return method.split('.')


def get_args(body):
    args = body['args'] if 'args' in body else []
    kwargs = body['kwargs'] if 'kwargs' in body else {}
    return args, kwargs


if __name__ == "__main__":
    pass