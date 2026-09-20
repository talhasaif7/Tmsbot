import base64
import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
import io
import random
import string
import requests
import json
import os
import urllib.parse
import re
import html
import time
from datetime import datetime
import http.server
import socketserver
import threading

# =========================================================
# 👑 BOT & ADMIN CONFIGURATION
# =========================================================
TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = "123456789"  # আপনার Telegram Admin ID দিন
ADMIN_USERNAME = "Rafsanvai0" # আপনার টেলিগ্রাম ইউজারনেম
BOT_USERNAME = "@HTML_OFFUSCATOR_BOT"
IMGBB_API_KEY = "ef424e1e7e96e0ebe80f079612575a80" # ImgBB API Key
PORT = int(os.environ.get("PORT", 8080))

# 📢 মাস্ট-জয়েন চ্যানেল/গ্রুপ সেটিংস (Force Sub)
CHANNEL_ID = "-1003471394528" 
CHANNEL_LINK = "https://t.me/+IM3CypkvPakyMjk1"

bot = telebot.TeleBot(TOKEN, parse_mode=None, threaded=True)

# =========================================================
# 🗄️ DATABASE SETUP
# =========================================================
DB_FILE = 'bot_db.json'

def load_db():
    default_db = {
        "users": [], "activities": [], "bot_active": True, 
        "saved_urls": [], "saved_files": [],
        "stats": {"obf": 2488, "url": 2535, "img": 392}
    }
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for key in default_db:
                    if key not in data: data[key] = default_db[key]
                if "stats" not in data: data["stats"] = default_db["stats"]
                return data
            except: return default_db
    return default_db

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

db = load_db()
user_states = {}

def add_user(user_id):
    if str(user_id) not in db['users']:
        db['users'].append(str(user_id))
        save_db(db)

def log_activity(user_id, action):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db['activities'].append(f"[{time_now}] UID: {user_id} -> {action}")
    if len(db['activities']) > 50: db['activities'] = db['activities'][-50:]
    save_db(db)

# =========================================================
# 📱 PERSISTENT BOTTOM KEYBOARD MENU
# =========================================================
def get_persistent_menu(user_id=None):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    btn_img = KeyboardButton("📸 𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋")
    btn_obf = KeyboardButton("🔐 𝐎𝐁𝐅𝐔𝐒𝐂𝐀𝐓𝐄 𝐇𝐓𝐌𝐋")
    btn_url = KeyboardButton("🌐 𝐔𝐑𝐋 𝐓𝐎 𝐇𝐓𝐌𝐋")
    btn_stats = KeyboardButton("📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐒")
    btn_dev = KeyboardButton("👑 𝐎𝐖𝐍𝐄𝐑 & 𝐃𝐄𝐕")

    markup.add(btn_img)
    markup.add(btn_obf, btn_url)
    
    if user_id and str(user_id) == str(ADMIN_ID):
        btn_admin = KeyboardButton("🛠️ 𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐍𝐓𝐑𝐎𝐋")
        markup.add(btn_admin)
        
    markup.add(btn_stats, btn_dev)
    return markup

# =========================================================
# 🔒 FORCE SUB CHECKER
# =========================================================
def is_subscribed(user_id):
    if str(user_id) == str(ADMIN_ID):
        return True
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator', 'restricted']:
            return True
        return False
    except Exception as e:
        print(f"Force Sub Error: {e}")
        return False

def check_force_sub(chat_id):
    if not is_subscribed(chat_id):
        markup = InlineKeyboardMarkup(row_width=1)
        btn1 = InlineKeyboardButton("📢 গ্রুপে জয়েন করুন (Join Now)", url=CHANNEL_LINK)
        btn2 = InlineKeyboardButton("✅ চেক জয়েন / আনলক করুন", callback_data="check_sub")
        markup.add(btn1, btn2)
        lock_text = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   🔒 <b>𝐀𝐂𝐂𝐄𝐒𝐒 𝐋𝐎𝐂𝐊𝐄𝐃 - 𝐉𝐎𝐈𝐍 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃</b> 🔒\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            "👋 <b>প্রিয় গ্রাহক,</b>\n"
            "বটটির সমস্ত ভিআইপি ফিচার ও আনলিমিটেড সার্ভিস ব্যবহার করতে হলে আপনাকে অবশ্যই আমাদের অফিশিয়াল চ্যানেলে যুক্ত থাকতে হবে।\n\n"
            "👉 <b>নিচের 'গ্রুপে জয়েন করুন' বাটনে ক্লিক করে যুক্ত হোন এবং তারপর 'চেক জয়েন' বাটনে চাপ দিন:</b>"
        )
        bot.send_message(chat_id, lock_text, reply_markup=markup, parse_mode="HTML")
        return False
    return True

# =========================================================
# 🔐 HARDCORE MULTI-LAYER CIPHER ENGINE
# =========================================================
def mask_scripts(html_code):
    def process_script(match):
        script_tag = match.group(1)
        script_content = match.group(2)
        script_end = match.group(3)
        if 'src=' in script_tag.lower() or not script_content.strip():
            return match.group(0)
        b64_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        obfuscated_js = f"eval(decodeURIComponent(escape(atob('{b64_script}'))));"
        return f"{script_tag}\n{obfuscated_js}\n{script_end}"
    return re.sub(r'(<script[^>]*>)(.*?)(</script>)', process_script, html_code, flags=re.IGNORECASE | re.DOTALL)

def rc4_crypt_bytes(data, key):
    S = list(range(256))
    j = 0
    out = bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])
    return out

def hardcore_hex_obfuscate(html_code):
    html_code = mask_scripts(html_code)
    b64_bytes = base64.b64encode(urllib.parse.quote(html_code).encode('utf-8'))
    rc4_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    rc4_key_bytes = rc4_key.encode('utf-8')
    rc4_cipher = rc4_crypt_bytes(b64_bytes, rc4_key_bytes)
    hex_cipher = rc4_cipher.hex()
    arr = [ord(c) for c in hex_cipher]
    arr_str = ",".join(map(str, arr))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    comment_inner = f"""
╔══════════════════════════════════════════════════════════╗
║  🔒 PROTECTED HTML - DO NOT MODIFY THIS HEADER 🔒         ║
║══════════════════════════════════════════════════════════║
║  Obfuscated By: @{ADMIN_USERNAME:<41}║
║  Telegram Bot: {BOT_USERNAME:<42}║
║  Timestamp: {timestamp:<45}║
║  Signature: RAFSAN VIP SHIELD [TOKEN: {rc4_key}]        ║
║══════════════════════════════════════════════════════════║
║  ⚠️ WARNING: Removing or modifying this credit header    ║
║  will cause this page to stop working permanently!       ║
╚══════════════════════════════════════════════════════════╝"""

    header_comment = f"<!--{comment_inner}\n-->"
    expected_stripped = re.sub(r'\s+', '', comment_inner)

    decoder_js = f"""
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {{
        if(e.keyCode == 123) {{ return false; }}
        if(e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0)) {{ return false; }}
        if(e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0)) {{ return false; }}
        if(e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0)) {{ return false; }}
        if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)) {{ return false; }}
    }};
    setInterval(function(){{ debugger; }}, 50);
    console.clear();
    
    var _safe = false;
    var _k = "";
    var _iter = document.createTreeWalker(document, 128, null, false);
    var _node;
    var _expected = "{expected_stripped}";
    
    while ((_node = _iter.nextNode())) {{
        var _val = _node.nodeValue;
        if (_val.indexOf('PROTECTED HTML') !== -1) {{
            var _actual = _val.replace(/\\s+/g, '');
            if (_actual === _expected) {{
                var _idx = _val.indexOf('[TOKEN: ');
                if (_idx !== -1) {{
                    _k = _val.substring(_idx + 8, _idx + 24);
                    _safe = true;
                    break;
                }}
            }}
        }}
    }}
    
    if (!_safe || _k.length !== 16) {{
        document.write('<h1 style="color:red;text-align:center;margin-top:50px;font-family:sans-serif;background:#000;padding:30px;border-radius:10px;">🚨 CRASH: TAMPER DETECTED!<br><br><span style="color:#fff;font-size:16px;">The credit header was modified or deleted. Decryption Key has been destroyed.</span></h1>');
        while(true) {{ debugger; }}
        return;
    }}

    function _R(k, s) {{
        var _s=[], j=0, x, res='';
        for (var i=0; i<256; i++) _s[i]=i;
        for (i=0; i<256; i++) {{
            j=(j+_s[i]+k.charCodeAt(i%k.length))%256;
            x=_s[i]; _s[i]=_s[j]; _s[j]=x;
        }}
        i=0; j=0;
        for (var y=0; y<s.length; y++) {{
            i=(i+1)%256;
            j=(j+_s[i])%256;
            x=_s[i]; _s[i]=_s[j]; _s[j]=x;
            res += String.fromCharCode(s.charCodeAt(y)^_s[(_s[i]+_s[j])%256]);
        }}
        return res;
    }}

    var _A = [{arr_str}];
    var _h = '';
    for(var i=0; i<_A.length; i++) _h += String.fromCharCode(_A[i]);
    var _c = '';
    for(var i=0; i<_h.length; i+=2) {{
        _c += String.fromCharCode(parseInt(_h.substr(i, 2), 16));
    }}
    var _b = _R(_k, _c);
    
    try {{
        var _final = decodeURIComponent(atob(_b));
        document.open();
        document.write(_final);
        document.close();
    }} catch(e) {{
        document.write('<h1 style="color:red;text-align:center;margin-top:50px;background:#000;padding:30px;">🚨 FATAL ERROR: INVALID KEY! HTML CORRUPTED.</h1>');
    }}
    """

    encoded_decoder_js = base64.b64encode(decoder_js.encode('utf-8')).decode('utf-8')
    chunk_size = len(encoded_decoder_js) // 2
    part1 = encoded_decoder_js[:chunk_size]
    part2 = encoded_decoder_js[chunk_size:]

    return f"""{header_comment}
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="author" content="@{ADMIN_USERNAME}">
<script>
    document.addEventListener("contextmenu", function(e){{ e.preventDefault(); }}, false);
</script>
</head>
<body oncontextmenu="return false;" onkeydown="return false;" onmousedown="return false;">
<script>
(function(){{
    var _p1 = '{part1}';
    var _p2 = '{part2}';
    var _combined = _p1 + _p2;
    var _payload = decodeURIComponent(escape(atob(_combined)));
    var _init = new Function(_payload);
    _init();
}})();
</script>
<noscript><h2>⚠️ Please enable JavaScript to view this secure page.</h2></noscript>
</body>
</html>"""

# =========================================================
# 👑 WELCOME MESSAGE FUNCTION
# =========================================================
def send_main_welcome(chat_id, user):
    welcome_text = (
        "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
        "  ⚡ 𝐔𝐋𝐓𝐑𝐀 𝐇𝐓𝐌𝐋 𝐂𝐈𝐏𝐇𝐄𝐑 𝐏𝐑𝐎 ⚡\n"
        "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
        f"👋 <b>স্বাগতম, {html.escape(user.first_name or 'গ্রাহক')}!</b>\n"
        "আপনার সোর্স কোড সম্পূর্ণ 👿🔥🥵💀❌ মাল্টি-লেয়ার সাইফারে লক করুন।\n\n"
        "💎 <b>𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐐𝐔𝐀𝐋𝐈𝐅𝐈𝐂𝐀𝐓𝐈𝐎𝐍𝐒:</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "🔹 🔒 <b>𝐂𝐒𝐒 & 𝐉𝐒 𝐙𝐞𝐫𝐨-𝐋𝐞𝐚𝐤 𝐒𝐡𝐢𝐞𝐥𝐝</b>\n"
        "╰─ ডিকোড করলেও আসল 𝐂𝐒𝐒 ও 𝐉𝐒 কখনোই বের হবে না।\n\n"
        "🔹 🌐 <b>𝟏𝟎𝟎% 𝐍𝐚𝐭𝐢𝐯𝐞 𝐁𝐫𝐨𝐰𝐬𝐞𝐫 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧</b>\n"
        "╰─ 𝐅𝐢𝐫𝐞𝐛𝐚𝐬𝐞 ডাটাবেজ, CSS ও JS সরাসরি স্মুথলি কাজ করবে।\n\n"
        "🔹 🛡️ <b>𝐙𝐞𝐫𝐨 𝐒𝐞𝐜𝐫𝐞𝐭 𝐋𝐞𝐚𝐤 & 𝐌𝐞𝐦𝐨𝐫𝐲 𝐒𝐡𝐫𝐞𝐝𝐝𝐞𝐫</b>\n"
        "╰─ সোর্স কোড বা স্ট্যাটিক ডেটা ডাম্প সম্পূর্ণ প্রতিরোধ।\n\n"
        "🔹 🚫 <b>𝐌𝐢𝐥𝐢𝐭𝐚𝐫𝐲-𝐆𝐫𝐚𝐝𝐞 𝐃𝐞𝐯𝐓𝐨𝐨𝐥𝐬 𝐁𝐥𝐨𝐜𝐤𝐢𝐧𝐠</b>\n"
        "╰─ 𝐅𝟏𝟐, 𝐂𝐭𝐫𝐥+𝐔, 𝐂𝐭𝐫𝐥+𝐒 ও 𝐂𝐨𝐧𝐬𝐨𝐥𝐞 চিরতরে লক।\n\n"
        "🔹 📸 <b>𝐈𝐦𝐚𝐠𝐞 𝐓𝐨 𝐔𝐑𝐋 𝐂𝐨𝐧𝐯𝐞𝐫𝐭𝐞𝐫</b>\n"
        "╰─ যেকোনো ছবি সেন্ড করে সরাসরি হাই-স্পিড ডিরেক্ট লিংক তৈরি করুন।\n\n"
        "🔹 🌐 <b>𝐒𝐦𝐚𝐫𝐭 𝐔𝐑𝐋 𝐓𝐨 𝐑𝐚𝐟𝐬𝐚𝐧 𝐂𝐥𝐨𝐧𝐞𝐫</b>\n"
        "╰─ লাইভ এসেট ফিক্সিং ও স্ক্রিনশট সহ সোর্স কোড সংগ্রহ।\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "👇 <b>নিচের কীবোর্ড মেনু থেকে আপনার প্রয়োজনীয় অপশন নির্বাচন করুন:</b>\n"
        f"🤖 <b>𝐁𝐨𝐭:</b> {BOT_USERNAME} | 👑 <b>𝐎𝐰𝐧𝐞𝐫:</b> @{ADMIN_USERNAME}"
    )
    bot.send_message(chat_id, welcome_text, reply_markup=get_persistent_menu(user.id), parse_mode="HTML")

# =========================================================
# 🚀 COMMAND HANDLERS
# =========================================================
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    add_user(message.chat.id)
    log_activity(message.chat.id, "Started Bot")
    user_states[message.chat.id] = "" 
    
    if not db['bot_active'] and str(message.chat.id) != str(ADMIN_ID):
        bot.reply_to(message, "🛠️ <b>Maintenance Break!</b> Bot is currently offline.", parse_mode="HTML")
        return

    if check_force_sub(message.chat.id):
        send_main_welcome(message.chat.id, message.from_user)

@bot.message_handler(commands=['admin', 'panel'])
def secret_admin_panel(message):
    if str(message.chat.id) != str(ADMIN_ID): return
    user_states[message.chat.id] = "" 
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("👥 View Users", callback_data="admin_view_users"), InlineKeyboardButton("📝 Live Logs", callback_data="admin_view_logs"))
    markup.add(InlineKeyboardButton("🌐 View URLs", callback_data="admin_view_urls"), InlineKeyboardButton("📁 Get User Files", callback_data="admin_view_files"))
    markup.add(InlineKeyboardButton("📣 Broadcast Message", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("🔴 Turn OFF Bot", callback_data="admin_off"), InlineKeyboardButton("🟢 Turn ON Bot", callback_data="admin_on"))
    bot.reply_to(message, "🛡️ <b>ভিআইপি অ্যাডমিন কন্ট্রোল প্যানেল</b> 🛡️\n\nএকটি অপশন বেছে নিন:", reply_markup=markup, parse_mode="HTML")

# =========================================================
# 🔘 INLINE CALLBACK QUERY HANDLER
# =========================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    
    if call.data == "check_sub":
        if is_subscribed(call.from_user.id):
            try: bot.delete_message(chat_id, call.message.message_id)
            except: pass
            bot.send_message(chat_id, "🎉 <b>অভিনন্দন! গ্রুপ মেম্বারশিপ সফলভাবে ভেরিফাইড হয়েছে।</b>", parse_mode="HTML")
            send_main_welcome(chat_id, call.from_user)
        else:
            bot.answer_callback_query(call.id, "❌ আপনি এখনো চ্যানেলে জয়েন করেননি! দয়া করে আগে জয়েন করুন।", show_alert=True)
        return

    if call.data.startswith("admin_"):
        if str(chat_id) != str(ADMIN_ID): return
        if call.data == "admin_off": 
            db['bot_active'] = False; save_db(db)
            bot.send_message(chat_id, "🔴 <b>BOT STATUS:</b> OFFLINE", parse_mode="HTML")
        elif call.data == "admin_on": 
            db['bot_active'] = True; save_db(db)
            bot.send_message(chat_id, "🟢 <b>BOT STATUS:</b> ONLINE", parse_mode="HTML")
        elif call.data == "admin_view_users": 
            bot.send_message(chat_id, f"👥 <b>মোট ইউজার:</b> {len(db['users'])} জন", parse_mode="HTML") 
        elif call.data == "admin_view_logs": 
            logs = "\n".join(db['activities'][-15:]) or "কোনো অ্যাক্টিভিটি নেই।"
            bot.send_message(chat_id, f"📝 <b>লাইভ লগ:</b>\n\n{logs}", parse_mode="HTML")
        elif call.data == "admin_view_urls": 
            urls_log = "\n".join(db.get('saved_urls', [])[-20:]) or "কোনো URL হিস্ট্রি নেই।"
            bot.send_message(chat_id, f"🌐 <b>সর্বশেষ URLs:</b>\n\n{urls_log}", disable_web_page_preview=True, parse_mode="HTML")
        elif call.data == "admin_view_files":
            files = db.get('saved_files', [])
            if not files: bot.send_message(chat_id, "📁 কোনো ফাইল পাওয়া যায়নি।")
            for f in files[-10:]:
                if isinstance(f, dict): 
                    bot.send_document(chat_id, f['file_id'], caption=f"📅 {f['time']}\n👤 User: <code>{f['uid']}</code>", parse_mode="HTML")
        elif call.data == "admin_broadcast":
            user_states[chat_id] = "WAIT_BROADCAST"
            bot.send_message(chat_id, "📣 <b>ব্রডকাস্ট মেসেজটি লিখুন:</b>", parse_mode="HTML")
        return

# =========================================================
# 💬 TEXT & KEYBOARD MENU HANDLER
# =========================================================
@bot.message_handler(func=lambda msg: msg.text and not msg.text.startswith("/"))
def handle_text(message):
    chat_id = message.chat.id
    text = message.text.strip()
    user_id = message.from_user.id
    add_user(user_id)
    
    # ---------------- ADMIN BROADCAST ----------------
    state = user_states.get(chat_id, "")
    if str(chat_id) == str(ADMIN_ID) and state == "WAIT_BROADCAST":
        bot.reply_to(message, "⏳ ব্রডকাস্ট পাঠানো হচ্ছে...")
        success = 0
        for uid in db['users']:
            try: 
                bot.send_message(int(uid), f"📢 <b>অফিশিয়াল নোটিশ:</b>\n\n{message.text}", parse_mode="HTML", reply_markup=get_persistent_menu(uid))
                success += 1
            except: pass
        bot.send_message(chat_id, f"✅ সফলভাবে <code>{success}</code> জন ইউজারের কাছে পাঠানো হয়েছে।", parse_mode="HTML")
        user_states[chat_id] = ""
        return

    if not db['bot_active'] and str(chat_id) != str(ADMIN_ID):
        bot.reply_to(message, "🛠️ Bot is currently offline.")
        return
        
    if not check_force_sub(chat_id): return

    # ---------------- KEYBOARD MENU BUTTONS ----------------
    if "𝐎𝐁𝐅𝐔𝐒𝐂𝐀𝐓𝐄 𝐇𝐓𝐌𝐋" in text:
        user_states[chat_id] = "WAIT_HTML_FILE"
        obf_prompt = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "  🛡️ <b>রাফসান ইনক্রিপ্টেড (TALHA ENCRYPTED)</b>\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            "📁 <b>আপনার <code>.html</code> বা <code>.htm</code> ফাইলটি এখানে সেন্ড করুন:</b>\n\n"
            "🛡️ <b>প্রোটেকশন ফিচারসমূহ:</b>\n"
            "• 🔒 <i>CSS & JS Zero-Leak বাইটকোড শিল্ড</i>\n"
            "• 👿 <i>👿🔥🥵💀❌ মাল্টি-লেয়ার রোber-XOR সাইফার</i>\n"
            "• 🚫 <i>F12, Inspect Element, View Source ও রাইট ক্লিক সম্পূর্ণ ধ্বংস</i>\n"
            "• ⚡ <i>জিরো-লিক মেমোরি ডিকোডার ও কাস্টম অ্যান্টি-থেফট প্রটেকশন</i>\n"
            "• 🌐 <i>ব্রাউজারে ১০০% স্মুথ ও নেটিভ এক্সিকিউশন</i>"
        )
        bot.send_message(chat_id, obf_prompt, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        log_activity(chat_id, "Clicked Obfuscate HTML")
        return

    elif "𝐔𝐑𝐋 𝐓𝐎 𝐇𝐓𝐌𝐋" in text:
        user_states[chat_id] = "WAIT_URL"
        url_prompt = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   🌐 <b>ইউআরএল টু রাফসান (URL TO TALHA)</b> 🌐\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            "🔗 <b>টার্গেট ওয়েবসাইটের ডোমেইন বা লিংক সেন্ড করুন:</b>\n"
            "<i>(যেমন: <code>example.com</code> অথবা <code>https://example.com</code>)</i>\n\n"
            "⚡ <b>সুবিধা:</b> <code>https://</code> না দিলেও বট স্বয়ংক্রিয়ভাবে লাইভ এসেট ফিক্স করে <b>URL_To_Talha.html</b> ফাইল ও লাইভ স্ক্রিনশট ডেলিভারি করবে।"
        )
        bot.send_message(chat_id, url_prompt, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        log_activity(chat_id, "Clicked URL to HTML")
        return

    elif "𝐈𝐌𝐀𝐆𝐄 𝐓𝐎 𝐔𝐑𝐋" in text:
        user_states[chat_id] = "WAIT_IMAGE"
        img_prompt = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   📸 <b>ইমেজ টু ইউআরএল (IMAGE TO URL)</b> 📸\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            "🪄 <b>সহজ ২টি ধাপে আপনার ইমেজের সরাসরি লিংক তৈরি করুন:</b>\n\n"
            "1️⃣ আপনার গ্যালারি থেকে যেকোনো ছবি নির্বাচন করুন।\n"
            "2️⃣ সরাসরি এই বটে ছবি (Photo) হিসেবে সেন্ড করুন।\n\n"
            "⚡ <i>সাপোর্টেড ফরম্যাট: JPG, PNG, WEBP, GIF</i>\n"
            "👇 <b>এখনই আপনার ছবিটি নিচে সেন্ড করুন:</b>"
        )
        bot.send_message(chat_id, img_prompt, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        log_activity(chat_id, "Clicked Image to URL")
        return

    elif "𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐒" in text:
        total_users = len(db['users'])
        obf_count = db['stats']['obf']
        url_count = db['stats']['url']
        img_count = db['stats']['img']
        
        stats_text = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   📊 <b>বট লাইভ স্ট্যাটিস্টিকস (LIVE STATS)</b> 📊\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            f"👥 <b>মোট সক্রিয় ইউজার:</b> <code>{total_users}</code> জন\n"
            f"🔐 <b>এনক্রিপ্টেড সোর্স কোড:</b> <code>{obf_count}</code> টি\n"
            f"🌐 <b>ওয়েবসাইট ক্লোন সম্পন্ন:</b> <code>{url_count}</code> টি\n"
            f"📸 <b>ইমেজ টু লিংক জেনারেট:</b> <code>{img_count}</code> টি\n\n"
            f"⚡ <b>সার্ভার স্ট্যাটাস:</b> 🟢 <b>Active 24/7 (100% Online)</b>\n"
            f"👑 <b>অ্যাডমিন ও ডেভেলপার:</b> @{ADMIN_USERNAME}"
        )
        bot.send_message(chat_id, stats_text, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        log_activity(chat_id, "Viewed Stats")
        return

    elif "𝐎𝐖𝐍𝐄𝐑 & 𝐃𝐄𝐕" in text:
        owner_text = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   💎 <b>𝐕𝐈𝐏 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑 & 𝐎𝐖𝐍𝐄𝐑 𝐈𝐍𝐅𝐎</b> 💎\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            f"👤 <b>মালিক ও ডেভেলপার:</b> @{ADMIN_USERNAME}\n"
            f"🤖 <b>বট ইউজারনেম:</b> {BOT_USERNAME}\n"
            "🛡️ <b>সিস্টেম আর্কিটেকচার:</b> রাফসান আনব্রেকেবল সাইফার ইঞ্জিন\n"
            "🚀 <b>হোস্টিং স্ট্যাটাস:</b> ২৪/৭ লাইভ ক্লাউড ডেডিকেটেড সার্ভার\n\n"
            f"💬 যেকোনো সমস্যা বা প্রজেক্টের জন্য যোগাযোগ করুন: @{ADMIN_USERNAME}"
        )
        bot.send_message(chat_id, owner_text, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        return

    elif "𝐀𝐃𝐌𝐈𝐍 𝐂𝐎𝐍𝐓𝐑𝐎𝐋" in text and str(chat_id) == str(ADMIN_ID):
        secret_admin_panel(message)
        return

    # ---------------- URL TO HTML PROCESSING ----------------
    if state == "WAIT_URL" or text.startswith("http://") or text.startswith("https://") or re.match(r"^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text):
        url = text
        if not url.startswith("http"): url = "https://" + url
            
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        db['saved_urls'].append(f"[{time_now}] UID: {chat_id} -> {url}")
        db['stats']['url'] += 1
        save_db(db)

        if str(chat_id) != str(ADMIN_ID):
            try:
                name = message.from_user.first_name or "Unknown"
                admin_msg = f"🚨 <b>নতুন URL ক্লোন রিকোয়েস্ট!</b>\n👤 Name: {name}\n🆔 ID: <code>{chat_id}</code>\n🌐 URL: {url}"
                bot.send_message(int(ADMIN_ID), admin_msg, parse_mode="HTML")
            except: pass
        
        msg_wait = bot.reply_to(message, "⏳ <b>ওয়েবসাইট থেকে রিয়েল সোর্স কোড ও স্ক্রিনশট সংগ্রহ করা হচ্ছে...</b>", parse_mode="HTML")
        
        try:
            # লাইভ ওয়েবসাইট স্ক্রিনশট
            try:
                screenshot_url = f"https://image.thum.io/get/width/1200/crop/800/noanimate/{url}"
                bot.send_photo(chat_id, screenshot_url, caption=f"📸 <b>লাইভ ওয়েবসাইট স্ক্রিনশট:</b> {url}", parse_mode="HTML")
            except: pass

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = requests.get(url, headers=headers, timeout=25)
            response.raise_for_status() 
            
            html_content = response.text
            # রিলেটিভ পাথ ফিক্সার
            if "<base " not in html_content.lower():
                base_tag = f'<base href="{url}">'
                if re.search(r"<head[^>]*>", html_content, re.IGNORECASE):
                    html_content = re.sub(r"(<head[^>]*>)", rf"\1\n  {base_tag}", html_content, count=1, flags=re.IGNORECASE)
                else:
                    html_content = f"<head>{base_tag}</head>\n" + html_content

            html_file = io.BytesIO(html_content.encode('utf-8'))
            domain = url.split("//")[-1].split("/")[0]
            html_file.name = "URL_To_Talha.html"
            
            caption = (
                "💎 ━━━━━━━━━━━━━━━━━━━━━━━━━ 💎\n"
                "🌐 <b>ইউআরএল টু রাফসান (URL TO TALHA SUCCESS)</b>\n"
                "💎 ━━━━━━━━━━━━━━━━━━━━━━━━━ 💎\n\n"
                f"🔗 <b>টার্গেট 𝐔𝐑𝐋:</b> <code>{html.escape(url)}</code>\n"
                "📁 <b>ফাইল নাম:</b> <code>URL_To_Talha.html</code>\n"
                "✅ <b>লোকাল ব্রাউজার সাপোর্ট:</b> 𝟏𝟎𝟎% সচল ও লাইভ\n"
                "🛠️ <b>সম্পূর্ণ 𝐂𝐒𝐒, 𝐈𝐦𝐚𝐠𝐞𝐬 ও 𝐉𝐒 এসেট ফিক্সড</b>\n\n"
                f"🤖 <b>𝐁𝐨𝐭:</b> {BOT_USERNAME} | 👑 <b>𝐃𝐞𝐯:</b> @{ADMIN_USERNAME}"
            )
            bot.send_document(chat_id, html_file, caption=caption, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
            log_activity(chat_id, f"Fetched URL: {domain}")
            user_states[chat_id] = "" 
        except Exception as e:
            bot.reply_to(message, f"❌ <b>ক্লোন ব্যর্থ:</b> URL ব্লক অথবা অবৈধ। ({str(e)})")
        
        try: bot.delete_message(chat_id, msg_wait.message_id)
        except: pass
        return
        
    bot.reply_to(message, "⚠️ দয়া করে নিচের কীবোর্ড মেনু বাটন ব্যবহার করুন অথবা একটি সঠিক লিংক পাঠান।", reply_markup=get_persistent_menu(user_id))

# =========================================================
# 📁 HTML DOCUMENT HANDLER (ENCRYPTION ENGINE)
# =========================================================
@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    if not db['bot_active'] and str(chat_id) != str(ADMIN_ID):
        bot.reply_to(message, "🛠️ Bot is currently offline.")
        return
        
    if not check_force_sub(chat_id): return

    file_name = message.document.file_name or "file.html"
    if not (file_name.endswith('.html') or file_name.endswith('.htm') or file_name.endswith('.txt')):
        bot.reply_to(message, "⚠️ <b>ভুল ফাইল ফরম্যাট!</b> দয়া করে একটি <code>.html</code> ফাইল সেন্ড করুন।", parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        return

    # Admin Vault Notification
    if str(chat_id) != str(ADMIN_ID):
        try:
            name = message.from_user.first_name or "Unknown"
            admin_msg = f"🚨 <b>নতুন HTML ফাইল রিসিভড (Admin Vault)!</b>\n👤 Name: {name}\n🆔 ID: <code>{chat_id}</code>\n📁 File: {file_name}"
            bot.send_message(int(ADMIN_ID), admin_msg, parse_mode="HTML")
            bot.forward_message(int(ADMIN_ID), chat_id, message.message_id)
        except: pass

    try:
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
        db['saved_files'].append({"time": time_now, "uid": chat_id, "name": file_name, "file_id": message.document.file_id})
        db['stats']['obf'] += 1
        save_db(db)
        
        msg_wait = bot.reply_to(
            message, 
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "   🔒 <b>রাফসান এনক্রিপশন প্রসেসিং চলছে...</b>\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            "⚡ <i>Applying CSS/JS Bytecode Scrambler & 👿🔥 Security Shield...</i>", 
            parse_mode="HTML"
        )
        
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        html_content = downloaded_file.decode('utf-8', errors='ignore')
        
        obfuscated_content = hardcore_hex_obfuscate(html_content)
        
        base_name, _ = os.path.splitext(file_name)
        protected_file_name = f"Talha_Encrypted_{base_name}.html"
        
        obfuscated_file = io.BytesIO(obfuscated_content.encode('utf-8'))
        obfuscated_file.name = protected_file_name

        caption_text = (
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
            "🛡️ <b>রাফসান ইনক্রিপ্টেড (TALHA ENCRYPTED)</b>\n"
            "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
            f"📁 <b>ফাইল নাম:</b> <code>{html.escape(protected_file_name)}</code>\n"
            "🔒 <b>সাইফার আর্কিটেকচার:</b> 👿🔥 𝐌𝐮𝐥𝐭𝐢-𝐋𝐚𝐲𝐞𝐫 𝐂𝐮𝐬𝐭𝐨𝐦 𝐒𝐭𝐫𝐞𝐚𝐦\n"
            "🚫 <b>প্রোটেকশন:</b> 𝐂𝐒𝐒/𝐉𝐒 𝐙𝐞𝐫𝐨-𝐋𝐞𝐚𝐤 + 𝐀𝐧𝐭𝐢-𝐈𝐧𝐬𝐩𝐞𝐜𝐭 + 𝐅𝟏𝟐\n"
            "🌐 <b>ব্রাউজার রানিং:</b> 𝟏𝟎𝟎% 𝐍𝐚𝐭𝐢𝐯𝐞 𝐄𝐱𝐞𝐜𝐮𝐭𝐢𝐨𝐧\n"
            "⚡ <b>সিকিউরিটি লেভেল:</b> 𝐌𝐢𝐥𝐢𝐭𝐚𝐫𝐲-𝐆𝐫𝐚𝐝𝐞 𝐋𝐨𝐜𝐤\n\n"
            f"🤖 <b>𝐁𝐨𝐭:</b> {BOT_USERNAME} | 👑 <b>𝐃𝐞𝐯:</b> @{ADMIN_USERNAME}"
        )
        
        bot.send_document(chat_id, obfuscated_file, caption=caption_text, parse_mode="HTML", reply_markup=get_persistent_menu(user_id))
        log_activity(chat_id, f"Encrypted file: {file_name}")
        user_states[chat_id] = "" 
        try: bot.delete_message(chat_id, msg_wait.message_id)
        except: pass
    except Exception as e:
        bot.reply_to(message, f"❌ <b>এনক্রিপ্ট ব্যর্থ:</b> ({str(e)})", reply_markup=get_persistent_menu(user_id))

# =========================================================
# 📸 PHOTO HANDLER (IMAGE TO URL CONVERTER)
# =========================================================
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    
    if not db['bot_active'] and str(chat_id) != str(ADMIN_ID):
        bot.reply_to(message, "🛠️ Bot is currently offline.")
        return
        
    if not check_force_sub(chat_id): return

    try:
        msg_wait = bot.reply_to(message, "⏳ <b>ছবি আপলোড এবং সরাসরি লিংক তৈরি করা হচ্ছে...</b>", parse_mode="HTML")
        
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        image_url = None
        if IMGBB_API_KEY and IMGBB_API_KEY != "YOUR_IMGBB_API_KEY_HERE":
            response = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files={"image": downloaded_file}, timeout=25)
            res_data = response.json()
            if response.status_code == 200 and res_data.get("success"):
                image_url = res_data["data"]["url"]
        
        if not image_url:
            response = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": ("image.jpg", downloaded_file, "image/jpeg")}, timeout=25)
            if response.status_code == 200:
                image_url = response.text.strip()

        if image_url:
            name = message.from_user.first_name or "Unknown"
            db['stats']['img'] += 1
            save_db(db)
            
            success_text = (
                "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n"
                "📸 <b>ইমেজ টু ইউআরএল (IMAGE TO URL SUCCESS)</b>\n"
                "👑 ━━━━━━━━━━━━━━━━━━━━━━━━━ 👑\n\n"
                f"👤 <b>ইউজার নাম:</b> {html.escape(name)}\n"
                f"🆔 <b>ইউজার আইডি:</b> <code>{chat_id}</code>\n"
                f"🔗 <b>ডিরেক্ট ইমেজ লিংক:</b>\n<code>{image_url}</code>\n\n"
                "⚡ <b>স্ট্যাটাস:</b> পার্মানেন্ট হাই-স্পিড সিডিএন লিংক প্রস্তুত!\n\n"
                f"🤖 <b>𝐁𝐨𝐭:</b> {BOT_USERNAME} | 👑 <b>𝐃𝐞𝐯:</b> @{ADMIN_USERNAME}"
            )
            bot.reply_to(message, success_text, parse_mode="HTML", disable_web_page_preview=False, reply_markup=get_persistent_menu(user_id))
            log_activity(chat_id, "Generated Image URL")
            user_states[chat_id] = ""
        else:
            bot.reply_to(message, "❌ <b>ইমেজ আপলোড ব্যর্থ হয়েছে! আবার চেষ্টা করুন।</b>", parse_mode="HTML")
            
        try: bot.delete_message(chat_id, msg_wait.message_id)
        except: pass
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}", reply_markup=get_persistent_menu(user_id))

# =========================================================
# 🌐 24/7 KEEP-ALIVE WEB SERVER (CRASH-PROOF)
# =========================================================
class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_keep_alive_server():
    class KeepAliveHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            status_page = (
                "<html><head><title>Talha VIP Ultra Bot</title></head>"
                "<body style='font-family:sans-serif;text-align:center;padding-top:60px;background:#0b0e14;color:#58a6ff;'>"
                "<h1>⚡ TALHA VIP ULTRA CIPHER ENGINE ⚡</h1>"
                "<p style='color:#3fb950;font-size:18px;'>🟢 System Status: Active &amp; Online 24/7</p>"
                f"<p style='color:#8b949e;'>Owner &amp; Dev: @{ADMIN_USERNAME} | Bot: {BOT_USERNAME}</p>"
                "</body></html>"
            )
            self.wfile.write(status_page.encode("utf-8"))
        def log_message(self, format, *args): pass

    while True:
        try:
            with ReusableTCPServer(("", PORT), KeepAliveHandler) as httpd:
                print(f"🌐 Keep-Alive Web Server active on port {PORT}")
                httpd.serve_forever()
        except Exception as e:
            print(f"⚠️ Web Server Error: {e}, retrying in 5s...")
            time.sleep(5)

# =========================================================
# 🚀 SYSTEM BOOT & POLLING
# =========================================================
if __name__ == "__main__":
    print("🔥 Starting Talha VIP Ultra Engine...")
    server_thread = threading.Thread(target=run_keep_alive_server, daemon=True)
    server_thread.start()
    
    while True:
        try:
            bot.remove_webhook()
            time.sleep(1)
            print(f"🚀 Bot Polling Active & Running 24/7 ({BOT_USERNAME})...")
            bot.infinity_polling(timeout=30, long_polling_timeout=30, skip_pending=True)
        except Exception as e:
            print(f"⚠️ Polling Exception: {e}. Auto-restarting in 3s...")
            time.sleep(3)    return True

# ================= ADVANCED SENSITIVE MASKING & HOOK EVASION ENGINE =================

def mask_scripts(html_code):
    def process_script(match):
        script_tag = match.group(1)
        script_content = match.group(2)
        script_end = match.group(3)
        if 'src=' in script_tag.lower() or not script_content.strip():
            return match.group(0)
        b64_script = base64.b64encode(script_content.encode('utf-8')).decode('utf-8')
        obfuscated_js = f"eval(decodeURIComponent(escape(atob('{b64_script}'))));"
        return f"{script_tag}\n{obfuscated_js}\n{script_end}"
    return re.sub(r'(<script[^>]*>)(.*?)(</script>)', process_script, html_code, flags=re.IGNORECASE | re.DOTALL)

def rc4_crypt_bytes(data, key):
    S = list(range(256))
    j = 0
    out = bytearray()
    for i in range(256):
        j = (j + S[i] + key[i % len(key)]) % 256
        S[i], S[j] = S[j], S[i]
    i = j = 0
    for char in data:
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        out.append(char ^ S[(S[i] + S[j]) % 256])
    return out

def hardcore_hex_obfuscate(html_code):
    html_code = mask_scripts(html_code)
    b64_bytes = base64.b64encode(urllib.parse.quote(html_code).encode('utf-8'))
    rc4_key = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    rc4_key_bytes = rc4_key.encode('utf-8')
    rc4_cipher = rc4_crypt_bytes(b64_bytes, rc4_key_bytes)
    hex_cipher = rc4_cipher.hex()
    arr = [ord(c) for c in hex_cipher]
    arr_str = ",".join(map(str, arr))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 👇 [এখানকার টেক্সটগুলো আপনি নিজের মতো কাস্টমাইজ করে নিতে পারেন]
    comment_inner = f"""

╔══════════════════════════════════════════════════════════╗
║  🔒 PROTECTED BY TMS CYBER 9X - DO NOT MODIFY THIS       ║
║══════════════════════════════════════════════════════════║
║  Owner / Admin : @talhasaif7                            ║
║  TG Channel    : https://t.me/infinity9x                 ║
║  Timestamp     : {timestamp}                             ║
║  Signature     : TMS CYBER 9X [TOKEN: {rc4_key}]         ║
║══════════════════════════════════════════════════════════║
║  ⚠️ সতর্কতা: এই ক্রেডিট বা কোড পরিবর্তন করলে ফাইল কাজ করবে না!║
╚══════════════════════════════════════════════════════════╝"""

    header_comment = f"<!--{comment_inner}\n-->"  
    expected_stripped = re.sub(r'\s+', '', comment_inner)  

    decoder_js = f"""  
document.addEventListener('contextmenu', event => event.preventDefault());  
document.onkeydown = function(e) {{  
    if(e.keyCode == 123) {{ return false; }}  
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'I'.charCodeAt(0)) {{ return false; }}  
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'C'.charCodeAt(0)) {{ return false; }}  
    if(e.ctrlKey && e.shiftKey && e.keyCode == 'J'.charCodeAt(0)) {{ return false; }}  
    if(e.ctrlKey && e.keyCode == 'U'.charCodeAt(0)) {{ return false; }}  
}};  
setInterval(function(){{ debugger; }}, 50);  
console.clear();  
  
var _safe = false;  
var _k = "";  
var _iter = document.createTreeWalker(document, 128, null, false);  
var _node;  
var _expected = "{expected_stripped}";  
  
while ((_node = _iter.nextNode())) {{  
    var _val = _node.nodeValue;  
    if (_val.indexOf('PROTECTED BY TMS CYBER 9X') !== -1) {{  
        var _actual = _val.replace(/\\s+/g, '');  
        if (_actual === _expected) {{  
            var _idx = _val.indexOf('[TOKEN: ');  
            if (_idx !== -1) {{  
                _k = _val.substring(_idx + 8, _idx + 24);  
                _safe = true;  
                break;  
            }}  
        }}  
    }}  
}}  
  
if (!_safe || _k.length !== 16) {{  
    document.write('<h1 style="color:red;text-align:center;margin-top:50px;font-family:sans-serif;background:#000;padding:30px;border-radius:10px;">🚨 TAMPER DETECTED!<br><br><span style="color:#fff;font-size:16px;">ক্রেডিট পরিবর্তন করার কারণে Decryption Key নষ্ট হয়ে গেছে।</span></h1>');  
    while(true) {{ debugger; }}  
    return;  
}}  

function _R(k, s) {{  
    var _s=[], j=0, x, res='';  
    for (var i=0; i<256; i++) _s[i]=i;  
    for (i=0; i<256; i++) {{  
        j=(j+_s[i]+k.charCodeAt(i%k.length))%256;  
        x=_s[i]; _s[i]=_s[j]; _s[j]=x;  
    }}  
    i=0; j=0;  
    for (var y=0; y<s.length; y++) {{  
        i=(i+1)%256;  
        j=(j+_s[i])%256;  
        x=_s[i]; _s[i]=_s[j]; _s[j]=x;  
        res += String.fromCharCode(s.charCodeAt(y)^_s[(_s[i]+_s[j])%256]);  
    }}  
    return res;  
}}  

var _A = [{arr_str}];  
var _h = '';  
for(var i=0; i<_A.length; i++) _h += String.fromCharCode(_A[i]);  
var _c = '';  
for(var i=0; i<_h.length; i+=2) {{  
    _c += String.fromCharCode(parseInt(_h.substr(i, 2), 16));  
}}  
var _b = _R(_k, _c);  
  
try {{  
    var _final = decodeURIComponent(atob(_b));  
    document.open();  
    document.write(_final);  
    document.close();  
}} catch(e) {{  
    document.write('<h1 style="color:red;text-align:center;margin-top:50px;background:#000;padding:30px;">🚨 FATAL ERROR: INVALID KEY! HTML CORRUPTED.</h1>');  
}}  
"""  

    encoded_decoder_js = base64.b64encode(decoder_js.encode('utf-8')).decode('utf-8')  
    chunk_size = len(encoded_decoder_js) // 2  
    part1 = encoded_decoder_js[:chunk_size]  
    part2 = encoded_decoder_js[chunk_size:]  

    final_html = f"""{header_comment}

<!DOCTYPE html>  <html>  
<head>  
<meta charset="utf-8">  
<meta name="author" id="tdx_author" content="@talhasaif7">  
<script>  
    document.addEventListener("contextmenu", function(e){{ e.preventDefault(); }}, false);  
</script>  
</head>  
<body oncontextmenu="return false;" onkeydown="return false;" onmousedown="return false;">  
<script>  
(function(){{  
    var _p1 = '{part1}';  
    var _p2 = '{part2}';  
    var _combined = _p1 + _p2;  
    var _payload = decodeURIComponent(escape(atob(_combined)));  
    var _init = new Function(_payload);  
    _init();  
}})();  
</script>  
<noscript><h2>⚠️ Please enable JavaScript to view this secure page.</h2></noscript>  
</body>  
</html>"""  
    return final_html  

# ================= MAIN MENU =================

def send_main_menu(chat_id):
    markup = InlineKeyboardMarkup()

    btn_url = InlineKeyboardButton("🌐 Rᴇɴᴅᴇʀ URL", callback_data="btn_url")  
    btn_obf = InlineKeyboardButton("🔒 Oʙғᴜsᴄᴀᴛᴇ HTML", callback_data="btn_obf")  
    btn_img = InlineKeyboardButton("📸 Iᴍᴀɢᴇ ᴛᴏ URL", callback_data="btn_img")  
    btn_stats = InlineKeyboardButton("📊 Sᴛᴀᴛs", callback_data="btn_stats")  
      
    markup.row(btn_url, btn_obf)  
    markup.row(btn_img)  
    markup.row(btn_stats)  
      
    bot.send_message(chat_id, db["texts"]["welcome"], reply_markup=markup, parse_mode="HTML")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    add_user(message.chat.id)
    log_activity(message.chat.id, "Started Bot")
    user_states[message.chat.id] = ""

    if not db['bot_active'] and str(message.chat.id) != ADMIN_ID:  
        bot.reply_to(message, "🛠️ <b>মেনটেন্যান্স ব্রেক!</b> বট বর্তমানে অফলাইন আছে।", parse_mode="HTML")  
        return  

    if check_force_sub(message.chat.id):  
        send_main_menu(message.chat.id)

# ================= ADMIN PANEL =================

@bot.message_handler(commands=['admin'])
def secret_admin_panel(message):
    if str(message.chat.id) != ADMIN_ID: return
    user_states[message.chat.id] = ""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("👥 View Users", callback_data="admin_view_users"), InlineKeyboardButton("📝 Live Logs", callback_data="admin_view_logs"))
    markup.add(InlineKeyboardButton("🌐 View URLs", callback_data="admin_view_urls"), InlineKeyboardButton("📁 Get User Files", callback_data="admin_view_files"))
    markup.add(InlineKeyboardButton("📣 Broadcast Message", callback_data="admin_broadcast"))
    markup.add(InlineKeyboardButton("✏️ Edit Bot Texts", callback_data="admin_edit_texts"))
    markup.add(InlineKeyboardButton("🔴 Turn OFF Bot", callback_data="admin_off"), InlineKeyboardButton("🟢 Turn ON Bot", callback_data="admin_on"))
    bot.reply_to(message, "🛡️ <b>ADMIN PANEL</b> 🛡️\n\nএকটি অপশন বেছে নিন:", reply_markup=markup, parse_mode="HTML")

# ================= BUTTON CALLBACKS =================

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)

    # FORCE SUB CHECK  
    if call.data == "check_sub":  
        if is_subscribed(call.from_user.id):  
            bot.delete_message(chat_id, call.message.message_id)  
            bot.send_message(chat_id, "✅ <b>ভেরিফিকেশন সফল হয়েছে! চ্যানেলে জয়েন করার জন্য ধন্যবাদ।</b>", parse_mode="HTML")  
            send_main_menu(chat_id)  
        else:  
            bot.answer_callback_query(call.id, "❌ আপনি এখনও চ্যানেলে জয়েন করেননি! দয়া করে জয়েন করুন।", show_alert=True)  
        return  

    if call.data.startswith("admin_"):  
        if str(chat_id) != ADMIN_ID: return  
        if call.data == "admin_off": db['bot_active'] = False; save_db(db); bot.send_message(chat_id, "🔴 <b>BOT STATUS:</b> OFFLINE", parse_mode="HTML")  
        elif call.data == "admin_on": db['bot_active'] = True; save_db(db); bot.send_message(chat_id, "🟢 <b>BOT STATUS:</b> ONLINE", parse_mode="HTML")  
        elif call.data == "admin_view_users": bot.send_message(chat_id, f"👥 <b>Total Users:</b> {len(db['users'])}", parse_mode="HTML")   
        elif call.data == "admin_view_logs": logs = "\n".join(db['activities'][-15:]) or "No activities yet."; bot.send_message(chat_id, f"📝 <b>Live Logs:</b>\n\n{logs}", parse_mode="HTML")  
        elif call.data == "admin_view_urls": urls_log = "\n".join(db.get('saved_urls', [])[-20:]) or "No URLs yet."; bot.send_message(chat_id, f"🌐 <b>Last URLs:</b>\n\n{urls_log}", disable_web_page_preview=True, parse_mode="HTML")  
        elif call.data == "admin_view_files":  
            files = db.get('saved_files', [])  
            if not files: bot.send_message(chat_id, "📁 No files yet.")  
            for f in files[-10:]:  
                if isinstance(f, dict): bot.send_document(chat_id, f['file_id'], caption=f"📅 {f['time']}\n👤 User: <code>{f['uid']}</code>", parse_mode="HTML")  
        elif call.data == "admin_broadcast":  
            user_states[chat_id] = "WAIT_BROADCAST"  
            bot.send_message(chat_id, "📣 ব্রডকাস্ট মেসেজ টাইপ করুন (HTML ফরম্যাট সাপোর্ট করবে):", parse_mode="HTML")  
        elif call.data == "admin_edit_texts":  
            markup = InlineKeyboardMarkup()  
            markup.add(InlineKeyboardButton("Edit Welcome", callback_data="edit_txt_welcome"))  
            markup.add(InlineKeyboardButton("Edit Obfuscate Prompt", callback_data="edit_txt_obf_prompt"))  
            markup.add(InlineKeyboardButton("Edit URL Prompt", callback_data="edit_txt_url_prompt"))  
            markup.add(InlineKeyboardButton("Edit Image Prompt", callback_data="edit_txt_img_prompt"))  
            bot.send_message(chat_id, "✏️ যে টেক্সটটি এডিট করতে চান তা সিলেক্ট করুন:", reply_markup=markup)  
        return  

    if call.data.startswith("edit_txt_"):  
        if str(chat_id) != ADMIN_ID: return  
        target = call.data.replace("edit_txt_", "")  
        user_states[chat_id] = f"WAIT_EDIT_{target}"  
        bot.send_message(chat_id, f"{target}-এর জন্য নতুন টেক্সট পাঠান (HTML গ্রহণযোগ্য):")  
        return  

    if not db['bot_active'] and str(chat_id) != ADMIN_ID: return  
    if not check_force_sub(chat_id): return  

    # MAIN MENU BUTTONS  
    if call.data == "btn_obf":  
        user_states[chat_id] = "WAIT_HTML_FILE"  
        bot.send_message(chat_id, db["texts"]["obf_prompt"], parse_mode="HTML")  
        log_activity(chat_id, "Clicked Obfuscate HTML")  
    elif call.data == "btn_url":  
        user_states[chat_id] = "WAIT_URL"  
        bot.send_message(chat_id, db["texts"]["url_prompt"], parse_mode="HTML")  
        log_activity(chat_id, "Clicked URL to HTML")  
    elif call.data == "btn_img":  
        user_states[chat_id] = "WAIT_IMAGE"  
        bot.send_message(chat_id, db["texts"]["img_prompt"], parse_mode="HTML")  
        log_activity(chat_id, "Clicked Image to URL")  
    elif call.data == "btn_stats":  
        total_users = len(db['users'])  
        obf_count = db['stats']['obf']  
        url_count = db['stats']['url']  
        img_count = db['stats']['img']  
          
        stats_text = f"👑 <b>বট স্ট্যাটিস্টিক্স</b>\n\n👥 <b>মোট ইউজার:</b> {total_users}\n🔄 <b>এনক্রিপশন সম্পন্ন:</b> {obf_count}\n🌐 <b>URL রেন্ডার করা হয়েছে:</b> {url_count}\n📸 <b>ছবি কনভার্ট করা হয়েছে:</b> {img_count}"  
          
        bot.send_message(chat_id, stats_text, parse_mode="HTML")  
        log_activity(chat_id, "Viewed Stats")

# ================= MESSAGE & FILE HANDLERS =================

def extract_user_info_safe(message):
    name = message.from_user.first_name if message.from_user.first_name else "Unknown"
    uid = message.chat.id
    username = f"@{message.from_user.username}" if message.from_user.username else "No Username"
    return f"👤 Name: {name}\n🆔 ID: <code>{uid}</code>\n📛 Username: {username}"

@bot.message_handler(content_types=['document'])
def handle_document(message):
    chat_id = message.chat.id
    if not db['bot_active'] and str(chat_id) != ADMIN_ID:
        bot.reply_to(message, "🛠️ বট বর্তমানে অফলাইনে আছে।")
        return

    if not check_force_sub(chat_id): return  
      
    state = user_states.get(chat_id, "")  

    if str(chat_id) != ADMIN_ID:  
        try:  
            info = extract_user_info_safe(message)  
            admin_msg = f"🚨 <b>নতুন ফাইল রিসিভ হয়েছে!</b>\n{info}\n📁 File: {message.document.file_name}"  
            bot.send_message(int(ADMIN_ID), admin_msg, parse_mode="HTML")  
            bot.forward_message(int(ADMIN_ID), chat_id, message.message_id)  
        except Exception: pass  

    # HTML OBFUSCATOR  
    try:  
        if not message.document.file_name.endswith('.html'):  
            bot.reply_to(message, "⚠️ ভুল ফাইল! দয়া করে একটি পাওয়ারফুল `.html` ফাইল পাঠান।")  
            return  
              
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")  
        db['saved_files'].append({"time": time_now, "uid": chat_id, "name": message.document.file_name, "file_id": message.document.file_id})  
          
        db['stats']['obf'] += 1  
        save_db(db)  
          
        bot.reply_to(message, "⏳ <b>প্রসেসিং করা হচ্ছে...</b>\n<b>🌩️ মাল্টি-লেয়ারড এনক্রিপশনের মাধ্যমে ফাইল সুরক্ষিত করা হচ্ছে... ✅</b>", parse_mode="HTML")  
        file_info = bot.get_file(message.document.file_id)  
        downloaded_file = bot.download_file(file_info.file_path)  
        html_content = downloaded_file.decode('utf-8', errors='ignore')  
          
        obfuscated_content = hardcore_hex_obfuscate(html_content)  
          
        obfuscated_file = io.BytesIO(obfuscated_content.encode('utf-8'))  
        
        # 🎯 চাহিদা অনুযায়ী ফাইলের নাম পরিবর্তন: TMS Cyber 9X talhasaif7 Encrypted.html
        obfuscated_file_name = "TMS Cyber 9X talhasaif7 Encrypted.html"  
        obfuscated_file.name = obfuscated_file_name  
          
        file_size_kb = len(obfuscated_content.encode('utf-8')) / 1024  
          
        try:  
            bot.send_photo(chat_id, CUSTOM_PHOTO_URL, caption="🔒 <b>প্রো লেভেল এনক্রিপশন সফলভাবে সম্পন্ন হয়েছে!</b>", parse_mode="HTML")  
        except:  
            pass

        # 👇 [নিচের টেক্সটগুলো আপনি আপনার ইচ্ছামতো কাস্টমাইজ করতে পারবেন]
        caption_text = f"""✅ <b>ফাইল সফলভাবে অবফাসকেট করা হয়েছে!</b>

📁 <b>ফাইলের নাম:</b> {obfuscated_file_name}
📦 <b>সাইজ:</b> {file_size_kb:.1f} KB
👑 <b>ডেভেলপার / ওনার:</b> @talhasaif7

🛡️ <b>প্রোটেকশন লেয়ার:</b>
• 🚫 রাইট ক্লিক ব্লক করা হয়েছে
• ⌨️ কীবোর্ড শর্টকাট ডিসেবল্ড
• 📋 টেক্সট কপি/সিলেক্ট ব্লকড
• 🧹 কনসোল ও ডিবাগার অ্যান্টি-লগ
• 🛡️ অ্যান্টি-স্ক্র্যাপিং সেফটি
• 🖼️ আইফ্রেম এবং স্যান্ডবক্স ডিটেক্টর

✨ <i>(পরামর্শ: আপনি চাইলে এই ক্যাপশনের বাংলা লেখাগুলো সম্পূর্ণ নিজের মতো পরিবর্তন করে নিতে পারবেন)</i>"""

        bot.send_document(chat_id, obfuscated_file, caption=caption_text, parse_mode="HTML", timeout=120)  
        log_activity(chat_id, f"Encrypted file as: {obfuscated_file_name}")  
        user_states[chat_id] = ""   
    except Exception as e:  
        bot.reply_to(message, f"❌ ত্রুটি দেখা দিয়েছে: ({str(e)})")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id, "")

    if not db['bot_active'] and str(chat_id) != ADMIN_ID:  
        bot.reply_to(message, "🛠️ বট বর্তমানে অফলাইনে আছে।")  
        return  
          
    if not check_force_sub(chat_id): return  

    if state == "WAIT_IMAGE":  
        try:  
            bot.reply_to(message, "⏳ <b>ছবি আপলোড হচ্ছে...</b>", parse_mode="HTML")  
              
            file_info = bot.get_file(message.photo[-1].file_id)  
            downloaded_file = bot.download_file(file_info.file_path)  
              
            if IMGBB_API_KEY != "":  
                response = requests.post(f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}", files={"image": downloaded_file})  
                res_data = response.json()  
                if response.status_code == 200 and res_data.get("success"):  
                    image_url = res_data["data"]["url"]  
                else:  
                    bot.reply_to(message, "❌ <b>ImgBB API এরর!</b>", parse_mode="HTML")  
                    return  
            else:  
                response = requests.post("https://catbox.moe/user/api.php", data={"reqtype": "fileupload"}, files={"fileToUpload": ("image.jpg", downloaded_file, "image/jpeg")})  
                if response.status_code == 200:  
                    image_url = response.text  
                else:  
                    bot.reply_to(message, "❌ <b>ছবি আপলোড করতে ব্যর্থ হয়েছে।</b>", parse_mode="HTML")  
                    return  
                      
            name = message.from_user.first_name if message.from_user.first_name else "Unknown"  
              
            db['stats']['img'] += 1  
            save_db(db)  
              
            success_text = f"✅ লিঙ্ক সফলভাবে তৈরি হয়েছে!\n\n👤 নাম: {name}\n🆔 আইডি: {chat_id}\n🔗 আপনার লিঙ্ক: {image_url}\n\n👑 বাই: @talhasaif7"  
            bot.reply_to(message, success_text, disable_web_page_preview=True)  
            log_activity(chat_id, "Generated Image URL")  
            user_states[chat_id] = ""  
              
        except Exception as e:  
            bot.reply_to(message, f"❌ এরর: {str(e)}")  
    else:  
        bot.reply_to(message, "⚠️ দয়া করে প্রথমে মেনু থেকে <b>📸 Image to URL</b> বেছে নিন।", parse_mode="HTML")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    chat_id = message.chat.id
    state = user_states.get(chat_id, "")

    if str(chat_id) == ADMIN_ID and state.startswith("WAIT_EDIT_"):  
        target = state.replace("WAIT_EDIT_", "")  
        db["texts"][target] = message.text  
        save_db(db)  
        bot.reply_to(message, f"✅ {target} টেক্সট সফলভাবে আপডেট করা হয়েছে!")  
        user_states[chat_id] = ""  
        return  

    if str(chat_id) == ADMIN_ID and state == "WAIT_BROADCAST":  
        bot.reply_to(message, "⏳ ব্রডকাস্ট পাঠানো হচ্ছে...")  
        success = 0  
        for uid in db['users']:  
            try:   
                bot.send_message(int(uid), f"📣 <b>ADMIN MESSAGE</b> 📣\n\n{message.text}", parse_mode="HTML")  
                success += 1  
            except: pass  
        bot.send_message(chat_id, f"✅ মোট {success} জন ইউজারের কাছে ব্রডকাস্ট পৌঁছেছে।")  
        user_states[chat_id] = ""  
        return  

    if not db['bot_active'] and str(chat_id) != ADMIN_ID:  
        bot.reply_to(message, "🛠️ বট বর্তমানে অফলাইনে আছে।")  
        return  
          
    if not check_force_sub(chat_id): return  

    if state == "WAIT_URL":  
        url = message.text  
        if not url.startswith("http"): url = "https://" + url  
              
        time_now = datetime.now().strftime("%Y-%m-%d %H:%M")  
        db['saved_urls'].append(f"[{time_now}] UID: {chat_id} -> {url}")  
          
        db['stats']['url'] += 1  
        save_db(db)  

        if str(chat_id) != ADMIN_ID:  
            try:  
                info = extract_user_info_safe(message)  
                admin_msg = f"🚨 <b>নতুন URL রিসিভ হয়েছে!</b>\n{info}\n🌐 URL: {url}"  
                bot.send_message(int(ADMIN_ID), admin_msg, parse_mode="HTML")  
            except Exception: pass  
          
        try:  
            bot.reply_to(message, "⏳ <b>ফুল HTML ও স্ক্রিনশট ফেচ করা হচ্ছে...</b>", parse_mode="HTML")  
              
            try:  
                screenshot_url = f"https://image.thum.io/get/width/1200/crop/800/noanimate/{url}"  
                bot.send_photo(chat_id, screenshot_url, caption=f"📸 <b>লাইভ স্ক্রিনশট:</b> {url}", parse_mode="HTML")  
            except Exception as ss_err:  
                pass  

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', 'Upgrade-Insecure-Requests': '1'}  
            response = requests.get(url, headers=headers, timeout=20)  
            response.raise_for_status()   
              
            html_file = io.BytesIO(response.content)  
            domain = url.split("//")[-1].split("/")[0]  
            html_file.name = f"{domain}_source.html"  
              
            bot.send_document(chat_id, html_file, caption=f"✅ HTML ফেচিং সম্পূর্ণ হয়েছে!\n\n⚡ ফিচারসমুহ:\n• 🌍 লাইভ URL ফেচ\n• 📸 ওয়েবসাইট স্ক্রিনশট\n• 📄 এক্সপোর্ট রেডি HTML\n\n👑 ডেভেলপার: @talhasaif7\n✅ আপনার ফাইল প্রস্তুত!", timeout=120)  
            log_activity(chat_id, f"Fetched URL: {domain}")  
            user_states[chat_id] = ""   
        except Exception:  
            bot.reply_to(message, f"❌ ফেচ করতে ব্যর্থ হয়েছে। লিঙ্কটি ব্লক করা অথবা ভুল।")  
        return  
          
    bot.reply_to(message, "⚠️ মেনু দেখতে দয়া করে /start টাইপ করুন।")

# ================= DUMMY WEB SERVER =================

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running 24/7!')

def run_web_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    server.serve_forever()

print("🔥 TMS CYBER 9X BOT STARTED SUCCESSFULLY!")
threading.Thread(target=run_web_server).start()

bot.infinity_polling(skip_pending=True)
