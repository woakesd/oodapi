import azure.functions
import logging

async def main(req: azure.functions.HttpRequest) -> azure.fubctions.HttpResponse:
    try:
        return azure.fubctions.HttpResponse('hello world')
    except:
        logging.except("return failed")