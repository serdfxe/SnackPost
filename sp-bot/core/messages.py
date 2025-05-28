from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


HELLO_MSG = """✨ <b>Добро пожаловать в SnackPost!</b>

Я - ваш интеллектуальный помощник для работы с текстами. Вот что я умею:

<blockquote>📚 <b>Анализировать статьи</b> - присылайте ссылки, и я сделаю краткую выжимку

✍️ <b>Адаптировать контент</b> - помогу переработать текст по вашим пожеланиям</blockquote>

Начните прямо сейчас - отправьте мне ссылку на статью с командой /summarize (или /s).

Для доступа ко всем возможностям оформите подписку в разделе /profile"""

PROFILE_MSG = """👤 <b>Ваш профиль</b>

Здесь вы можете управлять подпиской и проверять её статус."""

NO_SUBSCRIPTION_MSG = """ℹ️ <b>Информация о подписке</b>

У вас нет активной подписки.

Для доступа ко всем функциям бота оформите подписку. (свяжитесь с @p_voronin)"""

SUBSCRIPTION_INFO_MSG = """ℹ️ <b>Информация о подписке</b>

Статус: {status}
Истекает: {expires_at}"""

PAYMENT_OPTIONS_MSG = """💳 <b>Выберите вариант подписки</b>

1 месяц - X₽
3 месяца - XX₽
1 год - XXX₽"""

SUBSCRIPTION_REQUIRED_MSG = """🔒 <b>Требуется подписка</b>

Эта функция доступна только для пользователей с активной подпиской.

Оформите подписку с помощью команды /profile"""

# ===

SOURCES_MENU_MSG = """📚 <b>Управление источниками</b>

Здесь вы можете добавить новые источники или посмотреть текущие. Я буду проверять их раз в день и присылать свежие статьи по команде /digest!"""

SOURCES_MENU_BUTTONS = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="➕ Добавить источник", callback_data="add_source"),
    InlineKeyboardButton(text="🗂 Мои источники", callback_data="list_sources")],
    [InlineKeyboardButton(text="❌ Удалить источник", callback_data="delete_source"),
    InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_profile"),]]
)

ADD_SOURCE_MSG = """🔗 <b>Добавление источника</b>

Пришлите ссылку на RSS-ленту или сайт. Примеры:  
- <code>https://example.com/rss</code> (RSS)  
- <code>https://example.com/blog</code> (сайт)  

Отмена: /cancel"""

SOURCE_ADDED_MSG = """✅ <b>Источник добавлен!</b>

Теперь я буду проверять его раз в день и присылать новые статьи."""

INVALID_SOURCE_MSG = """❌ <b>Похоже этот сайт не поддерживает RSS</b>

Попробуйте с другим URL."""

SOURCE_LIST_MSG = """📋 <b>Ваши источники</b> (всего: {count}):

{source_list}"""

SOURCE_LIST_BUTTONS = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="◀️", callback_data="prev_page"),
    InlineKeyboardButton(text="▶️", callback_data="next_page")],[InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_sources")]])


DELETE_SOURCE_MSG = """🗑 <b>Удаление источника</b>

Выберите источник из списка:"""

DELETE_SOURCE_BUTTONS = InlineKeyboardMarkup(inline_keyboard=[[]])
# Динамически генерируемые кнопки для каждого источника (callback_data="delete_source_{id}")

SOURCE_DELETED_MSG = """🗑 <b>Источник удален</b>

Больше статьи из него не будут приходить."""

NOTIFICATION_SETTINGS_MSG = """⏰ <b>Настройки уведомлений</b>

Выберите время, когда я буду присылать новые статьи:"""

NOTIFICATION_TIME_BUTTONS = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Утро (09:00)", callback_data="set_time_morning"),
    InlineKeyboardButton(text="День (14:00)", callback_data="set_time_afternoon")],
    [InlineKeyboardButton(text="Вечер (19:00)", callback_data="set_time_evening"),
    InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_sources")]]
)

TIME_UPDATED_MSG = """⏰ <b>Время обновлено!</b>

Теперь уведомления будут приходить в {time}."""

SOURCES_SUBSCRIPTION_REQUIRED_MSG = """🔒 <b>Требуется подписка</b>

Мониторинг источников доступен только с активной подпиской.  
Оформите её в разделе /profile."""