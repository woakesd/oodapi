import azure.functions
import logging
from json import dumps
from __app__.shared.auth_lib import authorization
from __app__.shared.database import get_rows_as_dict_array

async def get_race(req: azure.functions.HttpRequest) -> object:
    rid = int(req.params.get('rid', '0'))
    bid = int(req.params.get('bid', '0'))
    logging.debug(f'Processing request for race id {rid}, bid {bid}')
    races = await get_rows_as_dict_array('''
        select *
        from races_new
        where rid = %s
        and (bid = %s or %s = 0)''', rid, bid, bid)
    return races

@authorization
async def add_race(req: azure.functions.HttpRequest, payload: dict) -> object:
    pass

@authorization
async def delete_race(req: azure.functions.HttpRequest, payload: dict) -> object:
    pass

@authorization
async def update_race(req: azure.functions.HttpRequest, payload: dict) -> object:
    pass

method_map = {
    "GET": get_race,
    "POST": add_race,
    "DELETE": delete_race,
    "PUT": update_race
}

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        ret_value = await method_map.get(req.method, lambda x: {})(req)
        return azure.functions.HttpResponse(dumps(ret_value, default=str))
    except Exception as e:
        logging.error(f"get races failed, {e}")
        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)
