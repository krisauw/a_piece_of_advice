# Streamlit version of "A Piece of Advice"
import json, random, math, colorsys, os
from datetime import datetime
from pathlib import Path
import streamlit as st

# ----- safety guard: require Streamlit runner -----
try:
    from streamlit.runtime.scriptrun_context import get_script_run_ctx
    if get_script_run_ctx() is None:
        raise SystemExit(
            "This file is a Streamlit app. Start it with:\n"
            "  streamlit run streamlit/piece_of_advice_app.py"
        )
except Exception:
    # Older/newer Streamlit versions may not have get_script_run_ctx – ignore.
    pass
# --------------------------------------------------

# ----------------------- Paths -----------------------
APP_DIR = Path(__file__).resolve().parent
DATA_FILE = APP_DIR / "advice_data.json"         # your existing Kivy JSON can stay as-is
CUSTOM_FILE = APP_DIR / "custom_advices.json"    # optional local persistence

# ----------------------- Palette helpers (to keep your vibe) -----------------------
PALETTE = {
    "teal":      (0.2941, 0.6824, 0.7804, 1),
    "cyan":      (0.2157, 0.7490, 0.8000, 1),
    "off_white": (0.8784, 0.9333, 0.9373, 1),
    "peach":     (0.9529, 0.7098, 0.5216, 1),
    "orange":    (0.9137, 0.5451, 0.3569, 1),
}
def desaturate_rgba(rgba, factor=0.5):
    r,g,b,a = rgba
    h,s,v = colorsys.rgb_to_hsv(r,g,b); s *= factor
    r2,g2,b2 = colorsys.hsv_to_rgb(h,s,v); return (r2,g2,b2,a)

def darken_rgba(rgba, factor=0.9):
    r,g,b,a = rgba
    h,s,v = colorsys.rgb_to_hsv(r,g,b); v *= factor
    r2,g2,b2 = colorsys.hsv_to_rgb(h,s,v); return (r2,g2,b2,a)

P = {k: darken_rgba(desaturate_rgba(v, 0.5), 0.9) for k, v in PALETTE.items()}
BACKGROUND = P["teal"]

# Convert rgba 0..1 to hex for Streamlit theme bits
def rgba_to_hex(rgba):
    r,g,b,_ = rgba
    return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))

# ----------------------- Built-in fallback DB -----------------------
DEFAULT_DB = {
    "life": [
        "Every day is a new opportunity to grow and become better.",
        "Your struggles today are building your strength for tomorrow.",
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "You are never too old to set another goal or to dream a new dream.",
        "Life is 10% what happens to you and 90% how you react to it.",
        "The only way to do great work is to love what you do.",
        "Success is not final, failure is not fatal: it is the courage to continue that counts.",
        "Believe you can and you're halfway there.",
        "The future belongs to those who believe in the beauty of their dreams.",
        "Don't watch the clock; do what it does. Keep going.",
    ],
    "love": [
        "Love yourself first and everything else falls into line.",
        "The best love is the kind that awakens the soul and makes us reach for more.",
        "Love is not about how much you say 'I love you', but how much you prove it's true.",
        "A successful marriage requires falling in love many times, always with the same person.",
        "The greatest thing you'll ever learn is just to love and be loved in return.",
        "Love is composed of a single soul inhabiting two bodies.",
        "Being deeply loved by someone gives you strength, while loving someone deeply gives you courage.",
        "Love is when the other person's happiness is more important than your own.",
        "The best and most beautiful things in the world cannot be seen or even touched - they must be felt with the heart.",
        "True love stories never have endings.",
    ],
    "family": [
        "Family is not an important thing. It's everything.",
        "The family is one of nature's masterpieces.",
        "A happy family is but an earlier heaven.",
        "Family means no one gets left behind or forgotten.",
        "The love of a family is life's greatest blessing.",
        "Family is where life begins and love never ends.",
        "In family life, love is the oil that eases friction, the cement that binds closer together.",
        "A family is a place where minds come in contact with one another.",
        "The family is the first essential cell of human society.",
        "Family is the most important thing in the world.",
    ],
    "career": [
        "Choose a job you love, and you will never have to work a day in your life.",
        "Success is not about the destination, it's about the journey.",
        "Your work is going to fill a large part of your life, so make sure it's something you love.",
        "The only way to do great work is to love what you do.",
        "Don't be afraid to give up the good to go for the great.",
        "Success is walking from failure to failure with no loss of enthusiasm.",
        "The way to get started is to quit talking and begin doing.",
        "Innovation distinguishes between a leader and a follower.",
        "Your limitation—it's only your imagination.",
        "Great things never come from comfort zones.",
    ],
    "healing": [
        "Healing is not about moving on or getting over it, it's about learning to carry it with you.",
        "You are allowed to feel your feelings. You are allowed to take your time to heal.",
        "Healing is an art. It takes time, it takes practice, it takes love.",
        "The wound is the place where the Light enters you.",
        "Healing doesn't mean the damage never existed. It means the damage no longer controls your life.",
        "You are not broken. You are becoming.",
        "Healing is not linear. It's okay to have setbacks.",
        "Your pain is valid. Your healing is valid. Your journey is valid.",
        "Sometimes the strongest people are the ones who love beyond the faults, cry behind closed doors, and fight battles that nobody knows about.",
        "Healing takes time, and asking for help is a courageous step.",
    ],
    "friendship": [
        "A true friend is someone who is there for you when they'd rather be anywhere else.",
        "Friendship is the only cement that will ever hold the world together.",
        "A friend is someone who knows all about you and still loves you.",
        "True friendship comes when the silence between two people is comfortable.",
        "Friends are the family you choose.",
        "A real friend is one who walks in when the rest of the world walks out.",
        "Friendship is born at that moment when one person says to another: 'What! You too? I thought I was the only one.'",
        "The best mirror is an old friend.",
        "Friendship is the golden thread that ties the heart of all the world.",
        "A friend is someone who gives you total freedom to be yourself.",
    ],
    "relationship": [
        "The best relationships are built on mutual respect, trust, and communication.",
        "A great relationship is about two things: first, finding out the similarities, second, respecting the differences.",
        "The best relationship is when you can act like lovers and best friends at the same time.",
        "A healthy relationship will never require you to sacrifice your friends, your dreams, or your dignity.",
        "The best relationships are the ones that make you a better person without changing who you are.",
        "Love is not about finding the perfect person, but about finding someone who makes you want to be perfect.",
        "The best relationships are built on a foundation of friendship.",
        "A successful relationship requires falling in love many times, always with the same person.",
        "The best relationships are the ones that make you feel good about yourself.",
        "True love is not about finding someone perfect, but about finding someone who makes you want to be perfect.",
    ],
}

@st.cache_data
def load_default_pool():
    # Build a 365-length pool (like your Kivy version)
    cats = list(DEFAULT_DB.keys())
    pool = []
    idx = 0
    for _ in range(365):
        cat = cats[idx % len(cats)]
        lst = DEFAULT_DB[cat]
        j = (_ // len(cats)) % len(lst)
        pool.append(lst[j])
        idx += 1
    return pool

# ----------------------- Load your Kivy JSON OR flat JSON -----------------------
@st.cache_data
def load_initial_advices():
    """
    Accepts three formats:
    A) Kivy JsonStore: {"advices":{"data":{"all_advices":[...], "custom_advices":[...]}}}
    B) Flat dict:      {"all_advices":[...], "custom_advices":[...]}
    C) Simple list:    ["a", "b", ...]
    """
    if DATA_FILE.exists():
        try:
            with DATA_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                # A) Kivy JsonStore
                node = data.get("advices", {}).get("data")
                if isinstance(node, dict) and "all_advices" in node:
                    return node.get("all_advices", []), node.get("custom_advices", [])

                # B) Flat dict
                if "all_advices" in data:
                    return data.get("all_advices", []), data.get("custom_advices", [])

            # C) Simple list
            if isinstance(data, list):
                return data, []
        except Exception:
            pass

    # Fallback if file missing/bad: synthesize from DEFAULT_DB
    return load_default_pool(), []

def load_custom_advices_local():
    # Local persistence (on Streamlit Cloud this may reset on redeploy)
    try:
        if CUSTOM_FILE.exists():
            with CUSTOM_FILE.open("r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_custom_advices_local(custom_list):
    try:
        with CUSTOM_FILE.open("w", encoding="utf-8") as f:
            json.dump(custom_list, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

# ----------------------- App state -----------------------
if "custom_advices" not in st.session_state:
    base, custom_from_data = load_initial_advices()
    st.session_state["base_advices"] = base
    custom_local = load_custom_advices_local()
    st.session_state["custom_advices"] = (custom_from_data or []) + (custom_local or [])
if "current_advice" not in st.session_state:
    st.session_state["current_advice"] = ""

# ----------------------- Page config & simple theming -----------------------
st.set_page_config(page_title="A Piece of Advice", page_icon="💡", layout="centered")
st.markdown(
    f"""
    <style>
      .stApp {{
        background: linear-gradient(135deg, {rgba_to_hex(BACKGROUND)} 0%, #0f172a 100%);
        color: {rgba_to_hex(P["off_white"])};
      }}
      .big-title {{
        font-size: 42px; font-weight: 800; text-align:center; margin-top: 8px;
      }}
      .advice {{
        font-size: 24px; text-align:center; padding: 14px 18px; border-radius: 12px;
        background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="big-title">💡 A Piece of Advice</div>', unsafe_allow_html=True)
st.write("")

# ----------------------- Sidebar = Settings (visual only) -----------------------
with st.sidebar:
    st.header("Settings")
    st.selectbox("Notification Time (visual only)",
                 ["6:00 AM","7:00 AM","8:00 AM","9:00 AM","10:00 AM",
                  "11:00 AM","12:00 PM","1:00 PM","2:00 PM","3:00 PM",
                  "4:00 PM","5:00 PM","6:00 PM","7:00 PM","8:00 PM"],
                 index=2)
    st.multiselect("Notification Days (visual only)",
                   ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
                   default=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"])
    if st.button("Test Notification (toast)"):
        st.toast("🔔 This is a test notification!", icon="💡")

# ----------------------- Main controls -----------------------
col1, col2, col3 = st.columns([1,1,1])

with col1:
    if st.button("Get Today's Advice"):
        pool = st.session_state["base_advices"] + st.session_state["custom_advices"]
        if pool:
            st.session_state["current_advice"] = random.choice(pool)
        else:
            st.warning("No advice available. Your JSON might be empty.")

with col2:
    with st.popover("Share / Copy"):
        if st.session_state["current_advice"]:
            share_text = f"\"{st.session_state['current_advice']}\"\n\n— From A Piece of Advice"
            st.code(share_text, language=None)
            st.download_button("Download as .txt", data=share_text.encode("utf-8"),
                               file_name="advice.txt")
        else:
            st.write("Get an advice first 🙂")

with col3:
    with st.popover("Add My Advice"):
        new_adv = st.text_area("Your advice", placeholder="Enter something uplifting…")
        if st.button("Save Advice"):
            txt = (new_adv or "").strip()
            if txt:
                st.session_state["custom_advices"].append(txt)
                _ = save_custom_advices_local(st.session_state["custom_advices"])
                st.success("Saved! (Session saved; local file updated if possible)")
            else:
                st.warning("Please enter some advice text.")

st.write("")
if st.session_state["current_advice"]:
    st.markdown(f'<div class="advice">“{st.session_state["current_advice"]}”</div>', unsafe_allow_html=True)
else:
    st.info("Tap **Get Today's Advice** to receive your daily motivation.")

# Optional: browse all
with st.expander("Browse all advices"):
    all_list = st.session_state["base_advices"] + st.session_state["custom_advices"]
    for i, a in enumerate(all_list, start=1):
        st.write(f"**{i}.** {a}")

st.caption(f"Last opened: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
