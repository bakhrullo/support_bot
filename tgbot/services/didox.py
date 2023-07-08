import aiohttp
import base64


def convert_doc(name):
    with open(f"{name}", "rb") as file:
        return base64.b64encode(file.read())


async def didox_get_token(config):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=config.misc.didox_token_url, data={"password": config.misc.didox_pass}) as \
                response:
            print(response)
            return await response.json()

async def get_info(config, inn, token):
    async with aiohttp.ClientSession(headers={
        'user-key': token,
        'Content-Type': 'application/json'}) as session:
        async with session.get(url=f"{config.misc.didox_inn_url}{inn}") as response:
            return await response.json()


async def didox_create_doc(config, doc_name, doc_no, doc_inn=None):
    token = await didox_get_token(config)
    encoded_doc = str(convert_doc(doc_name), encoding="utf-8")
    res = await get_info(config, doc_inn, token['token'])
    async with aiohttp.ClientSession(headers={
        'user-key': token['token'],
        'Content-Type': 'application/json'}) as session:
        async with session.post(url=config.misc.didox_url, json={"data": {
            "isValid": True,
            "Buyer": {
                "DepartmentName": "",
                "DepartmentTin": "",
                "TaxGap": None,
                "Name": res["shortName"],
                "Address": res["address"]
            },
            "didoxorderid": "",
            "Document": {
                "DocumentNo": doc_no,
                "DocumentDate": "2023-06-08",
                "DocumentName": ""
            },
            "ContractDoc": {
                "ContractNo": "",
                "ContractDate": ""
            },
            "Seller": {
                "TaxGap": None,
                "Name": "«SUPPORT SAMARQAND» MCHJ",
                "BranchCode": "",
                "BranchName": "",
                "Address": "ARNASOY KO`CHASI, 1A-UY"
            },
            "SellerTin": "300974584",
            "BuyerTin": doc_inn
        },
            "document": f"data:application/pdf;base64,{encoded_doc}"}) as \
                response:
            return await response.json()
