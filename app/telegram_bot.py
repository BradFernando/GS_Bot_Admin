from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

from app.GPT.gpt_integration import handle_text, exit_chat  # Importar exit_chat aquí
from app.config import settings
from app.utils.logging_config import setup_logging
from app.utils.responses import responses
from app.utils.keyboards import show_products_by_category_count, show_monthly_income  # Importamos las nuevas funciones

logger = setup_logging()

bot_name = "AdminBot"

# Almacena el chat_id y message_id del mensaje de saludo
greeting_messages = {}


def get_greeting() -> str:
    current_hour = datetime.now().hour
    if 5 <= current_hour < 12:
        return "Buenos días"
    elif 12 <= current_hour < 18:
        return "Buenas tardes"
    else:
        return "Buenas noches"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Handling /start command")

    if isinstance(update, Update) and update.message:
        user_first_name = update.message.from_user.first_name
        chat_id = update.message.chat_id
    elif isinstance(update, Update) and update.callback_query:
        user_first_name = update.callback_query.from_user.first_name
        chat_id = update.callback_query.message.chat_id
    else:
        logger.warning("Update does not have message or callback_query")
        return

    # Resetear el estado de la sesión al iniciar
    context.chat_data["session_closed"] = False

    greeting = get_greeting()
    logger.info(f"Chat ID: {chat_id}")

    greeting_message = responses["greeting_message"].format(
        greeting=greeting,
        user_first_name=user_first_name,
        chat_id=f"`{chat_id}`",
        bot_name=bot_name
    )

    # Actualización del teclado inicial
    keyboard = [
        [InlineKeyboardButton("Autenticación Admin 🔐", callback_data="auth")],
        [InlineKeyboardButton("Estadísticas 📊", callback_data="stats")],
        [InlineKeyboardButton("Gestión de inventario 📦", callback_data="inventory")],
        [InlineKeyboardButton("Salir 🚪", callback_data="salir")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if isinstance(update, Update) and update.message:
        sent_message = await update.message.reply_text(greeting_message, parse_mode='Markdown')
        greeting_messages[chat_id] = {
            "greeting_message_id": sent_message.message_id,
            "chat_id": chat_id
        }
        await update.message.reply_text(responses["menu_message"], reply_markup=reply_markup)
    elif isinstance(update, Update) and update.callback_query:
        await update.callback_query.message.edit_text(greeting_message, parse_mode='Markdown')
        greeting_messages[chat_id] = {
            "greeting_message_id": update.callback_query.message.message_id,
            "chat_id": chat_id
        }
        await update.callback_query.message.edit_text(responses["menu_message"], reply_markup=reply_markup)


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    logger.info(f"Callback data received: {query.data}")

    chat_id = query.message.chat_id

    # Verifica si la sesión está cerrada
    if context.chat_data.get("session_closed", True):
        await query.message.reply_text("La sesión ha terminado. Para empezar de nuevo, escribe /start.")
        return

    if query.data == "auth":
        response = responses["auth_message"]
        keyboard = [[InlineKeyboardButton("Regresar al Inicio ↩", callback_data="return_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=response, reply_markup=reply_markup)
    elif query.data == "stats":
        # Al hacer clic en "Estadísticas", se muestran las opciones de "Ver ingresos" y "Ver productos por categoría"
        keyboard = [
            [InlineKeyboardButton("Ver ingresos 💰", callback_data="view_income")],
            [InlineKeyboardButton("Ver productos por categoría 🗂️", callback_data="view_products_by_category")],
            [InlineKeyboardButton("Regresar al Inicio ↩", callback_data="return_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text="Seleccione una opción para ver estadísticas:", reply_markup=reply_markup)
    elif query.data == "view_income":
        await show_monthly_income(query)  # Llama a la nueva función para mostrar las ganancias mensuales
    elif query.data == "view_products_by_category":
        await show_products_by_category_count(query)  # Llama a la nueva función para mostrar productos por categoría
    elif query.data == "inventory":
        response = responses["inventory_message"]
        keyboard = [[InlineKeyboardButton("Regresar al Inicio ↩", callback_data="return_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=response, reply_markup=reply_markup)
    elif query.data == "salir":
        await exit_chat(update, context)  # Llama a la función exit_chat para manejar la salida
    elif query.data == "return_start":
        await start(update, context)


def run_bot():
    application = Application.builder().token(settings.bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.run_polling()
