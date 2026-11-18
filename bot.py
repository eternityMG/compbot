import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

import config

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

class ConfigStates(StatesGroup):
    waiting_answer = State()

# ===== ДАННЫЕ СБОРОК =====
BUILDS = {
    "gaming": {"name": "🎮 Игровой ПК", "url": "http://localhost:8080/product/gaming"},
    "work": {"name": "💼 Рабочая станция", "url": "http://localhost:8080/product/work"},
    "study": {"name": "📚 Учебный ПК", "url": "http://localhost:8080/product/study"},
    "design": {"name": "🎨 Для дизайна", "url": "http://localhost:8080/product/design"},
    "programming": {"name": "💻 Для программирования", "url": "http://localhost:8080/product/programming"},
    "universal": {"name": "🎯 Универсальный ПК", "url": "http://localhost:8080/product/universal"},
}

# ===== ВОПРОСЫ =====
QUESTIONS = [
    {
        "text": "Для каких целей нужен компьютер?",
        "explanation": "От этого зависит вся сборка! Для игр нужна мощная видеокарта, для работы — быстрый процессор.",
        "options": [
            ("🎮 Для игр", "gaming"),
            ("💼 Для работы", "work"),
            ("📚 Для учебы", "study"),
            ("🎨 Для дизайна/монтажа", "design"),
            ("💻 Для программирования", "programming"),
            ("🎯 Универсальный", "universal")
        ],
        "key": "purpose",
        "display": "Цель"
    },
    {
        "text": "Какой у тебя бюджет?",
        "explanation": "Бюджет определяет, какие комплектующие мы сможем предложить.",
        "options": [
            ("💰 до 50 000 ₽", "budget_50"),
            ("💰 50-80 000 ₽", "budget_80"),
            ("💰 80-120 000 ₽", "budget_120"),
            ("💰 120-180 000 ₽", "budget_180"),
            ("💰 от 180 000 ₽", "budget_plus")
        ],
        "key": "budget",
        "display": "Бюджет"
    },
    {
        "text": "Какой процессор предпочитаешь?",
        "explanation": "Процессор — мозг компьютера. Intel Core i5 — отличный выбор для игр. Intel Core i7/i9 — для профессиональных задач.",
        "options": [
            ("Intel Core i5", "cpu_i5"),
            ("Intel Core i7/i9", "cpu_i9"),
            ("AMD Ryzen 5", "cpu_r5"),
            ("AMD Ryzen 7/9", "cpu_r9")
        ],
        "key": "cpu",
        "display": "Процессор"
    },
    {
        "text": "Какое поколение процессора предпочитаешь?",
        "explanation": "Новое поколение = выше производительность. Intel 13-14 поколения и AMD 7000 — самые современные.",
        "options": [
            ("Intel 12-е поколение", "gen_intel12"),
            ("Intel 13-е поколение", "gen_intel13"),
            ("Intel 14-е поколение", "gen_intel14"),
            ("AMD Ryzen 5000", "gen_amd5000"),
            ("AMD Ryzen 7000", "gen_amd7000")
        ],
        "key": "cpu_gen",
        "display": "Поколение CPU"
    },
    {
        "text": "Сколько ядер должно быть у процессора?",
        "explanation": "Больше ядер = быстрее многозадачность. 6 ядер — оптимально для игр. 8 ядер — для стриминга.",
        "options": [
            ("6 ядер", "cores_6"),
            ("8 ядер", "cores_8"),
            ("12+ ядер", "cores_12")
        ],
        "key": "cores",
        "display": "Количество ядер"
    },
    {
        "text": "Какую видеокарту предпочитаешь?",
        "explanation": "Видеокарта — главная для игр. NVIDIA RTX — лидер в играх. AMD Radeon — хорошее соотношение цена/качество.",
        "options": [
            ("NVIDIA RTX", "gpu_rtx"),
            ("NVIDIA Quadro", "gpu_quadro"),
            ("AMD Radeon", "gpu_radeon")
        ],
        "key": "gpu",
        "display": "Видеокарта"
    },
    {
        "text": "Какой тип видеопамяти предпочитаешь?",
        "explanation": "Тип памяти влияет на скорость видеокарты. GDDR6 — стандарт. GDDR6X — быстрее.",
        "options": [
            ("GDDR6", "mem_gddr6"),
            ("GDDR6X", "mem_gddr6x"),
            ("HBM2", "mem_hbm2")
        ],
        "key": "gpu_mem",
        "display": "Тип видеопамяти"
    },
    {
        "text": "Какой объем видеопамяти нужен?",
        "explanation": "Больше видеопамяти = лучше для игр. 8 ГБ — для Full HD. 16 ГБ — для 4K.",
        "options": [
            ("8 ГБ", "vram_8"),
            ("12 ГБ", "vram_12"),
            ("16 ГБ", "vram_16"),
            ("24+ ГБ", "vram_24")
        ],
        "key": "vram",
        "display": "Объем видеопамяти"
    },
    {
        "text": "Сколько оперативной памяти нужно?",
        "explanation": "ОЗУ влияет на скорость работы. 16 ГБ — минимум для игр. 32 ГБ — комфорт.",
        "options": [
            ("16 ГБ", "ram_16"),
            ("32 ГБ", "ram_32"),
            ("64 ГБ", "ram_64"),
            ("128 ГБ", "ram_128")
        ],
        "key": "ram",
        "display": "Объем ОЗУ"
    },
    {
        "text": "Какая частота ОЗУ предпочтительна?",
        "explanation": "Выше частота = быстрее работа. DDR4 3600 — золотая середина. DDR5 5600+ — современный стандарт.",
        "options": [
            ("DDR4 3200", "freq_3200"),
            ("DDR4 3600", "freq_3600"),
            ("DDR5 5600", "freq_5600"),
            ("DDR5 6000+", "freq_6000")
        ],
        "key": "ram_freq",
        "display": "Частота ОЗУ"
    },
    {
        "text": "Какие тайминги ОЗУ (CL) предпочитаешь?",
        "explanation": "Тайминги влияют на задержки памяти. Чем ниже CL, тем быстрее память.",
        "options": [
            ("CL22", "cl22"),
            ("CL18", "cl18"),
            ("CL16", "cl16"),
            ("CL14", "cl14")
        ],
        "key": "timings",
        "display": "Тайминги ОЗУ"
    },
    {
        "text": "Какой тип накопителя предпочитаешь?",
        "explanation": "SSD быстрее HDD в 5-10 раз. SSD — для системы и игр. HDD — для хранения файлов.",
        "options": [
            ("SSD", "storage_ssd"),
            ("SSD + HDD", "storage_mix"),
            ("HDD", "storage_hdd"),
            ("NVMe M.2", "storage_nvme")
        ],
        "key": "storage",
        "display": "Тип накопителя"
    },
    {
        "text": "Какой интерфейс накопителя предпочитаешь?",
        "explanation": "Интерфейс определяет скорость. PCIe 4.0 — лучшее соотношение цена/качество.",
        "options": [
            ("SATA III", "int_sata"),
            ("PCIe 3.0", "int_pcie3"),
            ("PCIe 4.0", "int_pcie4"),
            ("PCIe 5.0", "int_pcie5")
        ],
        "key": "interface",
        "display": "Интерфейс накопителя"
    },
    {
        "text": "Какой объем накопителя нужен?",
        "explanation": "Объем зависит от задач. 1 ТБ — минимум. 2 ТБ — комфорт.",
        "options": [
            ("512 ГБ", "size_512"),
            ("1 ТБ", "size_1tb"),
            ("2 ТБ", "size_2tb"),
            ("4+ ТБ", "size_4tb")
        ],
        "key": "size",
        "display": "Объем накопителя"
    },
    {
        "text": "Какой тип материнской платы предпочитаешь?",
        "explanation": "Чипсет определяет возможности. B660/B650 — хороший баланс. Z690/Z790 — для разгона.",
        "options": [
            ("Базовый", "mb_base"),
            ("Средний", "mb_mid"),
            ("Высокий", "mb_high"),
            ("Проф.", "mb_pro")
        ],
        "key": "motherboard",
        "display": "Тип материнской платы"
    },
    {
        "text": "Какой бренд материнской платы предпочитаешь?",
        "explanation": "Бренд влияет на качество. ASUS — премиум. MSI — хорошее соотношение.",
        "options": [
            ("ASUS", "brand_asus"),
            ("MSI", "brand_msi"),
            ("Gigabyte", "brand_gigabyte"),
            ("ASRock", "brand_asrock")
        ],
        "key": "brand",
        "display": "Бренд материнской платы"
    },
    {
        "text": "Какой форм-фактор корпуса предпочитаешь?",
        "explanation": "Форм-фактор влияет на размер ПК. ATX — стандарт. mATX — компактный.",
        "options": [
            ("ATX", "form_atx"),
            ("mATX", "form_matx"),
            ("Mini-ITX", "form_mini")
        ],
        "key": "form_factor",
        "display": "Форм-фактор"
    },
    {
        "text": "Какие дополнительные функции важны?",
        "explanation": "Дополнительные функции для удобства. Wi-Fi нужен если нет провода.",
        "options": [
            ("Wi-Fi/Bluetooth", "feat_wifi"),
            ("RGB подсветка", "feat_rgb"),
            ("Тихий ПК", "feat_silent")
        ],
        "key": "features",
        "display": "Дополнительные функции"
    },
    {
        "text": "Какую операционную систему предпочитаешь?",
        "explanation": "ОС — интерфейс для работы. Windows 11 — современный. Linux — бесплатный.",
        "options": [
            ("Windows 11", "os_win11"),
            ("Windows 10", "os_win10"),
            ("Linux", "os_linux"),
            ("Без ОС", "os_none")
        ],
        "key": "os",
        "display": "ОС"
    },
    {
        "text": "Будешь ли разгонять (оверклокинг)?",
        "explanation": "Оверклокинг — повышение частоты. Дает +10-20% производительности.",
        "options": [
            ("Да, планирую", "oc_yes"),
            ("Возможно", "oc_maybe"),
            ("Нет", "oc_no")
        ],
        "key": "overclock",
        "display": "Оверклокинг"
    }
]

# ===== КЛАВИАТУРЫ =====
def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🖥 Собрать компьютер")
    builder.button(text="ℹ️ О нас")
    builder.button(text="📞 Контакты")
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)

def make_keyboard(options):
    builder = InlineKeyboardBuilder()
    for text, callback in options:
        builder.button(text=text, callback_data=callback)
    builder.adjust(2)
    return builder.as_markup()

# ===== СТАРТ =====
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я - профессиональный консультант по сборке ПК! 🖥\n\n"
        "Ответь на *20 вопросов*, и я подберу идеальную сборку!\n\n"
        "Нажми '🖥 Собрать компьютер' чтобы начать.",
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )

@dp.message(lambda message: message.text == "🖥 Собрать компьютер")
async def start_questionnaire(message: Message, state: FSMContext):
    await state.set_state(ConfigStates.waiting_answer)
    await state.update_data(step=0, answers={})
    await show_next_question(message, state)

async def show_next_question(target, state: FSMContext):
    data = await state.get_data()
    step = data.get('step', 0)

    if step >= len(QUESTIONS):
        await show_result(target, state)
        return

    question = QUESTIONS[step]
    q_num = step + 1

    text = f"🔧 *Вопрос {q_num} из {len(QUESTIONS)}*\n\n"
    text += f"{question['text']}\n\n"
    text += f"ℹ️ {question['explanation']}\n\n"
    text += "Выбери вариант:"

    keyboard = make_keyboard(question['options'])

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
        await target.answer()
    else:
        await target.answer(text, parse_mode="Markdown", reply_markup=keyboard)

# ===== ОБРАБОТЧИК ОТВЕТОВ =====
@dp.callback_query(ConfigStates.waiting_answer)
async def handle_answer(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    step = data.get('step', 0)
    answers = data.get('answers', {})

    if step >= len(QUESTIONS):
        await show_result(call, state)
        await call.answer()
        return

    question = QUESTIONS[step]
    key = question['key']

    answers[key] = call.data
    await state.update_data(answers=answers)

    next_step = step + 1
    await state.update_data(step=next_step)

    if next_step >= len(QUESTIONS):
        await show_result(call, state)
    else:
        await show_next_question(call, state)

    await call.answer()

# ===== РЕЗУЛЬТАТ =====
async def show_result(target, state: FSMContext):
    data = await state.get_data()
    answers = data.get('answers', {})

    purpose = answers.get('purpose', 'universal')
    build = BUILDS.get(purpose, BUILDS['universal'])

    result = "🎉 *РЕЗУЛЬТАТ ПОДБОРА*\n\n"
    result += "📊 *Твой выбор:*\n\n"

    for question in QUESTIONS:
        key = question['key']
        value = answers.get(key)
        if value:
            display_name = question['display']
            result += f"• *{display_name}:* {value}\n"

    result += f"\n⭐ *Рекомендуемая сборка:*\n"
    result += f"✅ {build['name']}\n\n"
    result += f"🔗 [👉 Перейти к товару 👈]({build['url']})"

    # Убираем кнопку с ссылкой, оставляем только "Пройти заново"
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Пройти заново", callback_data="new_build")
    builder.adjust(1)

    if isinstance(target, CallbackQuery):
        await target.message.edit_text(
            result,
            parse_mode="Markdown",
            reply_markup=builder.as_markup()
        )
    else:
        await target.answer(
            result,
            parse_mode="Markdown",
            reply_markup=builder.as_markup()
        )

    await state.clear()

@dp.callback_query(lambda c: c.data == "new_build")
async def new_build(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await start_questionnaire(call.message, state)
    await call.answer()

# ===== О НАС =====
@dp.message(lambda message: message.text == "ℹ️ О нас")
async def about_us(message: Message):
    await message.answer(
        "🖥 *О нашем магазине*\n\n"
        "Мы собираем компьютеры с 2015 года.\n"
        "✅ Только оригинальные комплектующие\n"
        "✅ Профессиональная сборка\n"
        "✅ Гарантия на все товары",
        parse_mode="Markdown"
    )

@dp.message(lambda message: message.text == "📞 Контакты")
async def contacts(message: Message):
    await message.answer(
        "📞 *Контакты*\n\n"
        "📱 +7 (999) 123-45-67\n"
        "📧 shop@example.com\n"
        "🕒 Пн-Пт: 10:00 - 20:00",
        parse_mode="Markdown"
    )

@dp.message()
async def unknown(message: Message):
    await message.answer(
        "Пожалуйста, используй кнопки меню.",
        reply_markup=get_main_keyboard()
    )

async def main():
    bot = Bot(token=config.BOT_TOKEN)
    print("🤖 Бот-консультант запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main()