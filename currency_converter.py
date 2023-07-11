import requests
from bs4 import BeautifulSoup as bs


# получение данных о курсе валют с сайта црб
def get_info():
    url = "http://www.cbr.ru/scripts/XML_daily.asp?"  # ссылка на xml файл
    req_currency = requests.get(url)
    soup = bs(req_currency.content, 'xml')
    usd_rub = float(soup.find(ID='R01235').Value.text.replace(",", '.'))  # получение курса $
    eur_rub = float(soup.find(ID='R01239').Value.text.replace(",", '.'))  # получение курса €
    return usd_rub, eur_rub

