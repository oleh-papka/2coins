import os

import requests
import json

from django.conf import settings
from django.utils import timezone

from misc.errors import Privat24APIError


def get_ccy_abbrs() -> list:
    file_path = os.path.join(settings.BASE_DIR, 'budget/fixtures/currencies.json')
    with open(file_path, "r") as file:
        data = file.read()
        json_data = json.loads(data)

    return [i['fields']['abbr'] for i in json_data]


def currency_converter(amount: float, from_ccy: str, to_ccy: str) -> float:
    base_privat_ccys = ('USD', 'EUR', 'UAH')
    if from_ccy in base_privat_ccys and to_ccy in base_privat_ccys:
        resp = requests.get(f"https://api.privatbank.ua/p24api/pubinfo?exchange&coursid=11")

        if resp.ok:
            resp_data = resp.json()
            ccy_dict = dict()

            for i in resp_data:
                ccy_dict[i['ccy']] = float(i['buy'])

            if 'UAH' in (from_ccy, to_ccy):
                if from_ccy == 'UAH':
                    res = round(amount / ccy_dict[to_ccy], 2)
                else:
                    res = round(ccy_dict[from_ccy] * amount, 2)
            else:
                from_price = ccy_dict[from_ccy] / ccy_dict[to_ccy]
                res = round(amount * from_price, 2)
        else:
            raise Privat24APIError
    else:
        date = timezone.now().strftime("%d.%m.%Y")
        resp = requests.get(f"https://api.privatbank.ua/p24api/exchange_rates?date={date}")

        if resp.ok:
            resp_data = resp.json()
            abbrs = get_ccy_abbrs()
            ccy_dict = dict()

            for i in resp_data['exchangeRate']:
                if i['currency'] in abbrs:
                    if i.get('purchaseRate'):
                        ccy_dict[i['currency']] = i['purchaseRate']

            if 'UAH' in (from_ccy, to_ccy):
                if from_ccy == 'UAH':
                    res = round(amount / ccy_dict[to_ccy], 2)
                else:
                    res = round(ccy_dict[from_ccy] * amount, 2)
            else:
                from_price = ccy_dict[from_ccy] / ccy_dict[to_ccy]
                res = round(amount * from_price, 2)
        else:
            raise Privat24APIError

    return res
