
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
        await update.message.reply_text('Usage: /login <password> <name>')
        return

    password = args[1]
    name = ' '.join(args[2:])

    if password != LOGIN_PASSWORD:
        await update.message.reply_text('Invalid password')
        return

    if db.checkIfIDExists(chat_id):
        db.update_name(chat_id, name)
        await update.message.reply_text(f'Name updated to: {name}')
    else:
        db.addToDb(chat_id, name)
        await update.message.reply_text(f'Logged in as {name}')


# Handle balance changes like +20 or -5
async def balance_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not db.checkIfIDExists(chat_id):
        await update.message.reply_text("You must /login before updating balance.")
        return

    if text.startswith(("+", "-")) and text[1:].isdigit():
        amount = int(text)
        new_balance = db.update_balance(chat_id, amount)
        await update.message.reply_text(f"Your new balance is {new_balance} €")
    else:
        await update.message.reply_text("Please enter a valid amount like +10 or -5.")


# Admin: /allbalances
async def all_balances_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = str(update.effective_chat.id)

    if chat_id not in ADMIN_USERS:
        await update.message.reply_text("You are not authorized to use this command.")
        return

    users = db.get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return

    response = "🏆 Balance Leaderboard 🏆\n\n"
    medals = ["🥇", "🥈", "🥉"]

    for i, (name, balance) in enumerate(users):
        symbol = medals[i] if i < 3 else f"{i+1}."
        sign = "🔻" if balance < 0 else ""
        response += f"{symbol} {name} — {balance} € {sign}\n"

    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)


# Main entry point
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("allbalances", all_balances_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balance_change_handler))

    print("Bot is running...")
    await app.run_polling()



if __name__ == '__main__':
    import asyncio

    async def start():
        await main()

    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No running loop: safe to use asyncio.run
        asyncio.run(start())
    else:
        # Already running loop: fallback for weird edge cases
        import nest_asyncio
        nest_asyncio.apply()
        asyncio.get_event_loop().create_task(start())
