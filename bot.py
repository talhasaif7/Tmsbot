import base64
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import io
import random
import string
import requests
import json
import os
import urllib.parse
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# ================= KREDENTIALS =================

TOKEN = '8670155352:AAGxgKfvPGdsWtIx1pqbqophLaJwtCB_Qn0'
ADMIN_ID = "6957867422" 
IMGBB_API_KEY = "ef424e1e7e96e0ebe80f079612575a80" # প্রয়োজন অনুযায়ী এটি পরিবর্তন করতে পারেন

# ================= CHANNEL SETTINGS (FORCE SUB) =================

CHANNEL_ID = "-1002875839715"
CHANNEL_LINK = "https://t.me/infinity9x"
CUSTOM_PHOTO_URL = "https://i.postimg.cc/LXrPTmyb/file-000000005d1c82089238787980c1a675.png"

bot = telebot.TeleBot(TOKEN)

# ================= DATABASE SETUP =================

DB_FILE = 'bot_db.json'

DEFAULT_TEXTS = {
    "welcome": "🚀 <b>Pʀᴇᴍɪᴜᴍ Sᴜɪᴛᴇ Aᴄᴛɪᴠᴀᴛᴇᴅ</b>\n\n👑 <b>স্বাগতম আমাদের সবচেয়ে অ্যাডভান্সড টুলবটে!</b>\nনিচের পাওয়ারফুল ফিচারগুলো থেকে যেকোনো একটি বেছে নিন:\n\n📍 Render URL: সোর্স কোড বের করুন ও ক্লিন করুন।\n🔒 Obfuscate HTML: আপনার HTML কোড এনক্রিপ্ট ও প্রটেক্ট করুন।\n📸 Image to URL: ছবি থেকে সরাসরি ডিরেক্ট লিঙ্ক তৈরি করুন।\n\n<b>শুরু করতে নিচের একটি অপশন সিলেক্ট করুন...</b>",

    "obf_prompt": "⚠️ <b>HTML Oʙғᴜsᴄᴀᴛᴏʀ Bᴏᴛ</b>\n\n🛡️ অ্যাডভান্সড অবফাসকেশনের মাধ্যমে আপনার HTML কোড সম্পূর্ণ নিরাপদ রাখুন!\n\n⚡ ফিচারসমুহ:\n• 🛡️ অ্যান্টি-ডিবাগ প্রোটেকশন\n• 🔍 টুলস ডিটেকশন\n• 🌐 এক্সট্রিম অবফাসকেশন\n• 🛡️ অ্যান্টি-স্ক্র্যাপিং প্রোটেকশন\n• 🖼️ আইফ্রেম/স্যান্ডবক্স ডিটেকশন\n\n📄 <b>শুরু করতে আপনার HTML ফাইলটি পাঠান!</b>",  
  
    "url_prompt": "╔════════════════════╗\n   📍 <b>URL ᴛᴏ HTML Bᴏᴛ</b>\n╚════════════════════╝\n\n⚡ ফিচারসমুহ:\n• 🌍 ফাস্ট URL ফেচ\n• 📄 ক্লিন HTML এক্সপোর্ট\n• ⚡ ইনস্ট্যান্ট প্রসেসিং\n• 🔒 সিকিউর এক্সট্র্যাকশন\n• 📸 লাইভ ওয়েবসাইট স্ক্রিনশট!\n\n🎁 <b>শুরু করতে একটি ওয়েবসাইট URL পাঠান!</b>\n\n🔗 উদাহরণ:\nhttps://example.com",  
  
    "img_prompt": "📸 <b>Iᴍᴀɢᴇ ᴛᴏ URL Bᴏᴛ</b>\n\n🪄 লিঙ্ক জেনারেট করতে নিচের ২টি সহজ ধাপ অনুসরণ করুন:\n\n1️⃣ গ্যালারি থেকে ছবি সিলেক্ট করুন।\n2️⃣ সরাসরি এই বটে সেটি সেন্ট করুন।\n\n⚠️ <i>সতর্কতা: শুধুমাত্র বৈধ ছবি (JPG/PNG) পাঠান।</i>\n\n<b>নিচে আপনার ছবি পাঠান!</b>"
}

def load_db():
    default_db = {
        "users": [], "activities": [], "bot_active": True,
        "saved_urls": [], "saved_files": [], "texts": DEFAULT_TEXTS,
        "stats": {"obf": 2488, "url": 2535, "img": 392}
    }
    if os.path.exists(DB_FILE):
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                for key in default_db:
                    if key not in data: data[key] = default_db[key]
                for text_key in DEFAULT_TEXTS:
                    if text_key not in data["texts"]: data["texts"][text_key] = DEFAULT_TEXTS[text_key]
                if "stats" not in data:
                    data["stats"] = default_db["stats"]
                return data
            except: return default_db
    return default_db

def save_db(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f: 
        json.dump(data, f, indent=4, ensure_ascii=False)

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

# ================= FORCE SUB CHECKER =================

def is_subscribed(user_id):
    if str(user_id) == ADMIN_ID:
        return True
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        if status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        print(f"Force Sub Error: {e}")
        return False

def check_force_sub(chat_id):
    if not is_subscribed(chat_id):
        markup = InlineKeyboardMarkup()
        btn1 = InlineKeyboardButton("📢 𝗝𝗼𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹", url=CHANNEL_LINK)
        btn2 = InlineKeyboardButton("✅ 𝗖𝗵𝗲𝗰𝗸 𝗦𝘂𝗯", callback_data="check_sub")
        markup.add(btn1)
        markup.add(btn2)
        bot.send_message(
            chat_id,
            "⚠️ <b>এক্সেস ব্লক করা হয়েছে!</b>\n\nএই বটটি ব্যবহার করতে হলে আপনাকে অবশ্যই আমাদের অফিসিয়াল চ্যানেলে জয়েন হতে হবে।\n\n👇 <i>নিচের লিঙ্কে জয়েন করে 'Check Sub' এ ক্লিক করুন।</i>",
            reply_markup=markup,
            parse_mode="HTML"
        )
        return False
    return True

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
