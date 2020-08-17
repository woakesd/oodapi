import azure.functions
import logging

async def main(req: azure.functions.HttpRequest) -> azure.functions.HttpResponse:
    try:
        return azure.functions.HttpResponse('hello world')
    except:
        logging.error("return failed")