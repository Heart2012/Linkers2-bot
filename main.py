import os
import json
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

# ================== Настройки ==================
API_TOKEN = os.getenv("API_TOKEN")
ADMINS = [int(os.getenv("ADMIN_ID", 0))]           # ID админов
OUTPUT_CHANNEL_ID = int(os.getenv("OUTPUT_CHANNEL_ID", 0))  # Канал для публикации

if not API_TOKEN or not OUTPUT_CHANNEL_ID:
    print("❌ Установите API_TOKEN и OUTPUT_CHANNEL_ID в Render → Environment")
    exit(1)

# ================== Список каналов ==================
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

LINKS_FILE = "links.json"

# ================== Создаём бота ==================
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# ================== Работа с JSON ==================
def load_links():
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_links(links):
    with open(LINKS_FILE, "w", encoding="utf-8") as f:
        json.dump(links, f, ensure_ascii=False, indent=2)

# ================== Хендлеры ==================
@dp.message(Command("newlink"))
async def new_link(message: Message):
    """Создаёт постоянные закрытые ссылки с заявкой"""
    if message.from_user.id not in ADMINS:
        await message.answer("❌ У вас нет прав для создания ссылок")
        return

    link_name = f"Заявка від {message.from_user.full_name}"
    created_links = []

    for ch in CHANNELS:
        try:
            invite = await bot.create_chat_invite_link(
                chat_id=ch["id"],
                name=link_name,
                creates_join_request=True   # ❗️ Закрытая ссылка с заявкой
            )
            created_links.append({"name": ch["name"], "url": invite.invite_link})
        except Exception as e:
            created_links.append({"name": ch["name"], "url": f"❌ {e}"})

    save_links(created_links)

    # Формируем сообщение для администратора
    text = "🔗 Постійні закриті лінки із заявкою:\n\n"
    text += "\n".join([f"{item['name']} → {item['url']}" for item in created_links])
    await message.answer(text)

    # Публикуем в общий канал
    await bot.send_message(OUTPUT_CHANNEL_ID, text)


@dp.message(Command("alllinks"))
async def all_links(message: Message):
    """Показывает все сохранённые ссылки"""
    saved = load_links()
    if not saved:
        await message.answer("ℹ️ Лінків ще немає")
        return

    text = "📂 Усі збережені лінки:\n\n"
    text += "\n".join([f"{item['name']} → {item['url']}" for item in saved])
    await message.answer(text)

# ================== Запуск ==================
async def main():
    # ❗️ Удаляем webhook, чтобы polling заработал
    await bot.delete_webhook(drop_pending_updates=True)
    print("✅ Webhook видалено, запускаємо polling...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
