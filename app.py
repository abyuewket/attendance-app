import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ", page_icon="🏢", layout="wide")

# --- 1. CSS Styles ---
st.markdown("""
    <style>
    /* 1. ጠቅላላ ገጽታ */
    .stApp {
        background-color: #f8faff;
    }

    /* 2. የግራ ማውጫ (Sidebar) ዲዛይን */
    [data-testid="stSidebar"] {
        background-color: #111b21 !important;
        background-image: linear-gradient(180deg, #111b21 0%, #1e3d59 100%) !important;
        border-right: 1px solid #00d4ff;
    }
    
    /* በSidebar ውስጥ ያሉት የሬዲዮ በተኖች */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: rgba(255, 255, 255, 0.05);
        margin: 10px 0px;
        padding: 15px !important;
        border-radius: 12px;
        border: 1px solid transparent;
        transition: 0.3s all;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        background-color: rgba(0, 212, 255, 0.1);
        border: 1px solid #00d4ff;
    }

    /* 3. የአርዕስት ሳጥን (Header Box) */
    .header-box {
        background: linear-gradient(90deg, #1e3d59 0%, #007bff 100%);
        padding: 30px;
        border-radius: 20px;
        color: white !important;
        text-align: center;
        margin-bottom: 35px;
        box-shadow: 0px 10px 20px rgba(0, 123, 255, 0.2);
    }
    .header-box h1 {
        color: white !important;
        font-weight: 800 !important;
        letter-spacing: 1px;
    }

    /* 4. የማናጀር ገጽ ካርዶች (Request Cards) */
    .request-card {
        background-color: white;
        padding: 25px;
        border-radius: 18px;
        border: none;
        border-left: 10px solid #00d4ff;
        margin-bottom: 20px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.05);
        transition: 0.3s;
    }
    .request-card:hover {
        transform: translateY(-5px);
        box-shadow: 0px 12px 25px rgba(0,0,0,0.1);
    }

    /* 5. የዳሽቦርድ ሜትሪክስ (Metrics) */
    div[data-testid="stMetric"] {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.03);
        border-bottom: 4px solid #007bff;
    }

    /* 6. የጽሑፍ ግብዓቶች (Inputs) */
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #e0e0e0 !important;
        padding: 10px !important;
    }

    /* 7. ዋናው በተን (Button) */
    .stButton > button {
        background: linear-gradient(45deg, #007bff, #00d4ff);
        border: none;
        color: white;
        font-weight: bold;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0px 5px 15px rgba(0, 212, 255, 0.4);
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

# --- ገጽ 1: የሰራተኞች መሙያ ---
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<div class='header-box'><h1>📝 የፈቃድ መጠየቂያ ፎርም</h1></div>", unsafe_allow_html=True)
    emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
    
    if emp_id:
        # ID ንፅፅር (ሁለቱንም ወደ String በመቀየር)
        staff_ids = staff_df['Employee_ID'].astype(str).str.split('.').str[0].values
        clean_id = str(emp_id).split('.')[0]
        
        if clean_id in staff_ids:
            staff_row = staff_df[staff_df['Employee_ID'].astype(str).str.contains(clean_id)]
            staff_name = staff_row['Full Name'].values[0]
            st.info(f"👤 ሰራተኛ፦ **{staff_name}**")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("መነሻ ቀን", value=date.today())
                start_time = st.time_input("መነሻ ሰዓት", value=datetime.now().time())
            with col2:
                end_date = st.date_input("መመለሻ ቀን", value=date.today())
                end_time = st.time_input("መመለሻ ሰዓት", value=datetime.now().time())

            reason = st.selectbox("የጥያቄው ምክንያት", ["ህመም", "ዓመታዊ ፈቃድ", "ቤተሰብ ጉዳይ", "ልዩ ፈቃድ", "ሌላ"])
            details = st.text_area("ዝርዝር መግለጫ (አስፈላጊ ከሆነ)")

            if st.button("🚀 ጥያቄውን መዝግብ"):
                current_start = datetime.combine(start_date, start_time)
                current_end = datetime.combine(end_date, end_time)
                
                if current_start >= current_end:
                    st.error("❌ ስህተት፦ መነሻ ሰዓት ከመድረሻ ሰዓት ቀደም ማለት አለበት!")
                else:
                    try:
                        all_data = conn.read(worksheet="Sheet1", ttl=0)
                    except:
                        all_data = pd.DataFrame()

                    # Overlap Check
                    is_duplicate = False
                    if not all_data.empty and 'ID' in all_data.columns:
                        user_records = all_data[all_data['ID'].astype(str).str.contains(clean_id)]
                        for _, record in user_records.iterrows():
                            if str(record.get('Status')) == "Cancelled": continue
                            try:
                                r_date = str(record['Date'])
                                prev_s = datetime.strptime(f"{r_date} {record['Start_Time']}", '%Y-%m-%d %H:%M:%S')
                                prev_e = datetime.strptime(f"{r_date} {record['End_Time']}", '%Y-%m-%d %H:%M:%S')
                                if current_start < prev_e and current_end > prev_s:
                                    is_duplicate = True; break
                            except: continue

                    if is_duplicate:
                        st.markdown('<div style="background-color: #ff4b4b; color: white; padding: 15px; border-radius: 10px; text-align: center;">⚠️ ጥያቄው አልተመዘገበም! በዛ ሰዓት ሌላ ጥያቄ አለ።</div>', unsafe_allow_html=True)
                    else:
                        new_row = pd.DataFrame([{
                            "Full Name": staff_name, "ID": emp_id, "Reason": reason, 
                            "Details": details if details else "ዝርዝር የለም", "Status": "Pending", 
                            "Remark": "", "Date": start_date.strftime('%Y-%m-%d'), 
                            "Start_Time": start_time.strftime('%H:%M:%S'), 
                            "End_Time": end_time.strftime('%H:%M:%S'), 
                            "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }])
                        conn.update(worksheet="Sheet1", data=pd.concat([all_data, new_row], ignore_index=True))
                        st.balloons(); st.success("✅ ጥያቄው ተመዝግቧል!")
        else:
            st.error("❌ ይህ መለያ ቁጥር ከሰራተኞች ዝርዝር የለም!!")

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

