# -*- coding: utf-8 -*-

from typing import Iterable
import inspect
import os
import logging
import requests

logger = logging.getLogger(__name__)

DECK_SERVER_URL = os.environ["DECK_SERVER_URL"]


def execute_operations(operations: Iterable[dict], params: dict = {}, environ: dict = {}) -> bool:
    return all(execute_single_operation(operation, params, environ) for operation in operations)

def execute_single_operation(operation: dict, params: dict, environ: dict) -> bool:
    logger.info(f"operation={str(operation)}, params={str(params)}, environ={str(environ)}")
    ret = getattr(OperationExecutor, operation["operation"])(operation["arguments"], params, environ)
    logger.info(ret)
    return ret

class OperationExecutor:

    @classmethod
    def confirm(cls, args, params, environ) -> bool:
        logger.info(f"{inspect.currentframe().f_code.co_name}: {str(args)}")
        state = spot_state()
        if state is None:
            return False
        spot = environ[args["spot"]]
        if spot not in state:
            return False
        exist = args.get("exist", True)
        return (state[spot] is not None) == exist

    @classmethod
    def move(cls, args, params, environ) -> bool:
        logger.info(f"{inspect.currentframe().f_code.co_name}: {str(args)}")
        state = spot_state()
        if state is None:
            return False
        from_spot = environ[args["from_spot"]]
        if from_spot not in state or state[from_spot] is None:
            return False
        to_spot = environ[args["to_spot"]]
        if to_spot not in state or state[to_spot] is not None:
            return False
        return move_item(from_spot, to_spot)

    @classmethod
    def consume(cls, args, params, environ) -> bool:
        logger.info(f"{inspect.currentframe().f_code.co_name}: {str(args)}")
        return use(environ[args["consumable"]], args["amount"])

    @classmethod
    def update(cls, args, params, environ) -> bool:
        logger.info(f"{inspect.currentframe().f_code.co_name}: {str(args)}")
        return update(environ[args["consumable"]], args["amount"])

def http_request_put(url: str, json: dict) -> bool:
    response = requests.put(url, json=json)
    logger.info(f"http_request_put {dict(status_code=response.status_code, response_body=response.json())}")
    if response.status_code == 200:
        return True
    else:
        return False

def http_request_post(url: str, json: dict) -> bool:
    response = requests.post(url, json=json)
    logger.info(f"http_request_post {dict(status_code=response.status_code, response_body=response.json())}")
    if response.status_code == 200:
        return True
    else:
        return False

def http_request_patch(url: str, json: dict) -> bool:
    response = requests.patch(url, json=json)
    logger.info(f"http_request_patch {dict(status_code=response.status_code, response_body=response.json())}")
    if response.status_code == 200:
        return True
    else:
        return False

def put_item(spot: str, uuid: str, item_type: str) -> bool:
    url = f"{DECK_SERVER_URL}/put_item/{spot}/"
    payload = dict(uuid=uuid, item_type=item_type)
    return http_request_put(url, payload)

def delete_item(spot: str) -> bool:
    url = f"{DECK_SERVER_URL}/delete_item/{spot}/"
    response = requests.delete(url)
    log.info("delete", status_code=response.status_code, response_body=response.json())
    if response.status_code == 200:
        return True
    else:
        return False

def move_item(from_spot: str, to_spot: str) -> bool:
    url = f"{DECK_SERVER_URL}/move"
    payload = dict(from_spot=from_spot, to_spot=to_spot)
    return http_request_post(url, payload)

def spot_state() -> dict | None:
    url = f"{DECK_SERVER_URL}/state"
    response = requests.get(url)
    logger.info(f"get: {dict(status_code=response.status_code, response_body=response.json())}")
    if response.status_code == 200:
        return response.json()
    else:
        return None

def new_consumable(item_type: str, amount: int) -> bool:
    url = f"{DECK_SERVER_URL}/new_consumable"
    payload = dict(item_type=item_type, amount=amount)
    return http_request_post(url, payload)

def remove_consumable(item_type: str) -> bool:
    url = f"{DECK_SERVER_URL}/remove_consumable/{item_type}/"
    response = requests.delete(url)
    log.info("delete", status_code=response.status_code, response_body=response.json())
    if response.status_code == 200:
        return True
    else:
        return False

def update(item_type: str, amount: int) -> bool:
    url = f"{DECK_SERVER_URL}/update/"
    payload = dict(item_type=item_type, amount=amount)
    return http_request_patch(url, payload)

def refill(item_type: str, amount: int) -> bool:
    url = f"{DECK_SERVER_URL}/refill/"
    payload = dict(item_type=item_type, amount=amount)
    return http_request_patch(url, payload)

def use(item_type: str, amount: int) -> bool:
    url = f"{DECK_SERVER_URL}/use/"
    payload = dict(item_type=item_type, amount=amount)
    return http_request_patch(url, payload)

def consumables_state() -> dict | None:
    url = f"{DECK_SERVER_URL}/consumables_state"
    response = requests.get(url)
    logger.info(f"get: {dict(status_code=response.status_code, response_body=response.json())}")
    if response.status_code == 200:
        return response.json()
    else:
        return None
