import azure.functions

async def main(req: azure.functions.HttpRequest) -> azure.fubctions.HttpResponse:
    return azure.fubctions.HttpResponse('hello world')
