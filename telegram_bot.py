import datetime

import telebot
from telebot import types
import fp_parser
import funpay_database
from currency_converter import get_info
import cfg
from loguru import logger


bot = telebot.TeleBot(cfg.API)  # создание бота


@bot.message_handler(commands=["start"])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_action_with_offers = types.KeyboardButton("📊 Информация о лотах 📊")
    send_plot = types.KeyboardButton("💰 Информация о средней цене 💰")
    button_save_avg_price = types.KeyboardButton("Сохранить средную цену")
    markup.add(button_action_with_offers, send_plot, button_save_avg_price)
    bot.send_message(
        message.chat.id,
        text="Привет, {0.first_name}! Я  бот для сбора цен на Funpay".format(
            message.from_user
        ),
        reply_markup=markup,
    )


@logger.catch
@bot.message_handler(content_types=["text"])
def bot_actions(message):
    if message.text == "📊 Информация о лотах 📊":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_west_server = types.KeyboardButton("Западный сервер")
        button_east_server = types.KeyboardButton("Восточный сервер")
        button_return_to_main_menu = types.KeyboardButton("Вернуться в главное меню")
        markup.add(button_west_server, button_east_server, button_return_to_main_menu)
        bot.send_message(
            message.chat.id, text="Выберите нужный сервер", reply_markup=markup
        )

    elif message.text == "Западный сервер":
        cfg.server_id = 992

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_get_all_orders = types.KeyboardButton("Информация о всех лотах")
        button_filter_orders = types.KeyboardButton("Фильтрация лотов по цене")
        button_avg_price = types.KeyboardButton("Информация о средней цене")
        button_return_to_main_menu = types.KeyboardButton("Вернуться в главное меню")
        markup.add(
            button_get_all_orders,
            button_filter_orders,
            button_avg_price,
            button_return_to_main_menu,
        )
        bot.send_message(
            message.chat.id, text="Вы выбрали Западный сервер", reply_markup=markup
        )

    elif message.text == "Восточный сервер":
        cfg.server_id = 8569

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_get_all_orders = types.KeyboardButton("Информация о всех лотах")
        button_filter_orders = types.KeyboardButton("Фильтрация лотов по цене")
        button_avg_price = types.KeyboardButton("Информация о средней цене")
        button_return_to_main_menu = types.KeyboardButton("Вернуться в главное меню")
        markup.add(
            button_get_all_orders,
            button_filter_orders,
            button_avg_price,
            button_return_to_main_menu,
        )
        bot.send_message(
            message.chat.id, text="Вы выбрали Восточный сервер", reply_markup=markup
        )

    elif message.text == "Информация о всех лотах":
        fp_parser.get_all_orders_by_server(server_code=cfg.server_id)
        try:
            if cfg.server_id == 0:
                bot.send_message(message.chat.id, text="Выберите сервер заново!")

            for i in fp_parser.get_all_orders_by_server(server_code=cfg.server_id):
                message_to_bot = f"Сервер: {i[0]} \nКоличество серебра: {i[1]} \nЦена за 1кк: {i[2]} \nСсылка на лот: {i[3]}"
                bot.send_message(message.chat.id, text=message_to_bot)
        except Exception as error:
            logger.exception(error)

    elif message.text == "Фильтрация лотов по цене":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_price = types.KeyboardButton("Введите цену")
        button_return_to_main_menu = types.KeyboardButton("Вернуться в главное меню")
        markup.row(button_price, button_return_to_main_menu)
        bot.send_message(
            message.chat.id, text="Фильтрация по цене", reply_markup=markup
        )

    elif message.text == "Введите цену":
        bot.register_next_step_handler(message, reply_to_user)

    elif message.text == "Информация о средней цене":
        if cfg.server_id != 0:
            avg_price = fp_parser.get_avg_price(cfg.server_id)
            server_name = ""

            usd_rub, eur_rub = get_info()

            if cfg.server_id == 992:
                server_name = "WEST"
            elif cfg.server_id == 8569:
                server_name = "EAST"

            message_with_price = return_message(
                server_name, avg_price, usd_rub, eur_rub
            )

            bot.send_message(message.chat.id, message_with_price)
        else:
            bot.send_message(message.chat.id, "Выберите сервер заново!")

    elif message.text == "Вернуться в главное меню":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button_action_with_offers = types.KeyboardButton("📊 Информация о лотах 📊")
        send_plot = types.KeyboardButton("💰 Информация о средней цене 💰")
        markup.add(button_action_with_offers, send_plot)

        bot.send_message(
            message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup
        )

    elif message.text == "Сохранить средную цену":
        avg_price = format(fp_parser.get_avg_price(server_code=992), "0.2f")
        date_now = datetime.date.today()
        date_now = str(date_now).split('-')
        db_connect = funpay_database.sql_connection()

        try:
            funpay_database.sqt_table_insert(db_connect, [992, float(avg_price), *date_now])
        except Exception as error:
            logger.error(error)

    elif message.text == '/help':
        try:
            help_message = 'Тут может быть реклама'
            bot.send_message(message.chat.id, text=help_message)
        except Exception as error:
            logger.error(error)
    else:
        bot.send_message(
            message.chat.id, text="Напишите /start для начала работы!"
        )


def reply_to_user(message):  # ответ пользователю
    # если введено число, выполняеться фильтрация по цене
    try:
        for i in fp_parser.get_orders_by_filter(
            float(message.text), server_code=cfg.server_id
        ):
            message_to_bot = f"Сервер: {i[0]} \nКоличество серебра: {i[1]} \nЦена за 1кк: {i[2]} \nСсылка на лот: {i[3]}"
            bot.send_message(message.chat.id, message_to_bot)

    except:  # обработка исключения
        bot.send_message(message.chat.id, text="Введите число")


def return_message(server_name, avg_price, usd_rub, eur_rub):
    message_with_price = f"""
                   Сервер: {server_name}!
               *************
               *       Рубли      *
               *************
               Средняя цена с комиссией FunPay: {format(avg_price, '0.2f')} ₽
               Примерная средняя цена без комиссии FunPay: {format(avg_price * 0.825, '0.2f')} ₽
               *************
               *        USD         *
               *************
               Средняя цена с комиссией FunPay: {format(avg_price / usd_rub, '0.2f')} $
               Примерная средняя цена без комиссии FunPay: {format((avg_price / usd_rub) * 0.825, '0.2f')} $
               *************
               *        EUR         *
               *************
               Средняя цена с комиссией FunPay: {format(avg_price / eur_rub, '0.2f')} €
               Примерная средняя цена без комиссии FunPay: {format((avg_price / eur_rub) * 0.825, '0.2f')} €
           """
    return message_with_price


if __name__ == "__main__":
    try:
        logger.add(
            "out.log", backtrace=True, diagnose=True, retention="1 week"
        )  # Caution, may leak sensitive data in prod
        logger.info("Бот начал работу")
        bot.polling(none_stop=True)

    except Exception as error:
        logger.error(error)
