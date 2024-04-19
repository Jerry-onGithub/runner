import requests
import threading
from datetime import datetime, timedelta
import time
import config
import db
import helper as h
import os
import json


u_token = config.ubot
ad_token = config.adbot

promo_items = config.url
search_list = config.main_data


# Function to check and notify subscribed users about promo start
def notify_subscribed_users():
    subscribed_users = db.promo_subscribed_user()
    promoItems = requests.get(promo_items)
    for item in promoItems:
        starting_time = datetime.strptime(item['additional']['Starting Date'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() <= starting_time <= datetime.now() + timedelta(hours=6):
            for user in subscribed_users:
                # send_telegram_message(user['chatid'], "Promo has started for item: {}".format(item['name']), u_token)
                # Set timer to send message to users at the starting time of each item
                t = threading.Timer((starting_time - datetime.now()).total_seconds(), h.send_telegram_message, (user['chatid'], "Promo has started for item: {}".format(item['name']), u_token))
                t.start()

# Function to notify managers when promo items begin and set timers
def notify_managers_and_set_timers():
    promoItems = requests.get(promo_items)
    for item in promoItems:
        starting_time = datetime.strptime(item['additional']['Starting Date'], '%Y-%m-%d %H:%M:%S')
        if datetime.now() <= starting_time <= datetime.now() + timedelta(hours=6):
            for manager in h.managers:
                h.send_telegram_message(manager, "Promo item '{}' has started!".format(item['name']), ad_token)
                # Set timer for sending progress report to admins every x hours within promo duration
                duration_hours = int(item['additional']['Duration'].split()[0])  # Extracting hours from duration
                progress_report_timer = threading.Timer((starting_time + timedelta(hours=duration_hours) - datetime.now()).total_seconds() / 3, send_progress_report_to_admins)
                progress_report_timer.start()

                # Set timer for executing function #4 every (item['additional']['Duration'] / 3) times
                report_count = 0
                if 'hours' in item['additional']['Duration']:
                    report_count = duration_hours // 3
                elif 'days' in item['additional']['Duration']:
                    report_count = (duration_hours * 24) // 3
                for i in range(report_count):
                    progress_report_timer = threading.Timer((starting_time + timedelta(hours=duration_hours) - datetime.now()).total_seconds() / 3, send_progress_report_to_admins)
                    progress_report_timer.start()

# Function to send final report to admins when promo ends
def send_final_report_to_admins():
    promoItems = requests.get(promo_items)
    for item in promoItems:
        starting_time = datetime.strptime(item['additional']['Starting Date'], '%Y-%m-%d %H:%M:%S')
        duration = int(item['additional']['Duration'].split()[0])  # Extracting duration value
        end_time = starting_time + timedelta(hours=duration)
        if datetime.now() >= end_time:
            orders = h.get_orders(starting_time, end_time)
            final_report = h.generate_report(orders)
            keyboard=json.dumps({ "inline_keyboard": [ [ {"text": 'Approve', "callback_data": f'decision_promo_{item['Id']}_yes'} ], [ {"text": 'Cancel', "callback_data": f'decision_promo_{item['Id']}_no'} ] ] })
            for manager in h.managers:
                h.send_telegram_photo(manager, final_report, ad_token, keyboard, 'Final Report - Promo Ended')

# Function to send progress report to admins every x hours within a promo duration
def send_progress_report_to_admins():
    promoItems = requests.get(promo_items)
    for item in promoItems:
        starting_time = datetime.strptime(item['additional']['Starting Date'], '%Y-%m-%d %H:%M:%S')
        duration = int(item['additional']['Duration'].split()[0])  # Extracting duration value
        end_time = starting_time + timedelta(hours=duration)
        if datetime.now() <= end_time:
            orders = h.get_orders(starting_time, datetime.now())
            progress_report = h.generate_report(orders)
            #generate an image for progress_report containing report_items
            for manager in h.managers:
                h.send_telegram_photo(manager, progress_report, ad_token, image_caption='Promo Progress Report')

# Function to reset promo items every 24 hours
def reset_promo_items():
    promoItems = requests.get(promo_items)
    for item in promoItems:
        starting_time = datetime.strptime(item['additional']['Starting Date'], '%Y-%m-%d %H:%M:%S')
        duration = int(item['additional']['Duration'].split()[0])  # Extracting duration value
        end_time = starting_time + timedelta(hours=duration)
        if end_time <= datetime.now():
            #remove item from promo_items
            h.saveFile('json', 'promo_items.json', promoItems)

# Function to reset search list every 24 hours
def reset_search_list():
    searchList = requests.get(search_list)
    for key in searchList:
        searchList[key] = []
    h.saveFile('json', 'search_list.json', searchList)


# Main function to run the bot
def main():
    while True:
        notify_subscribed_users()
        notify_managers_and_set_timers()
        send_final_report_to_admins()
        send_progress_report_to_admins()
        reset_promo_items()
        reset_search_list()
        # Sleep for 6 hours before checking again
        time.sleep(21600)  # 6 hours in seconds

if __name__ == "__main__":
    main()

