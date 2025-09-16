import os
import json
import asyncio
from aiogram import Bot, Dispatcher, types
from aiohttp import web

# -------------------- Настройки --------------------
API_TOKEN = os.getenv("API_TOKEN")          # Токен вашего бота
APP_NAME = os.getenv("APP_NAME")            # Название Render сервиса
PORT = int(os.getenv("PORT", 10000))       # Render передает порт в $PORT
ADMINS = [int(os.getenv("ADMIN_ID", 0))]   # Ваш Telegram ID
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID", 0))  # Куда отправлять ссылки

if not API_TOKEN or not APP_NAME or not OUTPUT_CHANNEL_ID:
    print("❌ Установите API_TOKEN, APP_NAME и OUTPUT_CHANNEL_ID")
    exit(1)

WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://{APP_NAME}.onrender.com{WEBHOOK_PATH}"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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
        return

    text = message.text or ""

    if text.startswith("/newlink"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            await message.answer("❌ Укажи название ссылки. Пример: /newlink Київ/обл.")
            return
        link_name = parts[1]

        created_links = []
        for ch in CHANNELS:
            try:
                invite = await bot.create_chat_invite_link(chat_id=ch["id"], name=link_name)
                created_links.append({"name": ch["name"], "url": invite.invite_link})
            except Exception as e:
                await message.answer(f"❌ Не удалось создать ссылку для {ch['name']}: {e}")

        save_links(created_links)

        output_lines = []
        for i in range(0, len(created_links), 3):
            group = created_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            output_lines.append(line)

        final_message = "\n".join(output_lines)
        await bot.send_message(OUTPUT_CHANNEL_ID, final_message)
        await message.answer("✅ Все ссылки созданы и опубликованы!")

    elif text.startswith("/alllinks"):
        saved_links = load_links()
        if not saved_links:
            await message.answer("ℹ️ Ссылок пока нет")
            return

        output_lines = []
        for i in range(0, len(saved_links), 3):
            group = saved_links[i:i+3]
            line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
            output_lines.append(line)

        await message.answer("\n".join(output_lines))

# -------------------- Webhook Handler --------------------
async def handle_webhook(request):
    data = await request.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return web.Response()

# -------------------- Запуск aiohttp --------------------
async def on_startup(app):
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(WEBHOOK_URL)
    print(f"Webhook установлен: {WEBHOOK_URL}")

async def on_shutdown(app):
    await bot.delete_webhook()
    await bot.session.close()

app = web.Application()
app.router.add_post(WEBHOOK_PATH, handle_webhook)
app.on_startup.append(on_startup)
app.on_shutdown.append(on_shutdown)

if __name__ == "__main__":
    web.run_app(app, host="0.0.0.0", port=PORT)
