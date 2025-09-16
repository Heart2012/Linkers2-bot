import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")
OUTPUT_CHANNEL_ID = os.getenv("OUTPUT_CHANNEL_ID")
ADMINS = [int(os.getenv("ADMIN_ID", 0))]  # ID админов через переменные окружения

if not API_TOKEN or OUTPUT_CHANNEL_ID is None:
    print("❌ Ошибка: не заданы API_TOKEN или OUTPUT_CHANNEL_ID")
    exit(1)

OUTPUT_CHANNEL_ID = int(OUTPUT_CHANNEL_ID)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

LINKS_FILE = "links.json"

# -------------------- Список каналов --------------------
CHANNELS = [
    {"name": "Київ/обл.", "id": -1002497921892},
    {"name": "Харків/обл.", "id": -1002282062694},
    {"name": "Одеса/обл.", "id": -1002378112112},
    {"name": "Дніпро/обл.", "id": -1002469953491},
    {"name": "Львів/обл.", "id": -1002462683862},
    {"name": "Запоріжжя/обл.", "id": -1002478382347},
    {"name": "Кривий Ріг", "id": -1002479247381},
    {"name": "Миколаїв/обл.", "id": -1002263502869},
    {"name": "Вінниця/обл.", "id": -1002408714452},
    {"name": "Чернігів/обл.", "id": -1002446393799},
    {"name": "Полтава/обл.", "id": -1002175469997},
    {"name": "Хмельницький/обл.", "id": -1002429587845},
    {"name": "Черкаси/обл.", "id": -1002400669760},
    {"name": "Чернівці/обл.", "id": -1002235399302},
    {"name": "Житомир/обл.", "id": -1002330195140},
    {"name": "Суми/обл.", "id": -1002445729693},
    {"name": "Рівне/обл.", "id": -1002380253993},
    {"name": "Івано-Франківськ/обл.", "id": -1002375309618},
    {"name": "Херсон/обл.", "id": -1002418416457},
    {"name": "Ужгород/обл.", "id": -1002451310310},
    {"name": "Кременчук", "id": -1002261835375},
    {"name": "Луцьк/обл.", "id": -1002293307493},
    {"name": "Тернопіль/обл.", "id": -1002363870955},
    {"name": "Кропивницький/обл.", "id": -1002288269113},
    {"name": "⚡️ОПЕРАТИВНІ НОВИНИ УКРАЇНИ 24/7⚡️", "id": -1002666646029},
]

# -------------------- Работа с JSON --------------------
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

# -------------------- Хендлер команд --------------------
@dp.message()
async def handle_commands(message: types.Message):
    if message.from_user.id not in ADMINS:
        return  # Только админы могут использовать бота

    text = message.text or ""

    # ---------------- Показать все ссылки ----------------
    if text.startswith("/alllinks"):
        output_lines = []
        for i in range(0, len(CHANNELS), 3):
            group = CHANNELS[i:i+3]
            line = " | ".join([f"{item['name']} - https://t.me/c/{str(item['id'])[4:]}" for item in group])
            output_lines.append(line)
        await message.answer("\n".join(output_lines))

# -------------------- Запуск бота --------------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    print("Webhook удалён, запускаем polling...")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
