import aiohttp
import base64


def convert_doc(name):
    with open(f"{name}", "rb") as file:
        return base64.b64encode(file.read())


async def didox_get_token(config):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.misc.didox_token_url, data={"password": config.misc.didox_pass}) as \
                response:
            return await response.json()


async def didox_create_doc(config, doc_name):
    token = await didox_get_token(config)
    encoded_doc = convert_doc(doc_name)
    async with aiohttp.ClientSession(headers={
        'user-key': token['token'],
        'Content-Type': 'application/json'}) as session:
        async with session.post(url=config.misc.didox_url, json={"data": {
            "isValid": True,
            "Buyer": {
                "DepartmentName": "",
                "DepartmentTin": "",
                "TaxGap": None,
                "Name": "\"VENKON GROUP\" MCHJ",
                "Address": "Фидойилар МФЙ, Махтумкули кучаси,  "
            },
            "didoxorderid": "",
            "Document": {
                "DocumentNo": "тест",
                "DocumentDate": "2023-06-08",
                "DocumentName": ""
            },
            "ContractDoc": {
                "ContractNo": "",
                "ContractDate": ""
            },
            "Seller": {
                "TaxGap": None,
                "Name": "\"WEBMEDIA INFORMATION\" MCHJ",
                "BranchCode": "",
                "BranchName": "",
                "Address": "ГОРОД ТАШКЕНТ ЯККАСАРАЙСКИЙ РАЙОН Хамид Сулаймон МФЙ, Глинка кучаси, 41а-уй  "
            },
            "SellerTin": "300974584",
            "BuyerTin": "302936161"
        },
            "document": f"data:application/pdf;base64,{encoded_doc}"}) as \
                response:
            return await response.json()
