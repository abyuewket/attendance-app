import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ", page_icon="🏢", layout="wide")

# --- 1. ደማቅ እና ግልጽ የሆኑ ቀለሞች (CSS) ---
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #111b21 !important;
        background-image: linear-gradient(#111b21, #1e3d59) !important;
    }
    .sidebar-title {
        color: #00d4ff !important;
        font-size: 28px !important;
        font-weight: 800 !important;
        text-align: center;
        padding: 20px 0px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .stApp { background-color: #ffffff; }
    .header-box {
        background-color: #f0f7ff;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #007bff;
        margin-bottom: 30px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    }
    .header-box h1 { color: #1e3d59 !important; margin: 0; font-weight: 800 !important; }
    label { color: #2c3e50 !important; font-weight: 600 !important; font-size: 1.1rem !important; }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.8em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0px 5px 15px rgba(0, 123, 255, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ዳታ መጫኛ ---
@st.cache_data(ttl=0)
def load_staff_list():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        staff_data = conn.read(worksheet="StaffList", ttl=0)
        if not staff_data.empty:
            staff_data = staff_data.rename(columns={'ID': 'Employee_ID', 'Name': 'Full Name'})
            return staff_data
    except:
        pass
    return pd.DataFrame(columns=['Employee_ID', 'Full Name'])

conn = st.connection("gsheets", type=GSheetsConnection)
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
        # ID ፍለጋ (ሁለቱንም ወደ String በመቀየር)
        is_valid = str(emp_id).split('.')[0] in staff_df['Employee_ID'].astype(str).str.split('.').str[0].values
        
        if is_valid:
            staff_name = staff_df[staff_df['Employee_ID'].astype(str).str.contains(str(emp_id).split('.')[0])]['Full Name'].values[0]
            st.info(f"👤 ሰራተኛ፦ **{staff_name}**")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("መነሻ ቀን", value=date.today())
                start_time = st.time_input("መነሻ ሰዓት")
            with col2:
                end_date = st.date_input("መመለሻ ቀን", value=date.today())
                end_time = st.time_input("መመለሻ ሰዓት")

            reason = st.selectbox("የጥያቄው ምክንያት", ["ህመም", "ዓመታዊ ፈቃድ", "ቤተሰብ ጉዳይ", "ልዩ ፈቃድ", "ሌላ"])
            details = st.text_area("ዝርዝር መግለጫ (አስፈላጊ ከሆነ)")

            if st.button("🚀 ጥያቄውን መዝግብ"):
                current_start = datetime.combine(start_date, start_time)
                current_end = datetime.combine(end_date, end_time)
                
                if current_start >= current_end:
                    st.error("❌ ስህተት፦ መነሻ ሰዓት ከመድረሻ ሰዓት ቀደም ማለት አለበት!")
                else:
                    all_data = conn.read(worksheet="Sheet1", ttl=0)
                    is_duplicate = False
                    conflict_info = ""

                    if not all_data.empty:
                        # የጊዜ መደራረብ ፍተሻ
                        user_records = all_data[all_data['ID'].astype(str).str.contains(str(emp_id).split('.')[0])]
                        for _, record in user_records.iterrows():
                            try:
                                if str(record['Status']) == "Cancelled": continue
                                r_date, r_start, r_end = str(record['Date']), str(record['Start_Time']), str(record['End_Time'])
                                prev_start = datetime.strptime(f"{r_date} {r_start}", '%Y-%m-%d %H:%M:%S')
                                prev_end = datetime.strptime(f"{r_date} {r_end}", '%Y-%m-%d %H:%M:%S')
                                
                                if current_start < prev_end and current_end > prev_start:
                                    is_duplicate = True
                                    conflict_info = f"{r_date} ({r_start} - {r_end})"
                                    break
                            except: continue

                    if is_duplicate:
                        st.markdown(f'<div style="background-color: #ff4b4b; color: white; padding: 15px; border-radius: 10px; text-align: center;">⚠️ ጥያቄው አልተመዘገበም! ሰራተኛው በ {conflict_info} ሰዓት ውስጥ ጥያቄ አቅርቧል።</div>', unsafe_allow_html=True)
                    else:
                        new_row = pd.DataFrame([{"Full Name": staff_name, "ID": emp_id, "Reason": reason, "Details": details if details else "ዝርዝር አልተገለጸም", "Status": "Pending", "Remark": "", "Date": start_date.strftime('%Y-%m-%d'), "Start_Time": start_time.strftime('%H:%M:%S'), "End_Time": end_time.strftime('%H:%M:%S'), "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}])
                        conn.update(worksheet="Sheet1", data=pd.concat([all_data, new_row], ignore_index=True))
                        st.balloons()
                        st.success("✅ ጥያቄው በትክክል ተመዝግቧል!")
        else:
            st.markdown('<div style="background-color: #ffe5e5; color: #d8000c; padding: 20px; border-radius: 12px; border: 2px solid #d8000c; text-align: center; font-weight: bold;">❌ ይህ መለያ ቁጥር ከሰራተኞች ዝርዝር የለም!! መለያ ቁጥሩን በትክክል ያስገቡ!!!</div>', unsafe_allow_html=True)

# --- ገጽ 2: የማናጀር ገጽ ---
elif page == "🔐 የማናጀር ገጽ":
    st.markdown("<div class='header-box'><h1>🔐 የአስተዳዳሪ መቆጣጠሪያ</h1></div>", unsafe_allow_html=True)
    admin_password = st.text_input("የአስተዳዳሪ ፓስወርድ ያስገቡ", type="password")
