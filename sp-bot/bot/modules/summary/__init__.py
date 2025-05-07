from aiogram import Bot, Router, F
from aiogram.types import Message
from aiogram.filters.state import State, StatesGroup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from core.config import ADMIN_ID, ZENROWS_TOKEN

from openai import OpenAI
import asyncio

summary_router = Router()

# Инициализация OpenAI клиента для OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",  # Замените на ваш ключ
)

# Состояния FSM
class SummaryStates(StatesGroup):
    waiting_for_url = State()
    waiting_for_edit = State()  # Для режима редактирования

# Хранилище контекста (вместо БД для примера)
user_contexts = {}

# --- Обработчики команд ---
@summary_router.message(Command("summarize", "s"))
async def handle_summary_command(message: Message, state: FSMContext):
    args = message.text.split(maxsplit=1)
    
    if len(args) > 1 and is_valid_url(args[1]):
        await process_url(message, args[1], state)
    else:
        await message.answer("📝 Отправьте ссылку на статью:")
        await state.set_state(SummaryStates.waiting_for_url)

# Обработка ссылки
@summary_router.message(SummaryStates.waiting_for_url, F.text & ~F.text.startswith("/"))
async def handle_url_input(message: Message, state: FSMContext):
    if not is_valid_url(message.text):
        await message.reply("⚠️ Неверный формат ссылки. Попробуйте еще раз:")
        return
    
    await process_url(message, message.text, state)

# Режим редактирования
@summary_router.message(SummaryStates.waiting_for_edit)
async def handle_edit_mode(message: Message, state: FSMContext):
    user_id = message.from_user.id
    context = user_contexts.get(user_id)
    
    if not context:
        await message.answer("❌ Сессия устарела. Начните заново с /s")
        await state.clear()
        return
    
    # Добавляем пожелание пользователя в контекст
    context['messages'].append({
        "role": "user",
        "content": message.text
    })
    
    # Отправляем запрос к ИИ
    progress_msg = await message.reply("🔄 Обновляю выжимку...")
    
    try:
        new_summary = await generate_summary(context['messages'])
        await progress_msg.edit_text(
            f"📝 <b>Обновлённая выжимка:</b>",
            parse_mode="HTML"
        )

        try:
            mess = await progress_msg.reply(new_summary.replace("\\n", "\n").replace('\"', '"'), parse_mode="HTML")
        except:
            mess = await progress_msg.reply(new_summary.replace("\\n", "\n").replace('\"', '"'))
        
        await mess.reply(
            "✏️ Можете продолжить редактирование или нажать /s для новой статьи",
            parse_mode="HTML"
        )
        
        # Обновляем контекст
        context['messages'].append({
            "role": "assistant",
            "content": new_summary
        })
        
    except Exception as e:
        await progress_msg.edit_text(f"❌ Ошибка: {str(e)}")

# --- Основные функции ---
async def process_url(message: Message, url: str, state: FSMContext):
    """Генерация выжимки из URL"""
    progress_msg = await message.reply(f"🔎 Анализирую статью...\n\n<code>{url}</code>", 
        parse_mode="HTML")
    
    try:
        # Имитация получения текста статьи (замените на реальный парсинг)
        article_text = await fetch_article_text(url)  
        
        # Формируем контекст для ИИ
        messages = [
            {
                "role": "system",
                "content": (
                    "Ты — профессиональный редактор. Ты пишешь посты для Telegram канала. Создай краткую выжимку из статьи "
                    "с соблюдением структуры (примерно):\n"
                    "1. Основная мысль (1 предложение)\n"
                    "2. Основная часть\n"
                    "3. CTA"
                    "Язык: русский. Не добавляй посторонней информации."
                    "Вот пример стиля:"
"""
🔥 Как AI ломает шаблоны: 7 сдвигов в ожиданиях пользователей, которые нельзя игнорировать

Вы замечали, что клиенты стали нетерпеливее? Что «удобный интерфейс» теперь означает «адаптируйся под меня»? 

В статье The Expectation Reset Брайан Бальфур (эксперт по growth, экс-HubSpot) разбирает, как ИИ не просто улучшает продукты, а меняет саму природу ожиданий пользователей. Вот главные тренды:

1. «Я создаю» → «Сделай за меня»
Раньше: Canva, Photoshop, Google Docs — инструменты для творчества.
Теперь: Midjourney генерирует дизайн по запросу, Devin пишет код вместо разработчика, а EvenUp составляет юридические документы за часы вместо месяцев.
Что делать: Ищите, какие рутинные задачи ваших пользователей можно автоматизировать — и превращайте их в «AI-сотрудников».

2. «Я настраиваю» → «Продукт адаптируется ко мне»
Пример: TikTok сразу показывает релевантный контент без подписок, а CRM Day.ai настраивается под бизнес-процессы.
Вывод: Пользователи больше не хотят тратить время на кастомизацию — AI должен учиться на их поведении.

3. «Я плачу за лицензии» → «Плачу за результат»
Тренд: Synthesia (генерация видео) берет деньги за минуты контента, EvenUp — за сгенерированный иск, Intercom — за решенный тикет.
Совет: Пересматривайте модели монетизации — ценность теперь в outcome, а не в «доступе».

4. «Я жду» → «Мне нужно сейчас»
GitHub Copilot дает ответ в IDE за секунды, Fin от Intercom решает 70% запросов без человека.
Вывод: Скорость — новый must-have.

5. «Я учу интерфейс» → «Интерфейс учится у меня»
Google Gemini создает кастомные UI под запрос, Perplexity меняет интерфейс для shopping-запросов.
Совет: Динамические интерфейсы — следующий рубеж.

❗️Главный инсайт:
PMF (Product-Market Fit) больше не статичен — он «коллапсирует» из-за скачков ожиданий. То, что было «достаточно хорошо» вчера, сегодня устарело.

Что делать?

Аудит боли — какие рутинные задачи пользователей можно убить AI?

Гибкая монетизация — привязка к результату, а не к «месту».

Скорость как фича — даже B2B-клиенты теперь хотят instant-решений.

Полный разбор с кейсами — в оригинале статьи (https://www.reforge.com/blog/the-expectation-reset).

P.S. А какие из этих трендов уже бьют по вашему продукту? Делитесь в комментах! 👇

---

Используй только Telegram-форматирование:  
- **Жирный**: `<b>текст</b>` или `<strong>текст</strong>`  
- *Курсив*: `<i>текст</i>` или `<em>текст</em>`  
- <u>Подчёркнутый</u>: `<u>текст</u>` или `<ins>текст</ins>`  
- ~~Зачёркнутый~~: `<s>текст</s>`, `<strike>текст</strike>` или `<del>текст</del>`  
- `Код`: `<code>текст</code>`  
- Блок кода: `<pre>текст</pre>`  
- ||Спойлер||: `<tg-spoiler>текст</tg-spoiler>`  
- [Ссылка](https://example.com): `<a href="URL">текст</a>`  
- > Цитата: `<blockquote>текст</blockquote>`  
- Упоминание: `<a href="tg://user?id=123">@юзер</a>`  

Другие HTML-теги или Markdown **не поддерживаются**.
"""
                )
            },
            {
                "role": "user",
                "content": f"Создай выжимку из этой статьи:\n\n{article_text}"
            }
        ]
        
        summary = await generate_summary(messages)

        # Сохраняем контекст для редактирования
        user_contexts[message.from_user.id] = {
            'url': url,
            'messages': messages + [{"role": "assistant", "content": summary}]
        }
        
        # Отправляем результат с кнопками
        await progress_msg.edit_text(
            f"📝 <b>Готовая выжимка:</b>",
            parse_mode="HTML"
        )

        try:
            mess = await progress_msg.reply(summary.replace("\\n", "\n").replace('\"', '"'), parse_mode="HTML")
        except:
            mess = await progress_msg.reply(summary.replace("\\n", "\n").replace('\"', '"'))

        await mess.reply("✏️ Напишите свои правки текстом, и я адаптирую выжимку.")
        
        await state.set_state(SummaryStates.waiting_for_edit)
    
    except Exception as e:
        await progress_msg.edit_text(f"❌ Ошибка: {str(e)}")
        await state.clear()

async def generate_summary(messages: list) -> str:
    """Запрос к OpenRouter API"""
    completion = client.chat.completions.create(
        model="tngtech/deepseek-r1t-chimera:free",  # Бесплатная модель
        messages=messages,
        temperature=0.3,  # Для меньшей "креативности"
        max_tokens=5000
    )

    print(completion)

    return completion.choices[0].message.reasoning

def is_valid_url(text: str) -> bool:
    return text.startswith(("http://", "https://"))

async def fetch_article_text(url: str) -> str:
    # return res
    from zenrows import ZenRowsClient

    client = ZenRowsClient(ZENROWS_TOKEN)
    params = {"js_render":"true","wait":"15000","response_type":"markdown"}

    response = client.get(url, params=params)
    return response.text