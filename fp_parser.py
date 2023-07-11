from functools import reduce

from bs4 import BeautifulSoup as BS
import requests as req
import cfg

funpay_url = cfg.funpay_url


def get_all_orders_by_server(url = funpay_url, server_code = None):

    resp = req.get(url)
    bs = BS(resp.text, 'html.parser')
    orders_list = bs.find_all('a', 'tc-item')
    result_orders_list = list()

    for data in orders_list:

        if int(data.get('data-server')) == server_code and data.get('data-online') == '1':

            tc_server = data.find('div', class_='tc-server hidden-xxs').text
            tc_amount = data.find("div", class_="tc-amount").text
            tc_price = float(data.find("div", class_="tc-price").text.strip().split()[0])
            offer_url = data.get("href")
            temp_list = [tc_server, tc_amount, tc_price, offer_url]
            result_orders_list.append(temp_list)
            if len(result_orders_list) > 10:
                break
    return result_orders_list


#Лучшая цена
def get_orders_by_filter(price, url=funpay_url, server_code=None):

    resp = req.get(url)
    bs = BS(resp.text, 'html.parser')
    orders_list = bs.find_all('a', 'tc-item')
    result_orders_list = list()

    for data in orders_list:

        if int(data.get('data-server')) == server_code and data.get('data-online') == '1' and \
                float(data.find("div", class_="tc-price").text.strip().split()[0]) <= price:
            tc_server = data.find('div', class_='tc-server hidden-xxs').text
            tc_amount = data.find("div", class_="tc-amount").text
            tc_price = float(data.find("div", class_="tc-price").text.strip().split()[0])
            offer_url = data.get("href")
            temp_list = [tc_server, tc_amount, tc_price, offer_url]
            result_orders_list.append(temp_list)

    return result_orders_list


def get_avg_price(server_code=None):
    price_list = get_all_orders_by_server(server_code=server_code)
    return reduce(lambda a, x: a+x[2], price_list, 0) / len(price_list)


if __name__ == '__main__':
    print(get_avg_price(server_code=8569))
