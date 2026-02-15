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
    /* 1. የጎን ማውጫ (Sidebar) - ደማቅ ጥቁር ሰማያዊ */
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

    /* 2. ዋናው ገጽ ጀርባ - ሙሉ በሙሉ ነጭ */
    .stApp { background-color: #ffffff; }

    /* 3. የአርዕስት ሳጥኖች (Header Boxes) - ጎልቶ የሚታይ */
    .header-box {
        background-color: #f0f7ff;
        padding: 25px;
        border-radius: 15px;
        border-left: 10px solid #007bff;
        margin-bottom: 30px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.08);
    }
    .header-box h1 {
        color: #1e3d59 !important;
        margin: 0;
        font-weight: 800 !important;
    }

    /* 4. የፎርም ሳጥኖች እና ግብዓቶች (Inputs) */
    label {
        color: #2c3e50 !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    .stTextInput input, .stSelectbox div, .stTextArea textarea {
        border-radius: 8px !important;
        border: 1px solid #d1d9e6 !important;
    }

    /* 5. የቁልፍ (Button) ዲዛይን - ትልቅ እና ደማቅ */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.8em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        font-size: 1.1rem;
        border: none;
        transition: 0.3s ease;
        box-shadow: 0px 5px 15px rgba(0, 123, 255, 0.3);
    }
    .stButton > button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }

    /* 6. የማናጀር ገጽ ካርዶች (Request Cards) */
    .request-card {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #e1e8f0;
        border-left: 6px solid #00d4ff;
        margin-bottom: 15px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
    }
    .request-card b { color: #1e3d59; }
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
    except:
        return pd.DataFrame(columns=['Employee_ID', 'Full Name'])

conn = st.connection("gsheets", type=GSheetsConnection)
staff_df = load_staff_list()

# --- 3. የጎን ማውጫ ---
with st.sidebar:
    st.markdown('<p class="sidebar-title">🏢 ሲስተም ሜኑ</p>', unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("ገጽ ይምረጡ", ["🏠 የሰራተኞች መሙያ", "🔐 የማናጀር ገጽ", "📊 ዳሽቦርድ"])
    st.markdown("---")
    st.markdown("""
        <div style='color: #8892b0; font-size: 0.85rem; text-align: center;'>
            📍 የኢትዮጵያ አቴንዳንስ ሲስተም<br>🚀 Version 2.5
        </div>
    """, unsafe_allow_html=True)

# --- ገጽ 1: የሰራተኞች መሙያ ---
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<div class='header-box'><h1>📝 የፈቃድ መጠየቂያ ፎርም</h1></div>", unsafe_allow_html=True)
    
    with st.container():
        emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
        
        if emp_id:
            is_valid = emp_id in staff_df['Employee_ID'].astype(str).values
            if is_valid:
                staff_name = staff_df[staff_df['Employee_ID'].astype(str) == emp_id]['Full Name'].values[0]
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
                    st.success("✅ ጥያቄዎ በትክክል ተመዝግቧል!")
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
            st.subheader(f"📬 አዲስ ጥያቄዎች ({len(pending)})")
            
            for index, row in pending.iterrows():
                st.markdown(f"""
                    <div class="request-card">
                        <span style='color: #007bff; font-weight: bold;'>👤 ሰራተኛ: {row['Full Name']}</span><br>
                        <b>🆔 መለያ:</b> {row['ID']} | <b>❓ ምክንያት:</b> {row['Reason']}<br>
                        <b>📅 ቀን:</b> {row['Date']} ({row['Start_Time']} - {row['End_Time']})<br>
                        <b>📝 ዝርዝር:</b> {row['Details']}
                    </div>
                """, unsafe_allow_html=True)
                
                rem = st.text_input("ማሳሰቢያ (Remark)", key=f"r_{index}", placeholder="ለምሳሌ: ተፈቅዷል...")
                c1, c2 = st.columns(2)
                if c1.button("✅ አጽድቅ", key=f"a_{index}"):
                    df.at[index, 'Status'] = 'Approved'
                    df.at[index, 'Remark'] = rem
                    conn.update(worksheet="Sheet1", data=df)
                    st.success(f"የ {row['Full Name']} ጥያቄ ጸድቋል!")
                    st.rerun()
                if c2.button("❌ ሰርዝ", key=f"c_{index}"):
                    df.at[index, 'Status'] = 'Cancelled'
                    df.at[index, 'Remark'] = rem
                    conn.update(worksheet="Sheet1", data=df)
                    st.warning("ጥያቄው ተሰርዟል!")
                    st.rerun()
            if len(pending) == 0:
                st.info("አዲስ የሚጠበቅ ጥያቄ የለም።")
        else:
            st.info("ምንም አይነት መዝገብ አልተገኘም።")
    elif admin_password:
        st.error("❌ የተሳሳተ ፓስወርድ!")
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
       # st.markdown("### 📋 የቅርብ ጊዜ መዝገቦች")
        #st.dataframe(df.tail(10), use_container_width=True)
        
   # else:
        #st.info("ለማሳየት የሚበቃ ዳታ በ 'Sheet1' ላይ እስካሁን አልተመዘገበም።")


