import requests
from PIL import Image, ImageDraw, ImageFont
import json
from datetime import datetime, timedelta
import db
import os

url = os.getenv("URL")
main_data = os.getenv("MAIN_DATA")

# Function to get managers from main data
def get_managers():
    # Implement fetching managers from main data
    response = requests.get(main_data)
    if response.status_code == 200:
        main_data = response.json()
        return main_data.get('managers', [])
    else:
        return []
    
managers = get_managers()

# Function to send Telegram message
def send_telegram_message(chat_id, message, token):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# Function to send Telegram photo
def send_telegram_photo(chat_id, photo, token):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    data = {"chat_id": chat_id}
    files = {"photo": photo}
    response = requests.post(url, data=data, files=files)
    return response

# Function to get orders within promo duration
def get_orders(start_time, end_time):
    orders = db.get_all_orders()  # Assuming db.get_all_orders() fetches all orders
    reform_orders = []
    for order in orders:
        if order.get('is_promo', False) and order.get('payment_status', '') == 'Pending':
            order_time = datetime.strptime(order.get('order_date', ''), '%Y-%m-%d %H:%M:%S')  # Assuming order_date field exists
            if start_time <= order_time <= end_time:
                reform_orders.append(order)
    return reform_orders


# Function to generate progress report
def generate_report(orders):
    # from these orders, create new orders (orders_new) where one item contains the orders with same order['photo_url'] as item['photo_url'], order['item_name'] as item['item_name'], the count of these orders as item['count'], sum of order['price_etb'] as item['total_amount'],
	# data to be displayed for each item in orders_new: item['item_name'], item['photo_url'], item['total_amount'], and item['count']
    item_dict = {}
    # Group orders by photo_url and item_name
    for order in orders:
        key = (order['photo_url'], order['item_name'])
        if key not in item_dict:
            item_dict[key] = {'count': 0, 'total_amount': 0}
        item_dict[key]['count'] += 1
        item_dict[key]['total_amount'] += order['price_etb']  # Assuming 'price_etb' contains the price for each item

    # Create a list of items from the aggregated values
    report_items = []
    for key, values in item_dict.items():
        photo_url, item_name = key
        total_amount = values['total_amount']
        count = values['count']
        report_items.append({'item_name': item_name, 'photo_url': photo_url, 'total_amount': total_amount, 'count': count})

    return report_items

def generate_report_image(report_items):
    # Set image dimensions and font properties
    image_width = 600
    image_height = 800
    font_size = 20
    font = ImageFont.truetype("arial.ttf", font_size)
    padding = 20

    # Create a blank image with white background
    image = Image.new("RGB", (image_width, image_height), "white")
    draw = ImageDraw.Draw(image)

    # Set initial y-coordinate for drawing
    y = padding

    # Write header
    header_text = "Progress Report"
    header_text_width, header_text_height = draw.textsize(header_text, font=font)
    draw.text(((image_width - header_text_width) / 2, y), header_text, fill="black", font=font)
    y += header_text_height + padding

    # Write report items
    for item in report_items:
        # Fetch photo from URL
        photo_response = requests.get(item['photo_url'])
        if photo_response.status_code == 200:
            photo = Image.open(BytesIO(photo_response.content))
            # Resize photo to fit image width
            photo = photo.resize((image_width - 2 * padding, 200))
            image.paste(photo, (padding, y))
            y += 200 + padding

        item_text = f"{item['item_name']}: {item['count']} orders, Total amount: {item['total_amount']}"
        draw.text((padding, y), item_text, fill="black", font=font)
        y += font_size + padding

    # Save the image
    image_path = "progress_report.png"
    image.save(image_path)

    return image_path


def saveFile(directory, file_name, data):
    files = {'file': json.dumps(data)}
    data_ = {'filename': file_name, 'directory': directory}
    response = requests.post(f'{url}/save_file', files=files, data=data_)
    if response.status_code == 200:
        print("Data sent successfully.")
    else:
        print("Failed to send data:", response.text)

