import asyncio
from decimal import Decimal

import requests

from bs4 import BeautifulSoup

from django.core.cache import cache

from currency import const
from currency import model_choices as choices
from currency.services import get_latest_rates

import aiohttp


def round_currency(num):
    return Decimal(num).quantize(Decimal('.01'))


def make_tasks() -> list:

    tasks = []

    parsers = [parse_privatbank, parse_monobank,
               parse_vkurse, parse_minfin, parse_pumb]

    for parser in parsers:
        task = asyncio.ensure_future(parser)
        tasks.append(task)

    return tasks


async def parse_privatbank() -> None:

    """
        celery task for parsing rates from privatbank.ua
    """

    from currency.models import Rate, Source

    url = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

    source = Source.objects.get_or_create(
        code_name=const.CODE_NAME_PRIVATBANK,
        defaults={'name': 'PrivatBank'},
    )[0]

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            rates = response.json()

    available_currency_types = {'USD': choices.TYPE_USD,
                                'EUR': choices.TYPE_EUR, }

    for rate in rates:

        currency_name = rate['ccy']

        if currency_name in available_currency_types:

            bid = round_currency(rate['buy'])
            ask = round_currency(rate['sale'])

            ct = available_currency_types[currency_name]

            last_rate = Rate.objects.filter(
                currency_name=ct,
                source=source,
            ).order_by('created').last()

            if (
                last_rate is None or
                last_rate.bid != bid or
                last_rate.ask != ask
            ):

                Rate.objects.create(
                    ask=ask,
                    bid=bid,
                    currency_name=ct,
                    source=source,
                )
                cache.delete(const.CACHE_KEY_LATEST_RATES)
                get_latest_rates()


async def parse_monobank() -> None:

    """
        Celery task for parsing rates from monobank.ua
    """

    from currency.models import Rate, Source

    source = Source.objects.get_or_create(
        code_name=const.CODE_NAME_MONOBANK,
        defaults={'name': 'MonoBank'},
    )[0]

    url = 'https://api.monobank.ua/bank/currency'

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            rates = response.json()

    available_currency_codes = {'840': choices.TYPE_USD,
                                '978': choices.TYPE_EUR,
                                '980': choices.TYPE_HRN}

    for rate in rates:
        first_currency_code = str(rate['currencyCodeA'])
        second_currency_code = str(rate['currencyCodeB'])
        grivna_code = '980'

        if first_currency_code in available_currency_codes and second_currency_code == grivna_code:

            bid = round_currency(rate['rateBuy'])
            ask = round_currency(rate['rateSell'])

            currency_name = available_currency_codes.get(first_currency_code)

            last_rate = Rate.objects.filter(
                currency_name=currency_name,
                source=source,
            ).order_by('created').last()

            if (
                last_rate is None or
                last_rate.bid != bid or
                last_rate.ask != ask
            ):

                Rate.objects.create(
                    ask=ask,
                    bid=bid,
                    currency_name=currency_name,
                    source=source,
                )


async def parse_vkurse() -> None:

    """
        Celery task for parsing rates from vkurse.ua
    """

    from currency.models import Rate, Source

    source = Source.objects.get_or_create(
        code_name=const.CODE_NAME_VKURSE,
        defaults={'name': 'Vkurse.ua'},
    )[0]

    url = 'http://vkurse.dp.ua/course.json'

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url) as response:
            json_data = response.json()

    available_currency_names = {'Dollar': choices.TYPE_USD,
                                'Euro': choices.TYPE_EUR, }

    currency_names = json_data.keys()

    # currency_names is the dictionary, where the keys is a currency names

    for name in currency_names:

        if name in available_currency_names:

            currency_name = available_currency_names.get(name)

            rate = json_data.get(name)
            bid = round_currency(rate['buy'])
            ask = round_currency(rate['sale'])

            last_rate = Rate.objects.filter(
                currency_name=currency_name,
                source=source,
            ).order_by('created').last()

            if (
                last_rate is None or
                last_rate.bid != bid or
                last_rate.ask != ask
            ):

                Rate.objects.create(
                    ask=ask,
                    bid=bid,
                    currency_name=currency_name,
                    source=source,
                )


async def parse_minfin() -> None:

    """
        Celery task for parsing rates from minfin.ua
    """

    from currency.models import Rate, Source

    source = Source.objects.get_or_create(
        code_name=const.CODE_NAME_MINFIN,
        defaults={'name': 'MinFin'},
    )[0]

    urls = {choices.TYPE_USD: 'https://minfin.com.ua/currency/banks/usd/',
            choices.TYPE_EUR: 'https://minfin.com.ua/currency/banks/eur/', }

    for currency_name in urls:

        async with aiohttp.ClientSession(raise_for_status=True) as session:
            async with session.get(urls.get(currency_name)) as response:
                soup = BeautifulSoup(response.text, 'html.parser')

        for span in soup("span"):
            span.decompose()

        # get the list where the first position is buy, second is sell
        result = soup.find('td', {'data-title': "Средний курс"}).text.split()
        bid = round_currency(result[0])
        ask = round_currency(result[1])

        last_rate = Rate.objects.filter(
            currency_name=currency_name,
            source=source,
        ).order_by('created').last()

        if (
            last_rate is None or
            last_rate.bid != bid or
            last_rate.ask != ask
        ):

            Rate.objects.create(
                ask=ask,
                bid=bid,
                currency_name=currency_name,
                source=source,
            )


async def parse_pumb() -> None:

    """
        Celery task for parsing rates from pumb.ua
    """

    from currency.models import Rate, Source

    source = Source.objects.get_or_create(
        code_name=const.CODE_NAME_PUMB,
        defaults={'name': 'PUMB'},
    )[0]

    url = 'https://about.pumb.ua/ru/info/currency_converter'

    available_currency_names = {'USD': choices.TYPE_USD,
                                'EUR': choices.TYPE_EUR, }

    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(urls.get(currency_name)) as response:
            soup = BeautifulSoup(response.text, 'html.parser')

    table = soup.find('table')

    for row in table.find_all('tr'):

        col = row.find_all('td')
        # We get a childs' elements of a table row as a list, but since in one of them will not be <td> tag,
        #  so the list would be empty and we can not get it by index
        try:
            name = col[0].text
        except IndexError:
            continue

        if name in available_currency_names:

            currency_name = available_currency_names.get(name)

            try:
                bid = col[1].text
                ask = col[2].text
            except IndexError:
                continue

            last_rate = Rate.objects.filter(
                currency_name=currency_name,
                source=source,
            ).order_by('created').last()

            if (
                last_rate is None or
                last_rate.bid != bid or
                last_rate.ask != ask
            ):

                Rate.objects.create(
                    ask=ask,
                    bid=bid,
                    currency_name=currency_name,
                    source=source,
                )
