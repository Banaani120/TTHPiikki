
import db
import prices
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
    user_id = update.effective_user.id
    args = update.message.text.split()

    if len(args) < 3:
        await update.message.reply_text('Käyttö: /login <avain> <nimi>')
        return

    password = args[1]
    name = ' '.join(args[2:])

    if password != LOGIN_PASSWORD:
        await update.message.reply_text('Väärä avain')
        return

    if db.checkIfIDExists(user_id):
        db.update_name(user_id, name)
        await update.message.reply_text(f'Nimi ja ääni muutettu: {name}')
    else:
        db.addToDb(user_id, name)
        await update.message.reply_text(f'Dokuttelemisiin {name}')


# Handle balance changes like +20 or -5
async def balance_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.effective_user.id
    text = update.message.text.replace(" ", "")

    if not db.checkIfIDExists(user_id):
        await update.message.reply_text("Du måste locka in 💅 (/login)")
        return
    
    if context.user_data.get("waiting_for_price_list"):
        return  # Let price_edit_handler handle it

    try:
        text_clean = text.replace(",", ".")
        amount = float(text_clean)
        new_balance = db.update_balance(user_id, amount)
        await update.message.reply_text(f"Saldo {new_balance:.2f} €")
    except ValueError:
        await update.message.reply_text("Laita vaikka -1.5 tai +1,5")



async def velat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if not db.checkIfIDExists(user_id):
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
        response += f"{symbol} {name}: {balance:.2f} € {sign}\n"

    for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
        await update.message.reply_text(chunk)



async def hinnat_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if not db.checkIfIDExists(user_id):
        await update.message.reply_text("Du måste locka in 💅 (/login)")
        return

    items = prices.get_all_prices()
    if not items:
        await update.message.reply_text("Ei kaljaa :(")
        return

    response = "📋 HINNASTO 📋\n\n"
    for name, price in items:
        response += f"{name.capitalize()}: {price:.2f} €\n"

    await update.message.reply_text(response)


# Admin:

async def muokkaahintoja_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if user_id not in ADMIN_USERS:
        await update.message.reply_text("Isännän hommia 💀")
        return

    items = prices.get_all_prices()
    response = "" # \nKirjoita uusi hinnasto muodossa:\ntuote - hinta
    for name, price in items:
        response += f"{name.capitalize()}: {price:.2f} €\n"

    response += ""
    await update.message.reply_text(response)

    context.user_data["waiting_for_price_list"] = True


async def price_edit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)

    if user_id not in ADMIN_USERS:
        return

    if not context.user_data.get("waiting_for_price_list"):
        return

    lines = update.message.text.strip().splitlines()
    if not lines:
        await update.message.reply_text("Lähetä vähintään yksi rivi muodossa: nimi - hinta")
        return
    
    updated_items = []
    errors = []
    prices.clear_all_prices()
    for index, line in enumerate(lines):
        if "-" not in line:
            errors.append(f"❌ Rivi ilman '-' merkkiä: {line}")
            continue

        try:
            name, price = line.split("-", 1)
            name = name.strip()
            price = float(price.strip().replace(",", "."))

            prices.set_price(name, price, index)
            updated_items.append(f"✅ {name.capitalize()} - {price:.2f} €")
        except Exception:
            errors.append(f"❌ Virhe rivillä: {line}")


    context.user_data["waiting_for_price_list"] = False

    result_message = "💾 Hinnasto päivitetty:\n\n"
    result_message += "\n".join(updated_items) if updated_items else "Ei onnistuneita päivityksiä."

    if errors:
        result_message += "\n\n⚠️ Virheet:\n" + "\n".join(errors)

    await update.message.reply_text(result_message)



if __name__ == '__main__':
    #prices.init_prices_db() #only needed once
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("login", login_command))
    app.add_handler(CommandHandler("velat", velat_command))
    app.add_handler(CommandHandler("hinnat", hinnat_command))
    app.add_handler(CommandHandler("muokkaahintoja", muokkaahintoja_command))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, price_edit_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, balance_change_handler))

    print("Bot is running...")
    app.run_polling()
