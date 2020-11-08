import azure.functions
import logging
from json import dumps
from __app__.shared.auth_lib import check_token
from __app__.shared.database import get_rows_as_dict_array

async def get_race(params: dict) -> list:
    rid = int(params.get('rid'))
    bid = int(params.get('bid', '0'))
    logging.debug(rid)
    races = await get_rows_as_dict_array('''
        select *
        from races_new
        where rid = %s
        and (bid = %s or %s = 0)''', rid, bid, bid)
    return races

async def add_race(params: dict):
    authenticated, payload, status_code = check_token(req)
    if not authenticated:
        return
    pass

async def delete_race(params: dict):
    if not authenticated:
        return
    pass

async def update_race(params: dict):
    if not authenticated:
        return
    pass

method_map = {
    "GET": get_race,
    "POST": add_race,
    "DELETE": delete_race,
    "PUT": update_race
}

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        ret_value = await method_map.get(req.method, lambda x: None)(req.params)
        return azure.functions.HttpResponse(dumps(ret_value, default=str))
    except Exception as e:
        logging.error(f"get races failed, {e}")
        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)
