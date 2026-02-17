import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ", page_icon="🏢", layout="wide")
# 1. መጀመሪያ የገጽ አቀማመጥ (ይህ የግድ መጀመሪያ መሆን አለበት)
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ", page_icon="🏢", layout="wide")

# 2. ዲዛይኑ በሁሉም ብራውዘር እኩል እንዲታይ የሚያደርግ ኮድ
st.markdown("""
    <style>
    /* ሁሉንም ብራውዘር አንድ አይነት ቀለም እንዲጠቀሙ ማስገደድ (Force Uniform Colors) */
    :root {
        --primary-color: #00d4ff;
    }

    /* 1. የጎን ማውጫ (Sidebar) ጀርባ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111b21 0%, #1b263b 100%) !important;
        min-width: 300px !important;
    }

    /* 2. "ገጽ ይምረጡ" አርዕስት ካርድ */
    div[data-testid="stSidebar"] .stRadio > label {
        background: linear-gradient(90deg, #007bff, #00d4ff) !important;
        color: white !important;
        padding: 15px !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        font-size: 1.2rem !important;
        text-align: center !important;
        display: block !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* 3. የሬዲዮ ምርጫ ካርዶች (Menu Cards) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff !important;
        padding: 18px 20px !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        border: 2px solid transparent !important;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1) !important;
        transition: all 0.3s ease !important;
    }

    /* በካርዶቹ ውስጥ ያለውን ጽሑፍ በግልጽ ማሳያ (ለጓደኞችህ የጠፋው ይሄ ነው) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        color: #1e3d59 !important; /* ደማቅ ሰማያዊ ጽሑፍ */
        font-size: 1.05rem !important;
        font-weight: 600 !important;
        opacity: 1 !important;
    }

    /* የተመረጠው ካርድ (Active Card) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-selected="true"] {
        border: 3px solid #00d4ff !important;
        background-color: #f0faff !important;
        transform: scale(1.02);
    }

    /* 4. የዳሽቦርድ ሜትሪክስ ቁጥሮች (Metrics Fix) */
    [data-testid="stMetricValue"] {
        color: #1e3d59 !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: #555555 !important;
    }

    div[data-testid="stMetric"] {
        background-color: white !important;
        border-radius: 15px !important;
        padding: 15px !important;
        border-top: 5px solid #00d4ff !important;
        box-shadow: 0px 5px 15px rgba(0,0,0,0.05) !important;
    }

    /* የድሮውን ክብ ምልክት ማጥፋት */
    div[data-testid="stRadio"] div[role="radiogroup"] [data-testid="stWidgetSelectionStateIndicator"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
    <style>
    /* ከላይ የሰጠሁህን የ CSS ኮድ እዚህ ውስጥ ሙሉውን ኮፒ አድርገህ ጨምረው */
    [data-testid="stMetricValue"] {
        color: #1e3d59 !important;
        font-size: 2.5rem !important;
        font-weight: 800 !important;
    }
    /* ... የቀሩት የዲዛይን ኮዶች ... */
    </style>
    """, unsafe_allow_html=True)

# --- 1. CSS Styles ---
st.markdown("""
    <style>
    /* 1. የጎን ማውጫ (Sidebar) አጠቃላይ መልክ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1b2a 0%, #1b263b 100%) !important;
        border-right: 2px solid #00d4ff;
    }

    /* 2. "ገጽ ይምረጡ" የሚለውን ጽሑፍ ማሳመር */
    [data-testid="stSidebar"] .stRadio > label {
        color: #00d4ff !important;
        font-size: 20px !important;
        font-weight: bold !important;
        padding-bottom: 15px !important;
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }

    /* 3. የሬዲዮ በተኖቹን (Menu Items) ወደ ዘመናዊ ካርድ መቀየር */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(0, 212, 255, 0.2) !important;
        padding: 15px 20px !important;
        border-radius: 15px !important;
        margin-bottom: 12px !important;
        color: #e0e1dd !important;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) !important;
        display: flex !important;
        align-items: center !important;
    }

    /* አይጥን ሲያሳርፉበት (Hover) የሚፈጠር ለውጥ */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: rgba(0, 212, 255, 0.1) !important;
        border: 1px solid #00d4ff !important;
        transform: scale(1.05) !important;
        box-shadow: 0px 5px 15px rgba(0, 212, 255, 0.2) !important;
    }

    /* የተመረጠው ገጽ (Selected State) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-selected="true"] {
        background: linear-gradient(90deg, #007bff 0%, #00d4ff 100%) !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        box-shadow: 0px 10px 20px rgba(0, 123, 255, 0.4) !important;
    }

    /* 4. ዋናው ገጽ የላይኛው አርዕስት (Header) */
    .header-box {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        padding: 40px;
        border-radius: 30px;
        border: 1px solid rgba(0, 123, 255, 0.1);
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0px 20px 40px rgba(0, 0, 0, 0.05);
    }
    
    .header-box h1 {
        background: linear-gradient(90deg, #1e3d59, #007bff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        font-weight: 900 !important;
    }

    /* 5. የዳሽቦርድ ካርዶች */
    [data-testid="stMetric"] {
        background: white !important;
        border-radius: 20px !important;
        padding: 25px !important;
        border-top: 5px solid #00d4ff !important;
        box-shadow: 0px 10px 20px rgba(0,0,0,0.02) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ዳታ መጫኛ ---
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=0)
def load_staff_list():
    try:
        staff_data = conn.read(worksheet="StaffList", ttl=0)
        if not staff_data.empty:
            # የኮለም ስሞችን ማስተካከያ (ID እና Name ካሉ)
            if 'ID' in staff_data.columns: staff_data = staff_data.rename(columns={'ID': 'Employee_ID'})
            if 'Name' in staff_data.columns: staff_data = staff_data.rename(columns={'Name': 'Full Name'})
            return staff_data
    except Exception: pass
    return pd.DataFrame(columns=['Employee_ID', 'Full Name'])

staff_df = load_staff_list()

# --- 3. የጎን ማውጫ ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">🏢 ሲስተም ሜኑ</p>', unsafe_allow_html=True)
    page = st.radio("ገጽ ይምረጡ", ["🏠 የሰራተኞች መሙያ", "🔐 የማናጀር ገጽ", "📊 ዳሽቦርድ"])

# 1. የጌጥ (CSS) ክፍል
st.markdown("""
    <style>
    /* ጠቅላላ ገጹን እና Sidebarን ወደ ጥቁር ሰማያዊ መቀየር */
    .stApp, [data-testid="stSidebar"], [data-testid="stHeader"] {
        background-color: #0d1b2a !important;
    }

    /* የጎን ማውጫ "ገጽ ይምረጡ" አርዕስት */
    [data-testid="stSidebar"] .stRadio > label {
        color: #00d4ff !important;
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 10px 0px !important;
    }

    /* የገጽ መምረጫ ካርዶች (Menu Cards) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(0, 212, 255, 0.1) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        transition: 0.3s ease !important;
    }

    /* በካርዶቹ ውስጥ ያለው ጽሑፍ */
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        color: #ffffff !important;
        font-size: 17px !important;
        font-weight: 500 !important;
    }

    /* የተመረጠው ገጽ ምልክት (ቀይ ክብ) */
    div[data-testid="stRadio"] div[role="radiogroup"] [data-testid="stWidgetSelectionStateIndicator"] {
        background-color: #ff4b4b !important;
    }

    /* 📝 የፎርም ካርዶች (Input Grouping) */
    div[data-testid="column"] {
        background-color: rgba(255, 255, 255, 0.03);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 10px;
    }

    /* የኢንፑት ሌብሎች (Input Labels) */
    label p {
        color: #00d4ff !important;
        font-weight: bold !important;
        font-size: 1rem !important;
    }

    /* ዳሽቦርድ ሜትሪክስ */
    div[data-testid="stMetric"] {
        background-color: #ffffff !important;
        border-radius: 15px !important;
        padding: 20px !important;
        border-top: 6px solid #00d4ff !important;
    }
    
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #1e3d59 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. የፎርም አቀማመጥ ክፍል (በ ገጽ 1 ስር የሚገባ)
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<h1 style='text-align: center; color: white;'>📝 የፈቃድ መጠየቂያ ፎርም</h1>", unsafe_allow_html=True)
    
    emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
    
    if emp_id:
        # (ID Check ሎጂክ እዚህ ይገባል...)
        
        st.markdown("### 🕒 የጊዜ ሰሌዳ")
        
        # ቀንና ሰዓት በአንድ ካርድ ውስጥ (ጎን ለጎን)
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**📅 መነሻ (Start)**")
                start_date = st.date_input("መነሻ ቀን", label_visibility="collapsed")
                start_time = st.time_input("መነሻ ሰዓት", label_visibility="collapsed")
            
            with col2:
                st.markdown("**📅 መመለሻ (Return)**")
                end_date = st.date_input("መመለሻ ቀን", label_visibility="collapsed")
                end_time = st.time_input("መመለሻ ሰዓት", label_visibility="collapsed")

        # የኦቨርላፕ ቼክ እና የመመዝገቢያ በተን እዚህ ይቀጥላል...
# --- ገጽ 2: የማናጀር ገጽ ---
elif page == "🔐 የማናጀር ገጽ":
    st.markdown("<div class='header-box'><h1>🔐 የአስተዳዳሪ መቆጣጠሪያ</h1></div>", unsafe_allow_html=True)
    admin_password = st.text_input("የአስተዳዳሪ ፓስወርድ", type="password")
    
    if admin_password == st.secrets.get("admin_password", "1234"):
        try:
            df = conn.read(worksheet="Sheet1", ttl=0)
            if not df.empty and 'Status' in df.columns:
                pending = df[df['Status'] == 'Pending']
                st.subheader(f"📬 የሚጠባበቁ ጥያቄዎች ({len(pending)})")
                
                for idx, row in pending.iterrows():
                    with st.container():
                        st.markdown(f"""<div class="request-card"><b>👤 ሰራተኛ:</b> {row['Full Name']} (ID: {row['ID']})<br><b>📅 ቀን:</b> {row['Date']} ({row['Start_Time']} - {row['End_Time']})<br><b>❓ ምክንያት:</b> {row['Reason']}</div>""", unsafe_allow_html=True)
                        c_rem, c_acc, c_rej = st.columns([2, 1, 1])
                        rem = c_rem.text_input("ማሳሰቢያ", key=f"rem_{idx}")
                        if c_acc.button("✅ አጽድቅ", key=f"acc_{idx}"):
                            df.at[idx, 'Status'], df.at[idx, 'Remark'] = 'Approved', rem
                            conn.update(worksheet="Sheet1", data=df)
                            st.rerun()
                        if c_rej.button("❌ ሰርዝ", key=f"rej_{idx}"):
                            df.at[idx, 'Status'], df.at[idx, 'Remark'] = 'Cancelled', rem
                            conn.update(worksheet="Sheet1", data=df)
                            st.rerun()
            else: st.info("ምንም ጥያቄ የለም።")
        except Exception as e: st.error(f"ዳታ ማንበብ አልተቻለም፦ {e}")

# --- ገጽ 3: ዳሽቦርድ ---
elif page == "📊 ዳሽቦርድ":
    st.markdown("<div class='header-box'><h1>📊 የክትትል ዳሽቦርድ</h1></div>", unsafe_allow_html=True)
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
        if not df.empty and 'Status' in df.columns:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("ጠቅላላ", len(df))
            m2.metric("የጸደቁ", len(df[df['Status'] == 'Approved']))
            m3.metric("የተሰረዙ", len(df[df['Status'] == 'Cancelled']))
            m4.metric("በሂደት", len(df[df['Status'] == 'Pending']))
            
            c1, c2 = st.columns(2)
            if 'Reason' in df.columns:
                c1.plotly_chart(px.pie(df, names='Reason', title='በምክንያት'), use_container_width=True)
            c2.plotly_chart(px.bar(df, x='Status', color='Status', title='በሁኔታ'), use_container_width=True)
            
            st.markdown("### 📋 ዝርዝር መዝገቦች")
            st.dataframe(df, use_container_width=True)
        else: st.warning("ዳታው ባዶ ነው።")
    except Exception as e: st.error("ዳሽቦርዱን መጫን አልተቻለም።")





