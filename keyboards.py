from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.button(text="🖥 Собрать компьютер")
    builder.button(text="📋 Мои сборки")
    builder.button(text="ℹ️ О нас")
    builder.button(text="📞 Контакты")
    builder.adjust(2, 2)
    return builder.as_markup(resize_keyboard=True)

def get_component_type_keyboard():
    builder = InlineKeyboardBuilder()
    buttons = [
        ("🖥 Процессор", "comp_cpu"),
        ("🎮 Видеокарта", "comp_gpu"),
        ("💾 Оперативная память", "comp_ram"),
        ("📦 Материнская плата", "comp_motherboard"),
        ("💽 Накопитель", "comp_storage"),
        ("⚡ Блок питания", "comp_psu"),
        ("🏭 Корпус", "comp_case"),
        ("✅ Завершить сборку", "finish_config")
    ]
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    builder.adjust(2)
    return builder.as_markup()

def get_component_action_keyboard(component_id):
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Выбрать", callback_data=f"select_{component_id}")
    builder.button(text="🔙 Назад", callback_data="back_to_list")
    builder.adjust(2)
    return builder.as_markup()