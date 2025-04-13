import db
from telegram import Update, ForceReply
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, Filters


# Constant values
BOT_TOKEN = open('SECRETS.txt', 'r').readline().rstrip('\n')
LOGIN_PASSWORD = open('LOGIN_PASSWORD.txt', 'r').readline().rstrip('\n')
ADMIN_USERS = open('ADMIN_USERS.txt', 'r').readlines()
ADMIN_USERS = [s.strip() for s in ADMIN_USERS]

def login_command(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    args = update.message.text.split()

    if len(args) < 3:
        update.message.reply_text('Usage: /login <password> <name>')
        return

    password = args[1]
    name = ' '.join(args[2:])

    if password != LOGIN_PASSWORD:
        update.message.reply_text('Invalid password')
        return

    if db.checkIfIDExists(chat_id):
        db.update_name(chat_id, name)
        update.message.reply_text(f'Name updated to: {name}')
        return

    update.message.reply_text(f'Logged in as {name}')
    db.addToDb(chat_id, name)


def balance_change_handler(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat.id
    text = update.message.text.strip()

    # Ignore if not logged in
    if not db.checkIfIDExists(chat_id):
        update.message.reply_text("You must /login before updating balance.")
        return

    # Only allow messages like "+10", "-5", etc.
    if text.startswith(("+", "-")) and text[1:].isdigit():
        amount = int(text)
        new_balance = db.update_balance(chat_id, amount)
        update.message.reply_text(f"Your new balance is {new_balance} €")
    else:
        update.message.reply_text("Please enter a valid amount like +10 or -5.")




def all_balances_command(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.message.chat.id)

    if chat_id not in ADMIN_USERS:
        update.message.reply_text("You are not authorized to use this command.")
        return

    users = db.get_all_users()
    if not users:
        update.message.reply_text("No users found.")
        return

    response = "🏆 Balance Leaderboard 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (name, balance) in enumerate(users):
        symbol = medals[i] if i < 3 else f"{i+1}."
        sign = "🔻" if balance < 0 else ""
        response += f"{symbol} {name} {balance} € {sign}\n"

    # Telegram message limit is 4096 characters
    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        update.message.reply_text(chunk)



def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher
    # on different commands - answer in Telegram

    # All users
    dispatcher.add_handler(CommandHandler("login", login_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, balance_change_handler))

    #dispatcher.add_handler(CommandHandler("update", update_command))

    # Logged in
    #dispatcher.add_handler(CommandHandler("iltaa", photo_command))
    #dispatcher.add_handler(CommandHandler("delete", deletedata_command))

    # Admin
    #dispatcher.add_handler(CommandHandler("db", db_command))
    #dispatcher.add_handler(CommandHandler("log", log_command))
    dispatcher.add_handler(CommandHandler("allbalances", all_balances_command))


    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()