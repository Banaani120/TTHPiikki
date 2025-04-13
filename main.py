
import db
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Load secrets and config
BOT_TOKEN = open('SECRETS.txt', 'r').readline().strip()
LOGIN_PASSWORD = open('LOGIN_PASSWORD.txt', 'r').readline().strip()
ADMIN_USERS = [line.strip() for line in open('ADMIN_USERS.txt')]


# /login <password> <name>
async def login_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    args = update.message.text.split()

    if len(args) < 3:
        await update.message.reply_text('Käyttö: /login <avain> <nimi>')
        return

    password = args[1]
    name = ' '.join(args[2:])

    if password != LOGIN_PASSWORD:
        await update.message.reply_text('Väärä avain')
        return

    if db.checkIfIDExists(chat_id):
        db.update_name(chat_id, name)
        await update.message.reply_text(f'Nimi ja ääni muutettu: {name}')
    else:
        db.addToDb(chat_id, name)
        await update.message.reply_text(f'Dokuttelemisiin {name}')


# Handle balance changes like +20 or -5
async def balance_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not db.checkIfIDExists(chat_id):
        await update.message.reply_text("Du måste locka in 💅 (/login)")
        return

    try:
        text_clean = text.replace(",", ".")
        amount = float(text_clean)
        new_balance = db.update_balance(chat_id, amount)
        await update.message.reply_text(f"Saldo {new_balance} €")
    except ValueError:
        await update.message.reply_text("Laita vaikka -2 tai +2")



async def velat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)

    if not db.checkIfIDExists(chat_id):
        await update.message.reply_text("Du måste locka in 💅 (/login)")
        return

    users = db.get_all_users()
    if not users:
        await update.message.reply_text("Ei juoppoja 😭")
        return

    response = "💅 VELAT 💅\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (name, balance) in enumerate(users):
        symbol = medals[i] if i < 3 else f"{i+1}."
        sign = "💀" if balance <= -20 else ""
        response += f"{symbol} {name} {balance} € {sign}\n"

    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)


# Admin:

# Main entry point
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("velat", velat_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balance_change_handler))

    print("Bot is running1...")
    await app.run_polling()



if __name__ == '__main__':
   main()
   """ from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("velat", velat_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balance_change_handler))

    print("Bot is running2...")
    app.run_polling()"""

