import azure.functions

async def main(req: azure.functions.HttpRequest) -> str:
    return 'hello world'

