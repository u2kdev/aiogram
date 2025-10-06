# main.py
import json
import datetime
import base64
import asyncio
import pandas as pd

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, FSInputFile
)
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, ADMIN_IDS

# --------- Файлы -------------
USERS_FILE = "data.json"
VACANCIES_FILE = "vacancies.json"
ADMIN_LOG = "admin_log.txt"
APPS_LOG = "applications_log.txt"
USERS_XLSX = "users.xlsx"
MENU_PHOTO = "photo.jpg"

# --------- Бот и dispatcher -------------
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# --------- FSM States -------------
class Form(StatesGroup):
    add_country = State()
    add_job_name = State()
    add_job_desc = State()


# --------- Утилиты: base64 для callback-safe строк -------------
def enc(s: str) -> str:
    """Кодирование строки в base64 для использования в callback_data"""
    return base64.urlsafe_b64encode(s.encode()).decode()


def dec(s: str) -> str:
    """Декодирование строки из base64"""
    return base64.urlsafe_b64decode(s.encode()).decode()


# --------- Работа с файлами JSON -------------
def load_json_file(path: str, default):
    """Безопасная загрузка JSON с созданием файла при ошибке"""
    try:
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                raise ValueError("empty")
            return json.loads(txt)
    except (FileNotFoundError, ValueError, json.JSONDecodeError):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default


def save_json_file(path: str, obj):
    """Сохранение данных в JSON"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)


# --------- Users (data.json) -------------
def load_users():
    return load_json_file(USERS_FILE, {"users": []})


def save_users(obj):
    save_json_file(USERS_FILE, obj)


# --------- Vacancies (vacancies.json) -------------
def load_vacancies():
    return load_json_file(VACANCIES_FILE, {"countries": {}})


def save_vacancies(obj):
    save_json_file(VACANCIES_FILE, obj)


# --------- Логирование -------------
def log_admin(text: str):
    """Лог действий администратора"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(ADMIN_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")


def log_app(text: str):
    """Лог откликов пользователей"""
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(APPS_LOG, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] {text}\n")


# --------- Утилиты интерфейса -------------
async def delete_message_if_exists(chat_id: int, message_id: int):
    """Безопасное удаление сообщения"""
    try:
        await bot.delete_message(chat_id, message_id)
    except:
        pass


async def clear_menu_messages(message: Message, look_back: int = 6):
    """Удаление диапазона предыдущих сообщений"""
    for i in range(look_back):
        mid = message.message_id - i
        try:
            await bot.delete_message(message.chat.id, mid)
        except:
            pass


# --------- Главное меню -------------
async def show_main_menu(chat_id: int):
    """Отображение главного меню с фото"""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Вакансии", callback_data="A_vacancies")],
        [InlineKeyboardButton(text="ℹ️ О нас", callback_data="about")]
    ])
    try:
        photo = FSInputFile(MENU_PHOTO)
        await bot.send_photo(chat_id=chat_id, photo=photo, caption="Главное меню:", reply_markup=kb)
    except Exception:
        await bot.send_message(chat_id=chat_id, text="Главное меню:", reply_markup=kb)


# --------- /start -------------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Команда /start - регистрация или показ меню"""
    users_obj = load_users()
    user_id = message.from_user.id
    exists = any(u["id"] == user_id for u in users_obj["users"])

    await clear_menu_messages(message)

    if exists:
        await show_main_menu(message.chat.id)
        return

    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Отправить контакт", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("👋 Привет! Отправь свой контакт для регистрации:", reply_markup=kb)


# --------- Обработка контакта -------------
@dp.message(F.contact)
async def handle_contact(message: Message):
    """Сохранение контакта пользователя"""
    users_obj = load_users()
    user_id = message.from_user.id
    already = any(u["id"] == user_id for u in users_obj["users"])

    if not already:
        users_obj["users"].append({
            "id": user_id,
            "username": message.from_user.username,
            "name": message.from_user.full_name,
            "phone": message.contact.phone_number,
            "registered_at": datetime.datetime.now().isoformat()
        })
        save_users(users_obj)
        log_admin(f"Новый пользователь: {user_id} | {message.from_user.full_name}")
        await message.answer("✅ Регистрация завершена!", reply_markup=ReplyKeyboardRemove())

    await clear_menu_messages(message)
    await show_main_menu(message.chat.id)


# --------- О нас -------------
@dp.callback_query(F.data == "about")
async def show_about(callback: CallbackQuery):
    """Информация о компании"""
    text = (
        "ℹ️ **О нас**\n\n"
        "Мы помогаем найти работу за рубежом!\n"
        "Наша команда профессионалов подберет для вас лучшие вакансии "
        "и поможет с трудоустройством.\n\n"
        "📞 Свяжитесь с нами для консультации!"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])
    await callback.message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
    await callback.answer()


# --------- Возврат в главное меню -------------
@dp.callback_query(F.data == "back_main")
async def back_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)
    await show_main_menu(callback.message.chat.id)
    await callback.answer()


# --------- Пункт A: Вакансии -------------
@dp.callback_query(F.data == "A_vacancies")
async def a_vacancies(callback: CallbackQuery):
    """Показ списка стран"""
    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)
    vac = load_vacancies()
    kb_builder = InlineKeyboardBuilder()

    for cname in vac["countries"].keys():
        kb_builder.button(text=f"🌍 {cname}", callback_data=f"B_open:{enc(cname)}")

    if callback.from_user.id in ADMIN_IDS:
        kb_builder.button(text="➕ Добавить страну", callback_data="B_add")
        if vac["countries"]:
            kb_builder.button(text="🗑 Удалить страну", callback_data="B_del")

    kb_builder.button(text="⬅️ Назад", callback_data="back_main")
    kb_builder.adjust(2)
    await callback.message.answer("📋 Вакансии — выберите страну:", reply_markup=kb_builder.as_markup())
    await callback.answer()


# --------- Добавить страну (B) -------------
@dp.callback_query(F.data == "B_add")
async def b_add_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления страны"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    await callback.message.answer("Введите название новой страны:")
    await state.set_state(Form.add_country)
    await callback.answer()


@dp.message(Form.add_country)
async def b_add_name(message: Message, state: FSMContext):
    """Сохранение новой страны"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Доступно только админам.")
        await state.clear()
        return

    name = message.text.strip()
    vac = load_vacancies()

    if name in vac["countries"]:
        await message.answer("⚠️ Такая страна уже существует.")
        await state.clear()
        return

    vac["countries"][name] = {"jobs": {}}
    save_vacancies(vac)
    log_admin(f"Admin {message.from_user.id} добавил страну: {name}")

    await message.answer(f"✅ Страна '{name}' добавлена.")
    await state.clear()

    # Возврат в меню вакансий
    await delete_message_if_exists(message.chat.id, message.message_id)
    await delete_message_if_exists(message.chat.id, message.message_id - 1)

    kb_builder = InlineKeyboardBuilder()
    for cname in vac["countries"].keys():
        kb_builder.button(text=f"🌍 {cname}", callback_data=f"B_open:{enc(cname)}")
    if message.from_user.id in ADMIN_IDS:
        kb_builder.button(text="➕ Добавить страну", callback_data="B_add")
        kb_builder.button(text="🗑 Удалить страну", callback_data="B_del")
    kb_builder.button(text="⬅️ Назад", callback_data="back_main")
    kb_builder.adjust(2)
    await message.answer("📋 Вакансии — выберите страну:", reply_markup=kb_builder.as_markup())


# --------- Удалить страну (B) -------------
@dp.callback_query(F.data == "B_del")
async def b_del_start(callback: CallbackQuery):
    """Выбор страны для удаления"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    vac = load_vacancies()
    kb = InlineKeyboardBuilder()

    for cname in vac["countries"].keys():
        kb.button(text=f"🗑 {cname}", callback_data=f"B_delete:{enc(cname)}")

    kb.button(text="❌ Отмена", callback_data="A_vacancies")
    kb.adjust(2)
    await callback.message.edit_text("Выберите страну для удаления:", reply_markup=kb.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("B_delete:"))
async def b_delete(callback: CallbackQuery):
    """Подтверждение удаления страны"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    enc_name = callback.data.split(":", 1)[1]
    name = dec(enc_name)
    vac = load_vacancies()

    if name in vac["countries"]:
        del vac["countries"][name]
        save_vacancies(vac)
        log_admin(f"Admin {callback.from_user.id} удалил страну: {name}")
        await callback.answer(f"🗑 Страна '{name}' удалена.", show_alert=True)

    # Возврат в меню вакансий
    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)

    kb_builder = InlineKeyboardBuilder()
    for cname in vac["countries"].keys():
        kb_builder.button(text=f"🌍 {cname}", callback_data=f"B_open:{enc(cname)}")
    if callback.from_user.id in ADMIN_IDS:
        kb_builder.button(text="➕ Добавить страну", callback_data="B_add")
        if vac["countries"]:
            kb_builder.button(text="🗑 Удалить страну", callback_data="B_del")
    kb_builder.button(text="⬅️ Назад", callback_data="back_main")
    kb_builder.adjust(2)
    await callback.message.answer("📋 Вакансии — выберите страну:", reply_markup=kb_builder.as_markup())


# --------- Открыть страну (B -> показать C) -------------
@dp.callback_query(F.data.startswith("B_open:"))
async def b_open(callback: CallbackQuery):
    """Показ вакансий в стране"""
    enc_name = callback.data.split(":", 1)[1]
    name = dec(enc_name)
    vac = load_vacancies()

    if name not in vac["countries"]:
        await callback.answer("⚠️ Страна не найдена.", show_alert=True)
        return

    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)

    kb = InlineKeyboardBuilder()
    jobs = vac["countries"][name]["jobs"]

    for j in jobs.keys():
        kb.button(text=f"💼 {j}", callback_data=f"C_open:{enc(name)}:{enc(j)}")

    if callback.from_user.id in ADMIN_IDS:
        kb.button(text="➕ Добавить вакансию", callback_data=f"C_add:{enc(name)}")
        if jobs:
            kb.button(text="🗑 Удалить вакансию", callback_data=f"C_del:{enc(name)}")

    kb.button(text="⬅️ Назад", callback_data="A_vacancies")
    kb.adjust(2)
    await callback.message.answer(f"🌍 {name} — вакансии:", reply_markup=kb.as_markup())
    await callback.answer()


# --------- Добавить вакансию (C) -------------
@dp.callback_query(F.data.startswith("C_add:"))
async def c_add_start(callback: CallbackQuery, state: FSMContext):
    """Начало добавления вакансии"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    enc_name = callback.data.split(":", 1)[1]
    country = dec(enc_name)
    await state.update_data(country=country)
    await state.set_state(Form.add_job_name)
    await callback.message.answer(f"Введите название вакансии для страны '{country}':")
    await callback.answer()


@dp.message(Form.add_job_name)
async def c_add_name(message: Message, state: FSMContext):
    """Ввод названия вакансии"""
    data_state = await state.get_data()
    country = data_state.get("country")

    if not country or message.from_user.id not in ADMIN_IDS:
        await message.answer("⚠️ Ошибка — повторите попытку.")
        await state.clear()
        return

    job_name = message.text.strip()
    vac = load_vacancies()

    if job_name in vac["countries"].get(country, {}).get("jobs", {}):
        await message.answer("⚠️ Такая вакансия уже существует.")
        await state.clear()
        return

    await state.update_data(job=job_name)
    await state.set_state(Form.add_job_desc)
    await message.answer(f"Теперь введите описание вакансии '{job_name}':")


@dp.message(Form.add_job_desc)
async def c_add_desc(message: Message, state: FSMContext):
    """Сохранение описания вакансии"""
    data_state = await state.get_data()
    country = data_state.get("country")
    job_name = data_state.get("job")
    user_id = message.from_user.id

    if not country or not job_name or user_id not in ADMIN_IDS:
        await message.answer("⚠️ Ошибка — повторите попытку.")
        await state.clear()
        return

    vac = load_vacancies()
    if country not in vac["countries"]:
        vac["countries"][country] = {"jobs": {}}

    vac["countries"][country]["jobs"][job_name] = {
        "description": message.text.strip(),
        "created_by": user_id,
        "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_vacancies(vac)
    log_admin(f"Admin {user_id} добавил вакансию '{job_name}' в {country}")

    await message.answer(f"✅ Вакансия '{job_name}' в '{country}' добавлена.")
    await state.clear()

    # Возврат в меню страны
    await delete_message_if_exists(message.chat.id, message.message_id)
    await delete_message_if_exists(message.chat.id, message.message_id - 1)
    await delete_message_if_exists(message.chat.id, message.message_id - 2)

    kb = InlineKeyboardBuilder()
    jobs = vac["countries"][country]["jobs"]
    for j in jobs.keys():
        kb.button(text=f"💼 {j}", callback_data=f"C_open:{enc(country)}:{enc(j)}")
    if user_id in ADMIN_IDS:
        kb.button(text="➕ Добавить вакансию", callback_data=f"C_add:{enc(country)}")
        kb.button(text="🗑 Удалить вакансию", callback_data=f"C_del:{enc(country)}")
    kb.button(text="⬅️ Назад", callback_data="A_vacancies")
    kb.adjust(2)
    await message.answer(f"🌍 {country} — вакансии:", reply_markup=kb.as_markup())


# --------- Удалить вакансию (C) -------------
@dp.callback_query(F.data.startswith("C_del:"))
async def c_del_start(callback: CallbackQuery):
    """Выбор вакансии для удаления"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    enc_name = callback.data.split(":", 1)[1]
    country = dec(enc_name)
    vac = load_vacancies()
    jobs = vac["countries"].get(country, {}).get("jobs", {})

    kb = InlineKeyboardBuilder()
    for j in jobs.keys():
        kb.button(text=f"🗑 {j}", callback_data=f"C_delete:{enc_name}:{enc(j)}")

    kb.button(text="❌ Отмена", callback_data=f"B_open:{enc_name}")
    kb.adjust(2)
    await callback.message.edit_text("Выберите вакансию для удаления:", reply_markup=kb.as_markup())
    await callback.answer()


@dp.callback_query(F.data.startswith("C_delete:"))
async def c_delete(callback: CallbackQuery):
    """Подтверждение удаления вакансии"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("⛔️ Доступно только админам.", show_alert=True)
        return

    parts = callback.data.split(":")
    enc_country = parts[1]
    enc_job = parts[2]
    country = dec(enc_country)
    job = dec(enc_job)
    vac = load_vacancies()

    if job in vac["countries"].get(country, {}).get("jobs", {}):
        del vac["countries"][country]["jobs"][job]
        save_vacancies(vac)
        log_admin(f"Admin {callback.from_user.id} удалил вакансию '{job}' ({country})")
        await callback.answer(f"🗑 Вакансия '{job}' удалена.", show_alert=True)

    # Возврат в меню страны
    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)

    kb = InlineKeyboardBuilder()
    jobs = vac["countries"][country]["jobs"]
    for j in jobs.keys():
        kb.button(text=f"💼 {j}", callback_data=f"C_open:{enc(country)}:{enc(j)}")
    if callback.from_user.id in ADMIN_IDS:
        kb.button(text="➕ Добавить вакансию", callback_data=f"C_add:{enc(country)}")
        if jobs:
            kb.button(text="🗑 Удалить вакансию", callback_data=f"C_del:{enc(country)}")
    kb.button(text="⬅️ Назад", callback_data="A_vacancies")
    kb.adjust(2)
    await callback.message.answer(f"🌍 {country} — вакансии:", reply_markup=kb.as_markup())


# --------- Открыть вакансию (C -> показать D) -------------
@dp.callback_query(F.data.startswith("C_open:"))
async def c_open(callback: CallbackQuery):
    """Показ описания вакансии"""
    parts = callback.data.split(":")
    enc_country = parts[1]
    enc_job = parts[2]
    country = dec(enc_country)
    job = dec(enc_job)
    vac = load_vacancies()
    job_obj = vac["countries"].get(country, {}).get("jobs", {}).get(job, {})
    desc = job_obj.get("description", "Описание отсутствует.")

    await delete_message_if_exists(callback.message.chat.id, callback.message.message_id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Откликнуться", callback_data=f"apply:{enc_country}:{enc_job}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"B_open:{enc_country}")]
    ])
    await callback.message.answer(
        f"<b>💼 {job}</b>\n🌍 {country}\n\n{desc}",
        reply_markup=kb,
        parse_mode="HTML"
    )
    await callback.answer()


# --------- Отклик на вакансию -------------
@dp.callback_query(F.data.startswith("apply:"))
async def apply_job(callback: CallbackQuery):
    """Обработка отклика на вакансию"""
    parts = callback.data.split(":")
    enc_country = parts[1]
    enc_job = parts[2]
    country = dec(enc_country)
    job = dec(enc_job)
    user = callback.from_user

    # Получаем данные пользователя
    users_obj = load_users()
    user_data = next((u for u in users_obj["users"] if u["id"] == user.id), None)
    phone = user_data.get("phone", "Не указан") if user_data else "Не указан"

    text_for_admin = (
        f"📢 Новый отклик!\n\n"
        f"👤 {user.full_name}\n"
        f"🆔 {user.id}\n"
        f"@{user.username or 'нет username'}\n"
        f"📞 {phone}\n\n"
        f"🌍 Страна: {country}\n"
        f"💼 Вакансия: {job}"
    )

    # Отправляем всем админам
    for aid in ADMIN_IDS:
        try:
            await bot.send_message(aid, text_for_admin)
        except Exception as e:
            log_admin(f"Ошибка отправки отклика админу {aid}: {e}")

    # Логируем отклик
    log_app(f"User {user.id} ({user.full_name}) откликнулся на '{job}' ({country})")

    await callback.answer("✅ Ваша заявка отправлена администраторам!", show_alert=True)


# --------- Админские команды -------------
@dp.message(Command("data"))
async def cmd_data(message: Message):
    """Выгрузка данных пользователей в Excel"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Команда только для админов.")
        return

    users_obj = load_users()

    if not users_obj["users"]:
        await message.answer("⚠️ Нет зарегистрированных пользователей.")
        return

    try:
        df = pd.DataFrame(users_obj["users"])
        df.to_excel(USERS_XLSX, index=False, engine='openpyxl')
        await message.answer_document(
            FSInputFile(USERS_XLSX),
            caption=f"📊 Список пользователей\nВсего: {len(users_obj['users'])}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка создания файла: {e}")


@dp.message(Command("log"))
async def cmd_log(message: Message):
    """Отправка лога админских действий"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Команда только для админов.")
        return

    try:
        await message.answer_document(
            FSInputFile(ADMIN_LOG),
            caption="📄 Лог действий администраторов"
        )
    except FileNotFoundError:
        await message.answer("⚠️ Файл логов ещё не создан.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("applog"))
async def cmd_applog(message: Message):
    """Отправка лога откликов пользователей"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Команда только для админов.")
        return

    try:
        await message.answer_document(
            FSInputFile(APPS_LOG),
            caption="📄 Лог откликов на вакансии"
        )
    except FileNotFoundError:
        await message.answer("⚠️ Файл логов откликов ещё не создан.")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    """Статистика бота (дополнительная команда)"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("⛔️ Команда только для админов.")
        return

    users_obj = load_users()
    vac = load_vacancies()

    total_users = len(users_obj["users"])
    total_countries = len(vac["countries"])
    total_jobs = sum(len(country["jobs"]) for country in vac["countries"].values())

    text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"🌍 Стран: {total_countries}\n"
        f"💼 Вакансий: {total_jobs}\n"
    )

    await message.answer(text, parse_mode="Markdown")


# --------- Запуск бота -------------
async def main():
    """Главная функция запуска"""
    print("🚀 Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())