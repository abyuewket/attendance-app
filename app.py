import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ ሲስተም", page_icon="🏢", layout="wide")

# --- 1. የቀድሞውን ውበት የሚመልስ CSS ---
st.markdown("""
    <style>
    /* የጎን ማውጫ ጀርባ */
    [data-testid="stSidebar"] {
        background-color: #111b21 !important;
        background-image: linear-gradient(#111b21, #1e3d59) !important;
    }

    /* የጎን ማውጫ ጽሑፎች */
    .sidebar-title {
        color: #00d4ff !important;
        font-size: 30px !important;
        font-weight: bold !important;
        text-align: center;
        padding: 20px 0px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* ዋናው ገጽ ጀርባ */
    .stApp {
        background-color: #ffffff;
    }

    /* የአርዕስት ሳጥን (Header Box) */
    .header-box {
        background-color: #f1f4f9;
        padding: 20px;
        border-radius: 12px;
        border-left: 8px solid #007bff;
        margin-bottom: 25px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    }

    /* የቁልፍ (Button) ዲዛይን */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }

    /* የማናጀር ገጽ ካርዶች */
    .request-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin-bottom: 10px;
        color: #1e3d59 !important;
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
        return pd.DataFrame(columns=['Employee_ID', 'Full Name'])
    except Exception as e:
        return pd.DataFrame(columns=['Employee_ID', 'Full Name'])

conn = st.connection("gsheets", type=GSheetsConnection)
staff_df = load_staff_list()

# --- 3. የጎን ማውጫ ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">🏢 ሲስተም ሜኑ</p>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("ገጽ ይምረጡ", ["🏠 የሰራተኞች መሙያ", "🔐 የማናጀር ገጽ", "📊 ዳሽቦርድ"])
    st.markdown("---")
    st.markdown(f"""
        <div style='background-color: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px;'>
            <p style='margin:0; color: #38bdf8;'>📍 የኢትዮጵያ አቴንዳንስ</p>
            <p style='margin:0; color: #ffffff;'>📅 {date.today().strftime('%B %d, %Y')}</p>
            <p style='margin:0; color: #ffffff;'>🚀 Version 2.0</p>
        </div>
    """, unsafe_allow_html=True)

# --- ገጽ 1: የሰራተኞች መሙያ ---
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<div class='header-box'><h1>📝 የአቴንዳንስ መሙያ ፎርም</h1></div>", unsafe_allow_html=True)
    emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (Employee ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
    
    if emp_id:
        is_valid = emp_id in staff_df['Employee_ID'].astype(str).values
        if is_valid:
            staff_name = staff_df[staff_df['Employee_ID'].astype(str) == emp_id]['Full Name'].values[0]
            st.success(f"ሰላም {staff_name}! እባክዎ የቀሩበትን ዝርዝር በትክክል ይሙሉ")
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("ከቀን", value=date.today())
                start_time = st.time_input("ከሰዓት")
            with col2:
                end_date = st.date_input("እስከ ቀን", value=date.today())
                end_time = st.time_input("እስከ ሰዓት")

            reason = st.selectbox("የቀሩበት ምክንያት", ["ህመም", "ፈቃድ", "ቤተሰብ ጉዳይ", "ሌላ"])
            details = st.text_area("ዝርዝር መግለጫ")

            if st.button("🚀 ጥያቄውን መዝግብ"):
                all_data = conn.read(worksheet="Sheet1", ttl=0)
                new_row = pd.DataFrame([{
                    "Full Name": staff_name, "ID": emp_id, "Reason": reason,
                    "Details": details, "Status": "Pending", "Remark": "",
                    "Date": start_date.strftime('%Y-%m-%d'),
                    "Start_Time": start_time.strftime('%H:%M:%S'),
                    "End_Time": end_time.strftime('%H:%M:%S'),
                    "Timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }])
                updated_df = pd.concat([all_data, new_row], ignore_index=True)
                conn.update(worksheet="Sheet1", data=updated_df)
                st.balloons()
                st.success("✅ ጥያቄዎ ተመዝግቧል!")
        else:
            st.error("❌ የሰራተኛ መለያ ቁጥር አልተገኘም!")

# --- ገጽ 2: የማናጀር ገጽ ---
elif page == "🔐 የማናጀር ገጽ":
    st.markdown("<div class='header-box'><h1>🔐 የአስተዳዳሪ መቆጣጠሪያ</h1></div>", unsafe_allow_html=True)
    admin_password = st.text_input("የአስተዳዳሪ ፓስወርድ ያስገቡ", type="password")
    
    if admin_password == st.secrets.get("admin_password", "1234"):
        df = conn.read(worksheet="Sheet1", ttl=0)
        if not df.empty:
            pending = df[df['Status'] == 'Pending']
            st.subheader(f"📬 የሚጠባበቁ ጥያቄዎች ({len(pending)})")
            for index, row in pending.iterrows():
                st.markdown(f"""
                    <div class="request-card">
                        <b>👤 ሰራተኛ:</b> {row['Full Name']} | <b>❓ ምክንያት:</b> {row['Reason']}<br>
                        <b>📅 ቀን:</b> {row['Date']} | <b>📝 ዝርዝር:</b> {row['Details']}
                    </div>
                """, unsafe_allow_html=True)
                rem = st.text_input("ማሳሰቢያ", key=f"r_{index}")
                c1, c2 = st.columns(2)
                if c1.button("✅ አጽድቅ", key=f"a_{index}"):
                    df.at[index, 'Status'] = 'Approved'
                    df.at[index, 'Remark'] = rem
                    conn.update(worksheet="Sheet1", data=df)
                    st.rerun()
                if c2.button("❌ ሰርዝ", key=f"c_{index}"):
                    df.at[index, 'Status'] = 'Cancelled'
                    df.at[index, 'Remark'] = rem
                    conn.update(worksheet="Sheet1", data=df)
                    st.rerun()
    elif admin_password:
        st.error("❌ የተሳሳተ ፓስወርድ!")

# --- ገጽ 3: ዳሽቦርድ ---
# --- ገጽ 3: ዳሽቦርድ ---
elif page == "📊 ዳሽቦርድ":
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] { color: #007bff !important; font-weight: bold !important; }
        [data-testid="stMetricLabel"] { color: #2c3e50 !important; font-size: 1.1rem !important; }
        h1 { color: #1e3d59 !important; text-align: center; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1>📊 የክትትል ዳሽቦርድ</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    # ዳታውን ከ Sheet1 (የመመዝገቢያ ገጽ) ማንበብ
    try:
        df = conn.read(worksheet="Sheet1", ttl=0)
    except:
        df = pd.DataFrame() # ሺቱ ባዶ ከሆነ ወይም ካልተገኘ
    
    if not df.empty and 'Status' in df.columns:
        # ሜትሪክስ (Metrics)
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ጠቅላላ ጥያቄ", len(df))
        m2.metric("የጸደቁ ✅", len(df[df['Status'] == 'Approved']))
        m3.metric("የተሰረዙ ❌", len(df[df['Status'] == 'Cancelled']))
        m4.metric("በሂደት ላይ ⏳", len(df[df['Status'] == 'Pending']))
        
        st.markdown("---")
        
        # ቻርቶች (Charts)
        c1, c2 = st.columns(2)
        
        with c1:
            # የቀሩበት ምክንያቶች በፓይ ቻርት (Pie Chart)
            if 'Reason' in df.columns:
                fig_pie = px.pie(df, names='Reason', title='የቀሩበት ምክንያቶች', hole=0.4,
                                 color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig_pie, use_container_width=True)
        
        with c2:
            # የውሳኔዎች ሁኔታ በባር ቻርት (Bar Chart)
            status_colors = {'Approved': '#28a745', 'Cancelled': '#dc3545', 'Pending': '#ffc107'}
            fig_bar = px.bar(df, x='Status', title='የውሳኔዎች ሁኔታ', color='Status',
                             color_discrete_map=status_colors)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # ተጨማሪ፡ የሰራተኞች ዝርዝር ሰንጠረዥ
        st.markdown("### 📋 የቅርብ ጊዜ መዝገቦች")
        st.dataframe(df.tail(10), use_container_width=True)
        
    else:
        st.info("ለማሳየት የሚበቃ ዳታ በ 'Sheet1' ላይ እስካሁን አልተመዘገበም።")
