import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ ሲስተም", page_icon="🏢", layout="wide")

# --- 1. CSS (ለዲዛይን) ---
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    h1, h2, h3 { color: #1e3d59 !important; font-weight: 800 !important; }
    .header-box { background-color: #f1f4f9; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; margin-bottom: 20px; }
    .stButton > button { width: 100%; border-radius: 6px; height: 3em; background-color: #007bff; color: white; font-weight: bold; }
    [data-testid="stSidebar"] { background-image: linear-gradient(#1e3d59, #17252a); color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ዳታ መጫኛ (Staff List) ---
@st.cache_data(ttl=0)
def load_staff_list():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        # በጎግል ሺትህ ላይ ስሙ StaffList የሆነውን ገጽ ያነባል
        staff_data = conn.read(worksheet="StaffList", ttl=0)
        
        if not staff_data.empty:
            # በሺቱ ላይ ያለውን 'ID' ወደ 'Employee_ID'፣ 'Name'ን ወደ 'Full Name' ይቀይራል
            staff_data = staff_data.rename(columns={'ID': 'Employee_ID', 'Name': 'Full Name'})
            return staff_data
        return pd.DataFrame(columns=['Employee_ID', 'Full Name'])
    except Exception as e:
        st.error(f"ከሰራተኛ ዝርዝር ጋር መገናኘት አልተቻለም: {e}")
        return pd.DataFrame(columns=['Employee_ID', 'Full Name'])

# የጎግል ሺት ግንኙነት ለሁሉም ገጽ
conn = st.connection("gsheets", type=GSheetsConnection)
staff_df = load_staff_list()

# --- የጎን ማውጫ ---
with st.sidebar:
    st.markdown("<div style='text-align: center;'><span style='font-size: 30px; font-weight: bold; color: #00d4ff;'>🏢 ሲስተም ሜኑ</span></div>", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("ገጽ ይምረጡ", ["🏠 የሰራተኞች መሙያ", "🔐 የማናጀር ገጽ", "📊 ዳሽቦርድ"])
    st.markdown("---")
    st.info("📅 February 2026 | Version 2.0")

# --- ገጽ 1: የሰራተኞች መሙያ ---
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<div class='header-box'><h1>📝 የአቴንዳንስ እና የፈቃድ መሙያ</h1></div>", unsafe_allow_html=True)
    
    emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (Employee ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
    
    if emp_id:
        # ሰራተኛው በዝርዝሩ ውስጥ መኖሩን ማረጋገጥ
        is_valid = emp_id in staff_df['Employee_ID'].astype(str).values
        
        if is_valid:
            staff_name = staff_df[staff_df['Employee_ID'].astype(str) == emp_id]['Full Name'].values[0]
            st.success(f"ሰላም {staff_name}! እባክዎ የቀሩበትን ወይም የፈቃድ ዝርዝር ይሙሉ")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("ከቀን", value=date.today())
                start_time = st.time_input("ከሰዓት")
            with col2:
                end_date = st.date_input("እስከ ቀን", value=date.today())
                end_time = st.time_input("እስከ ሰዓት")

            reason = st.selectbox("የጥያቄው አይነት", ["ህመም", "ዓመታዊ ፈቃድ", "ቤተሰብ ጉዳይ", "ልዩ ፈቃድ", "ሌላ"])
            details = st.text_area("ዝርዝር መግለጫ (አስፈላጊ ከሆነ)")

            if st.button("🚀 ጥያቄውን መዝግብ"):
                current_start = datetime.combine(start_date, start_time)
                current_end = datetime.combine(end_date, end_time)
                
                if current_start >= current_end:
                    st.error("❌ ስህተት፦ መነሻ ሰዓት ከመድረሻ ሰዓት ቀደም ማለት አለበት!")
                else:
                    # 'Sheet1' (Attendance) ዳታ ማንበብ
                    all_data = conn.read(worksheet="Sheet1", ttl=0)
                    
                    # አዲስ መዝገብ ማዘጋጀት
                    new_row = pd.DataFrame([{
                        "Full Name": staff_name,
                        "ID": emp_id,
                        "Reason": reason,
                        "Details": details,
                        "Status": "Pending",
                        "Remark": "",
                        "Date": start_date.strftime('%Y-%m-%d'),
                        "Start_Time": start_time.strftime('%H:%M:%S'),
                        "End_Time": end_time.strftime('%H:%M:%S'),
                        "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }])
                    
                    updated_df = pd.concat([all_data, new_row], ignore_index=True)
                    conn.update(worksheet="Sheet1", data=updated_df)
                    st.balloons()
                    st.success("✅ የፈቃድ ጥያቄዎ በትክክል ተመዝግቧል!")
        else:
            st.error("❌ የሰራተኛ መለያ ቁጥር አልተገኘም! እባክዎ በትክክል ያስገቡ።")

# --- ገጽ 2: የማናጀር ገጽ ---
elif page == "🔐 የማናጀር ገጽ":
    st.markdown("<h1>🔐 የአስተዳዳሪ መቆጣጠሪያ</h1>", unsafe_allow_html=True)
    admin_password = st.text_input("የአስተዳዳሪ ፓስወርድ ያስገቡ", type="password")
    
    if admin_password == st.secrets.get("admin_password", "1234"):
        df = conn.read(worksheet="Sheet1", ttl=0)
        if not df.empty:
            pending = df[df['Status'] == 'Pending']
            st.subheader(f"📬 የሚጠባበቁ ጥያቄዎች ({len(pending)})")
            
            for index, row in pending.iterrows():
                with st.expander(f"👤 {row['Full Name']} - {row['Reason']}"):
                    st.write(f"**መለያ:** {row['ID']} | **ቀን:** {row['Date']}")
                    st.write(f"**ዝርዝር:** {row['Details']}")
                    rem = st.text_input("ማሳሰቢያ (Remark)", key=f"rem_{index}")
                    c1, c2 = st.columns(2)
                    if c1.button("✅ አጽድቅ", key=f"app_{index}"):
                        df.at[index, 'Status'] = 'Approved'
                        df.at[index, 'Remark'] = rem
                        conn.update(worksheet="Sheet1", data=df)
                        st.rerun()
                    if c2.button("❌ ሰርዝ", key=f"rej_{index}"):
                        df.at[index, 'Status'] = 'Cancelled'
                        df.at[index, 'Remark'] = rem
                        conn.update(worksheet="Sheet1", data=df)
                        st.rerun()
        else:
            st.info("ምንም ዳታ የለም።")
    elif admin_password:
        st.error("❌ የተሳሳተ ፓስወርድ!")

# --- ገጽ 3: ዳሽቦርድ ---
elif page == "📊 ዳሽቦርድ":
    st.markdown("<h1>📊 የክትትል ዳሽቦርድ</h1>", unsafe_allow_html=True)
    df = conn.read(worksheet="Sheet1", ttl=0)
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("ጠቅላላ ጥያቄ", len(df))
        col2.metric("የጸደቁ ✅", len(df[df['Status'] == 'Approved']))
        col3.metric("በሂደት ላይ ⏳", len(df[df['Status'] == 'Pending']))
        st.plotly_chart(px.pie(df, names='Reason', title='የፈቃድ/የመቅረት ምክንያቶች'), use_container_width=True)
    else:
        st.info("ዳታ አልተገኘም።")
