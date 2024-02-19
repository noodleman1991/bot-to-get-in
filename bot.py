import logging
import sys
from datetime import datetime

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import os
from dotenv import load_dotenv

from sheets import e_worksheet

# Load environment variables
load_dotenv()

# Webserver settings
WEB_SERVER_HOST = "127.0.0.1"
WEB_SERVER_PORT = 8000
WEBHOOK_PATH = "/"
BASE_WEBHOOK_URL = "https://bf1c-2a02-14f-174-97f4-7d90-d96e-69d3-3c89.ngrok-free.app"

# Define states for form completion
class Form(StatesGroup):
    eventName = State()
    participants = State()

# Initialize the router for message handling
router = Router()

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.eventName)
    global last_col
    last_col = len(e_worksheet.row_values(1))
    await message.answer(f"היי {message.from_user.first_name}, הזנ/י שם לאירוע חדש")

@router.message(Form.eventName)
async def process_event_name(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.participants)
    eventName = message.text
    global last_col
    e_worksheet.add_cols(1)
    now = datetime.now()
    e_worksheet.update_cell(1, last_col + 1, eventName)
    e_worksheet.update_cell(2, last_col + 1, now.strftime("%d-%m-%Y"))
    await message.answer("אירוע נוסף בהצלחה!")
    await message.answer("שלח/י שמות משתתפים, ניתן לשלוח שמות מופרדים בפסיק או בהודעות נפרדות. שלחו ״הביתה״ כדי לסיים את ההרשמה לאירוע")

@router.message(Form.participants)
async def process_participants_names(message: Message, state: FSMContext) -> None:
    names = message.text
    if 'הביתה' in names:
        await state.clear()
        await message.answer("הזנת שמות משתתפים נגמרה")
    elif ',' in names:
        inputs = names.split(',')
        start_row = len(e_worksheet.col_values(last_col + 1)) + 1
        for index, item in enumerate(inputs, start=start_row):
            e_worksheet.update_cell(index, last_col + 1, item.strip())
        await message.answer("השמות הוזנו בהצלחה")
    else:
        available_row = len(e_worksheet.col_values(last_col + 1)) + 1
        e_worksheet.update_cell(available_row, last_col + 1, names.strip())
        await message.answer("השם הוזן")

async def on_startup(bot: Bot) -> None:
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")

def main() -> None:
    bot = Bot(os.getenv('TOKEN'), parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(router)
    dp.startup.register(on_startup)
    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    main()
