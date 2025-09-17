import os
import json
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ================== Настройки ==================
API_TOKEN = os.getenv("API_TOKEN")
if not API_TOKEN:
    print("❌ Помилка: не вказано API_TOKEN у Render → Environment")
    exit(1)

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

# Создаём бота
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher()


# ================== FSM ==================
class LinkStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_confirm = State()


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
async def new_link(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    if len(args) > 1:
        await ask_confirmation(message, state, args[1])
    else:
        await message.answer("✍️ Введи название для лінків:")
        await state.set_state(LinkStates.waiting_for_name)


@dp.message(LinkStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    link_name = message.text.strip()
    await ask_confirmation(message, state, link_name)


async def ask_confirmation(message: Message, state: FSMContext, link_name: str):
    """Отправляет запрос на подтверждение"""
    await state.update_data(link_name=link_name)

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Створити", callback_data="confirm_yes")
    kb.button(text="❌ Скасувати", callback_data="confirm_no")
    kb.adjust(2)

    await message.answer(
        f"Ти ввів назву: <b>{link_name}</b>\nПідтвердити створення лінків?",
        reply_markup=kb.as_markup()
    )
    await state.set_state(LinkStates.waiting_for_confirm)


@dp.callback_query(LinkStates.waiting_for_confirm, F.data == "confirm_yes")
async def confirm_yes(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    link_name = data.get("link_name", "Без назви")

    await generate_links(callback.message, link_name)
    await state.clear()
    await callback.answer("✅ Лінки створені")


@dp.callback_query(LinkStates.waiting_for_confirm, F.data == "confirm_no")
async def confirm_no(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Створення лінків скасовано")
    await callback.answer("Скасовано")


async def generate_links(message: Message, link_name: str):
    """Генерация ссылок"""
    created_links = []
    for ch in CHANNELS:
        try:
            invite = await bot.create_chat_invite_link(
                chat_id=ch["id"],
                name=link_name,
                creates_join_request=True
            )
            created_links.append({"name": ch["name"], "url": invite.invite_link})
        except Exception as e:
            created_links.append({"name": ch["name"], "url": f"❌ {e}"})

    save_links(created_links)

    text = f"🔗 Постійні закриті лінки із заявкою <b>{link_name}</b>:\n\n"
    lines = []
    for i in range(0, len(created_links), 3):
        group = created_links[i:i+3]
        line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
        lines.append(line)
    text += "\n".join(lines)
    await message.answer(text)


@dp.message(Command("alllinks"))
async def all_links(message: Message):
    saved = load_links()
    if not saved:
        await message.answer("ℹ️ Лінків ще немає")
        return

    text = "📂 Усі збережені лінки:\n\n"
    lines = []
    for i in range(0, len(saved), 3):
        group = saved[i:i+3]
        line = " | ".join([f"{item['name']} - {item['url']}" for item in group])
        lines.append(line)
    text += "\n".join(lines)
    await message.answer(text)


# ================== Запуск ==================
async def main():
    print("✅ Бот запущено через polling")
    await bot.delete_webhook(drop_pending_updates=True)  # Убираем webhook
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
