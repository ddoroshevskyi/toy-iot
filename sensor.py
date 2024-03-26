import inspect
import pprint
from datetime import datetime, timedelta
from json.decoder import JSONDecodeError
from os import getenv
from random import choice, randint, uniform
from uuid import uuid4

from aiohttp import web

"""
====================================================
Poor man's jsonrpc implementation
====================================================
"""
PROTOCOL_VERSION = "2.0"

PARSE_ERROR_CODE = -32700
PARSE_ERROR_MSG = "Parse error"
INVALID_REQUEST_CODE = -32600
INVALID_REQUEST_MSG = "Invalid request"
METHOD_NOT_FOUND_CODE = -32601
METHOD_NOT_FOUND_MSG = "Method not found"
INVALID_PARAMS_CODE = -32602
INVALID_PARAMS_MSG = "Invalid params"
INTERNAL_ERROR_CODE = -32603
INTERNAL_ERROR_MSG = "Internal error"
METHOD_ERROR_CODE = -32000
METHOD_ERROR_MSG = "Method execution error"


def new_jrpc_error(code: int, message: str, data: dict | None = None) -> dict:
    res = {"code": code, "message": message}

    if data:
        res["data"] = data

    return res


def new_jrpc_request(
    available_methods: dict,
    **kwargs,
) -> tuple:
    err = res = None

    jsonrpc = kwargs.get("jsonrpc")
    id = kwargs.get("id")
    method = kwargs.get("method")
    params = kwargs.get("params")

    if not jsonrpc or jsonrpc != PROTOCOL_VERSION:
        err = new_jrpc_error(
            INVALID_REQUEST_CODE,
            INVALID_REQUEST_MSG,
            {
                "field": "jsonrpc",
                "received": jsonrpc,
                "expected": PROTOCOL_VERSION,
            },
        )
        return err, res

    if not id or not isinstance(id, int):
        err = new_jrpc_error(
            INVALID_REQUEST_CODE,
            INVALID_REQUEST_MSG,
            {"field": "id", "received": id, "expected": "integer value"},
        )
        return err, res

    if not method or method not in available_methods:
        err = new_jrpc_error(
            METHOD_NOT_FOUND_CODE,
            METHOD_NOT_FOUND_MSG,
            {
                "field": "method",
                "received": method,
                "available_methods": list(available_methods.keys()),
            },
        )
        return err, res

    requested_method = available_methods[method]
    legal_params = [
        str(param) for param in inspect.signature(requested_method).parameters
    ]

    if legal_params:
        if not params:
            err = new_jrpc_error(
                INVALID_PARAMS_CODE,
                INVALID_PARAMS_MSG,
                {
                    "field": "params",
                    "received": params,
                    "expected_params": legal_params,
                },
            )
            return err, res

        requested_params = list(params.keys())

        if requested_params != legal_params:
            err = new_jrpc_error(
                INVALID_PARAMS_CODE,
                INVALID_PARAMS_MSG,
                {
                    "field": "params",
                    "received": list(params.keys()),
                    "expected_params": legal_params,
                },
            )
            return err, res

    res = {
        "jsonrpc": jsonrpc,
        "id": id,
        "method": method,
        "params": params,
    }

    return err, res


def new_jrpc_response(result: dict | None = None, error: dict | None = None) -> dict:
    res = {
        "jsonrpc": PROTOCOL_VERSION,
        "id": 1,
    }

    if result:
        res["result"] = result

    if error:
        res["error"] = error

    return res


"""
====================================================
Sensor
====================================================
"""
SENSOR_PIN = getenv("SENSOR_PIN", "0000")
SENSOR_HID = uuid4().hex
SENSOR_MODELS = ["RM85", "RM125", "RM250", "RMZ250"]
SENSOR_MODEL = choice(SENSOR_MODELS)

FACTORY_SENSOR_NAME = SENSOR_MODEL + "-default-site"
SENSOR_NAME = FACTORY_SENSOR_NAME

FACTORY_FIRMWARE_VERSION = 10
FIRMWARE_VERSION = FACTORY_FIRMWARE_VERSION

FACTORY_READING_INTERVAL = 3
READING_INTERVAL = FACTORY_READING_INTERVAL


SENSOR = {
    "name": SENSOR_NAME,
    "hid": SENSOR_HID,
    "model": SENSOR_MODEL,
    "firmware_version": FIRMWARE_VERSION,
    "reading_interval": READING_INTERVAL,
}


BACK_ONLINE_TIME = None
TEMPERATURE_READING = uniform(-50.00, 50.00)
NEXT_READING_TIME = datetime.now()


pprint.pprint(SENSOR)


"""
====================================================
Sensor methods
====================================================
"""


def get_info() -> tuple:
    return None, SENSOR


def get_methods() -> tuple:
    return None, [
        {
            method_name: [
                str(param) for param in inspect.signature(method_obj).parameters
            ]
        }
        for method_name, method_obj in SENSOR_METHODS.items()
    ]


def set_reading_interval(
    interval: int,
) -> tuple:
    err = res = None

    if not isinstance(interval, int):
        err = new_jrpc_error(
            METHOD_ERROR_CODE,
            METHOD_ERROR_MSG,
            {
                "param": "interval",
                "received": interval,
                "expected": "integer",
            },
        )
        return err, res

    SENSOR["reading_interval"] = interval

    global NEXT_READING_TIME
    NEXT_READING_TIME = datetime.now() + timedelta(
        seconds=SENSOR["reading_interval"]
    )

    return err, SENSOR


def set_name(
    name: str,
) -> tuple:
    err = res = None

    if not isinstance(name, str) or name == "":
        err = new_jrpc_error(
            METHOD_ERROR_CODE,
            METHOD_ERROR_MSG,
            {
                "param": "name",
                "received": name,
                "expected": "non-empty string",
            },
        )
        return err, res

    SENSOR["name"] = name

    return err, SENSOR


def reset_to_factory() -> tuple:
    global SENSOR
    global BACK_ONLINE_TIME
    reset_duration = randint(5, 13)
    BACK_ONLINE_TIME = datetime.now() + timedelta(seconds=reset_duration)

    SENSOR = {
        "name": FACTORY_SENSOR_NAME,
        "hid": SENSOR_HID,
        "model": SENSOR_MODEL,
        "firmware_version": FACTORY_FIRMWARE_VERSION,
        "reading_interval": FACTORY_READING_INTERVAL,
    }

    return None, "resetting"


def update_firmware() -> tuple:

    if SENSOR["firmware_version"] != 15:
        global BACK_ONLINE_TIME
        update_duration = randint(5, 13)
        BACK_ONLINE_TIME = datetime.now() + timedelta(seconds=update_duration)
        SENSOR["firmware_version"] += 1
        return None, "updating"

    return None, "already at latest firmware version"


def reboot() -> tuple:
    global BACK_ONLINE_TIME
    reboot_duration = randint(3, 8)
    BACK_ONLINE_TIME = datetime.now() + timedelta(seconds=reboot_duration)
    return None, "rebooting"


def get_reading() -> tuple:
    global TEMPERATURE_READING
    global NEXT_READING_TIME

    if NEXT_READING_TIME < datetime.now():
        TEMPERATURE_READING += uniform(-0.05, 0.05)
        NEXT_READING_TIME = datetime.now() + timedelta(
            seconds=SENSOR["reading_interval"]
        )

    return None, round(TEMPERATURE_READING, 2)


SENSOR_METHODS = {
    "get_info": get_info,
    "get_methods": get_methods,
    "set_name": set_name,
    "set_reading_interval": set_reading_interval,
    "reset_to_factory": reset_to_factory,
    "update_firmware": update_firmware,
    "reboot": reboot,
    "get_reading": get_reading,
}


"""
====================================================
HTTP server business
====================================================
"""


def mind_transitive_state(func):
    async def wrapper(*args, **kwargs):
        if BACK_ONLINE_TIME:
            now = datetime.now()

            if BACK_ONLINE_TIME > now:
                return web.Response(status=503)

        return await func(*args, **kwargs)

    return wrapper


@mind_transitive_state
async def handle_http_request(request) -> web.Response:
    err = req = None

    auth_header = request.headers.get("Authorization")
    if auth_header != SENSOR_PIN:
        return web.Response(status=401)

    if not request.body_exists:
        err = new_jrpc_error(
            PARSE_ERROR_CODE,
            PARSE_ERROR_MSG,
            {
                "error": "request body is missing",
            },
        )

        res = new_jrpc_response(error=err)
        return web.json_response(res)

    request_json = {}

    try:
        request_json = await request.json()
    except JSONDecodeError:
        err = new_jrpc_error(
            PARSE_ERROR_CODE,
            PARSE_ERROR_MSG,
            {
                "error": "failed to parse request body",
            },
        )

        res = new_jrpc_response(error=err)
        return web.json_response(res)

    err, req = new_jrpc_request(**request_json, available_methods=SENSOR_METHODS)

    if err:
        res = new_jrpc_response(error=err)
        return web.json_response(res)

    method = SENSOR_METHODS[req["method"]]
    params = req["params"]

    if params:
        err, res = method(**params)
    else:
        err, res = method()

    return web.json_response(new_jrpc_response(error=err, result=res))


def init_func(argv):
    app = web.Application()
    app.router.add_post("/rpc", handle_http_request)
    return app
