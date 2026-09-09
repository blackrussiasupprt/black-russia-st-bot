import os
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    ConversationHandler,
    filters,
)

# =========================
# НАСТРОЙКИ
# =========================

TOKEN = "8834511415:AAGrNpikUYQTCPASRtZ_3pHDwoDaaVOI9-8"
ADMIN_CHAT_ID = -1004477752290

(
    NICKNAME,
    DEVICE,
    LAST_LOGIN,
    OTHER_ACCESS,
    CONFIRM,
) = range(5)


# =========================
# КЛАВИАТУРЫ
# =========================

def main_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["🔐 Мой аккаунт взломали"],
            ["🔑 Я потерял доступ к аккаунту"],
        ],
        resize_keyboard=True,
    )


def cancel_keyboard():
    return ReplyKeyboardMarkup(
        [["❌ Отмена"]],
        resize_keyboard=True,
    )


def navigation_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["⬅️ Назад", "❌ Отмена"],
        ],
        resize_keyboard=True,
    )


def confirm_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📨 Отправить заявку"],
            ["✏️ Изменить", "❌ Отмена"],
        ],
        resize_keyboard=True,
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    text = (
        "👋 Добро пожаловать!\n\n"
        "Данный бот создан специально для помощи игрокам Black Russia.\n\n"
        "С его помощью вы можете подать заявку на восстановление "
        "доступа к игровому аккаунту, если ваш аккаунт был взломан "
        "или вы потеряли к нему доступ.\n\n"
        "⚠️ Никогда не сообщайте свои данные обычным игрокам — "
        "вы можете потерять доступ к аккаунту.\n\n"
        "Выберите причину обращения:"
    )

    await update.message.reply_text(
        text,
        reply_markup=main_keyboard(),
    )


# =========================
# НАЧАЛО АНКЕТЫ
# =========================

async def start_application(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    if update.message.text == "🔐 Мой аккаунт взломали":
        context.user_data["request_type"] = "🔐 Мой аккаунт взломали"

        intro = (
            "🔐 Восстановление взломанного аккаунта\n\n"
            "Если ваш аккаунт был взломан или при входе появляется "
            "ошибка 102, заполните данную анкету.\n\n"
            "После отправки заявка будет передана техническим "
            "специалистам Black Russia для рассмотрения.\n\n"
        )

    else:
        context.user_data["request_type"] = "🔑 Я потерял доступ к аккаунту"

        intro = (
            "🔑 Восстановление доступа к аккаунту\n\n"
            "Если вы потеряли доступ к своему аккаунту, заполните "
            "данную анкету.\n\n"
            "После отправки заявка будет передана техническим "
            "специалистам Black Russia для рассмотрения.\n\n"
        )

    await update.message.reply_text(
        intro
        + "📋 АНКЕТА\n\n"
        "1️⃣ Ваш цифровой никнейм:",
        reply_markup=cancel_keyboard(),
    )

    return NICKNAME


# =========================
# 1. НИКНЕЙМ
# =========================

async def nickname(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    context.user_data["nickname"] = update.message.text

    await update.message.reply_text(
        "2️⃣ Ваше устройство:\n\n"
        "Например: iPhone 15, Samsung Galaxy S24, Redmi Note 13.",
        reply_markup=navigation_keyboard(),
    )

    return DEVICE


# =========================
# 2. УСТРОЙСТВО
# =========================

async def device(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    if update.message.text == "◀️ Назад":
        await update.message.reply_text(
            "1️⃣ Ваш цифровой никнейм:",
            reply_markup=cancel_keyboard(),
        )
        return NICKNAME

    context.user_data["device"] = update.message.text

    await update.message.reply_text(
        "3️⃣ Ваш пароль от аккаунта:",
        reply_markup=navigation_keyboard(),
    )
    return LAST_LOGIN

# =========================
# 3. ПАРОЛЬ ОТ АККАУНТА
# =========================

async def last_login(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    if update.message.text == "⬅️ Назад":
        await update.message.reply_text(
            "2️⃣ Ваше устройство:\n\n"
            "Например: iPhone 15, Samsung Galaxy S24, Redmi Note 13.",
            reply_markup=navigation_keyboard(),
        )
        return DEVICE

    context.user_data["last_login"] = update.message.text

    # ИСПРАВЛЕНО: объединили строки в одну правильную строку
    await update.message.reply_text(
        "🎓 Имеет ли кто-то доступ к вашему аккаунту помощь вам?\n\n"
        "Например: Да / Нет / Не знаю",
        reply_markup=navigation_keyboard(),
    )


    return OTHER_ACCESS


# =========================
# 4. ДОСТУП ДРУГИХ ЛИЦ
# =========================

async def other_access(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.message.text == "❌ Отмена":
        return await cancel(update, context)

    if update.message.text == "⬅️ Назад":
        await update.message.reply_text(
            "3️⃣ Когда вы последний раз входили на аккаунт?\n\n"
            "Укажите примерную дату или дату и время.",
            reply_markup=navigation_keyboard(),
        )
        return LAST_LOGIN

    context.user_data["other_access"] = update.message.text

    await show_preview(update, context)

    return CONFIRM


# =========================
# ПРЕДПРОСМОТР
# =========================

async def show_preview(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    data = context.user_data

    text = (
        "📋 ПРОВЕРЬТЕ ВАШУ ЗАЯВКУ\n\n"
        f"📌 Тип заявки:\n{data['request_type']}\n\n"
        f"1️⃣ Цифровой никнейм:\n{data['nickname']}\n\n"
        f"2️⃣ Устройство:\n{data['device']}\n\n"
        f"3️⃣ Последний вход:\n{data['last_login']}\n\n"
        f"4️⃣ Доступ других лиц:\n{data['other_access']}\n\n"
        "Если всё указано верно, нажмите "
        "«📨 Отправить заявку»."
    )

    await update.message.reply_text(
        text,
        reply_markup=confirm_keyboard(),
    )


# =========================
# ИЗМЕНЕНИЕ
# =========================

async def edit_application(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    await update.message.reply_text(
        "✏️ Заполнение анкеты начнётся заново.\n\n"
        "1️⃣ Ваш цифровой никнейм:",
        reply_markup=cancel_keyboard(),
    )

    return NICKNAME


# =========================
# ОТПРАВКА ЗАЯВКИ
# =========================

async def submit_application(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    text = update.message.text

    if text == "❌ Отмена":
        return await cancel(update, context)

    if text == "✏️ Изменить":
        return await edit_application(update, context)

    if text != "📨 Отправить заявку":
        await update.message.reply_text(
            "Пожалуйста, выберите действие с помощью кнопок.",
            reply_markup=confirm_keyboard(),
        )
        return CONFIRM

    if not ADMIN_CHAT_ID:
        await update.message.reply_text(
            "⚠️ Чат администрации ещё не настроен."
        )
        return ConversationHandler.END

    data = context.user_data
    user = update.effective_user

    username = (
        f"@{user.username}"
        if user.username
        else "не указан"
    )

    submitted_at = datetime.now().strftime(
        "%d.%m.%Y %H:%M:%S"
    )

    admin_text = (
        "🚨 НОВАЯ ЗАЯВКА\n\n"
        f"📌 Тип: {data['request_type']}\n\n"
        f"👤 Telegram: {username}\n"
        f"🆔 Telegram ID: {user.id}\n\n"
        f"1️⃣ Цифровой никнейм:\n"
        f"{data['nickname']}\n\n"
        f"2️⃣ Устройство:\n"
        f"{data['device']}\n\n"
        f"3️⃣ Последний вход:\n"
        f"{data['last_login']}\n\n"
        f"4️⃣ Доступ других лиц:\n"
        f"{data['other_access']}\n\n"
        f"⏱ Дата подачи:\n{submitted_at}"
    )

    try:
        await context.bot.send_message(
            chat_id=int(ADMIN_CHAT_ID),
            text=admin_text,
        )

        await update.message.reply_text(
            "✅ Заявка успешно отправлена!\n\n"
            "Ваша заявка передана техническим специалистам "
            "Black Russia.\n\n"
            "Ожидайте рассмотрения заявки.",
            reply_markup=main_keyboard(),
        )

    except Exception:
        await update.message.reply_text(
            "❌ Не удалось отправить заявку.\n\n"
            "Попробуйте ещё раз позже.",
            reply_markup=main_keyboard(),
        )

    context.user_data.clear()

    return ConversationHandler.END


# =========================
# ОТМЕНА
# =========================

async def cancel(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    context.user_data.clear()

    await update.message.reply_text(
        "❌ Заявка отменена.\n\n"
        "Вы вернулись в главное меню.",
        reply_markup=main_keyboard(),
    )

    return ConversationHandler.END


# =========================
# ЗАПУСК
# =========================

def main():
    if not TOKEN:
        raise RuntimeError(
            "BOT_TOKEN не установлен."
        )

    application = Application.builder().token(TOKEN).build()

    conversation = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex(
                    "^🔐 Мой аккаунт взломали$|"
                    "^🔑 Я потерял доступ к аккаунту$"
                ),
                start_application,
            )
        ],

        states={
            NICKNAME: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    nickname
                )
            ],
            DEVICE: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    device
                )
            ],
            LAST_LOGIN: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    last_login
                )
            ],
            OTHER_ACCESS: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    other_access
                )
            ],
            CONFIRM: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND,
                    submit_application
                )
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            MessageHandler(
                filters.Regex("^❌ Отмена$"),
                cancel,
            ),
        ],
    )

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(conversation)

    application.run_polling()


if __name__ == "__main__":
    main()
