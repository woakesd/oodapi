import azure.functions
import logging
from json import dumps
from __app__.auth_lib import authorization
from __app__.shared.database import get_rows_as_dict_array

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        rid = req.route_params.get('rid')
        logging.debug(rid)
        races = await get_rows_as_dict_array('select * from races_new where rid = %s', rid)
        return azure.functions.HttpResponse(dumps(races, default=str))
    except Exception as e:
        logging.error(f"get races failed, {e}")
        return azure.functions.HttpResponse(dumps({'fatal': e}, default=str), status_code=500)
