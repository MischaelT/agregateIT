from unittest.mock import MagicMock

from currency.models import Rate
from currency.tasks import parse_monobank, parse_privatbank, parse_vkurse


def test_parse_privatbank(mocker):

    privatbank_response = [
        {"ccy": "USD", "base_ccy": "UAH", "buy": "26.50000", "sale": "26.90000"},
        {"ccy": "EUR", "base_ccy": "UAH", "buy": "30.95000", "sale": "31.55000"},
        {"ccy": "RUR", "base_ccy": "UAH", "buy": "0.35000", "sale": "0.38000"},
        {"ccy": "BTC", "base_ccy": "USD", "buy": "39310.2844", "sale": "43448.2090"},
    ]

    initial_count_rate = Rate.objects.count()
    request_get_mock = mocker.patch('requests.get')
    request_get_mock.return_value = MagicMock(json=lambda: privatbank_response)

    parse_privatbank()
    assert Rate.objects.count() == initial_count_rate + 2

    parse_privatbank()
    assert Rate.objects.count() == initial_count_rate + 2

    privatbank_response = [
        {"ccy": "USD", "base_ccy": "UAH", "buy": "26.60000", "sale": "26.90000"},
    ]
    request_get_mock.return_value = MagicMock(json=lambda: privatbank_response)

    parse_privatbank()
    assert Rate.objects.count() == initial_count_rate + 3


def test_parse_monobank(mocker):

    initial_value = Rate.objects.count()
    request_get_mock = mocker.patch('requests.get')

    monobank_response = [
        {'currencyCodeA': '840', 'currencyCodeB': '980', 'date': '1634274811',  'rateBuy': '23.3', 'rateSell': '23.5', 'rateCross': '6.741'},  # noqa
        {'currencyCodeA': '978', 'currencyCodeB': '980', 'date': '1634159406',  'rateBuy': '30.5', 'rateSell': '32', 'rateCross': '6.741'},  # noqa
        {'currencyCodeA': '124', 'currencyCodeB': '980', 'date': '1634274811', 'rateCross': '21.4523'},
        {'currencyCodeA': '976', 'currencyCodeB': '980', 'date': '1634159406', 'rateCross': '0.0134'},
    ]
    request_get_mock.return_value = MagicMock(json=lambda: monobank_response)

    parse_monobank()
    assert Rate.objects.count() == initial_value + 2

    monobank_response = [
        {'currencyCodeA': '840', 'currencyCodeB': '980', 'date': '1634274811',  'rateBuy': '23.6', 'rateSell': '23.9', 'rateCross': '6.741'},  # noqa
        {'currencyCodeA': '675', 'currencyCodeB': '980', 'date': '1634159406',  'rateBuy': '30.5', 'rateSell': '32', 'rateCross': '6.741'},  # noqa
    ]
    request_get_mock.return_value = MagicMock(json=lambda: monobank_response)

    parse_monobank()
    assert Rate.objects.count() == initial_value + 3


def test_parse_vkurse(mocker):

    initial_value = Rate.objects.count()
    request_get_mock = mocker.patch('requests.get')

    vkurse_response = {
        'Dollar': {'buy': '8', 'sale': '17'},
        'Lira': {'buy': '65', 'sale': '69'},
        'Rub': {'buy': '0.377', 'sale': '0.398'}
    }
    request_get_mock.return_value = MagicMock(json=lambda: vkurse_response)

    parse_vkurse()
    assert Rate.objects.count() == initial_value + 1

    vkurse_response = {'Aut': {'buy': '8', 'sale': '17'},
                       'Lira': {'buy': '65', 'sale': '69'},
                       'Rub': {'buy': '0.377', 'sale': '0.398'}}

    request_get_mock.return_value = MagicMock(json=lambda: vkurse_response)

    parse_vkurse()
    assert Rate.objects.count() == initial_value + 1
