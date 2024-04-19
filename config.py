from dotenv import load_dotenv
import os
load_dotenv()

ubot = os.environ.get("UBOT")
adbot = os.environ.get("ADBOT")
url = os.environ.get("URL")
main_data = os.environ.get("MAIN_DATA")