import telegram

def start(update, context):
    text = "<b>¡Hola!</b> que tal"
    context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML", reply_markup=telegram.ReplyKeyboardRemove())

