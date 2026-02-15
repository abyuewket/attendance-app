import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ ሲስተም", page_icon="🏢", layout="wide")

# --- የዲዛይን ማስተካከያ (CSS) ---
st.markdown("""
    <style>
    /* 1. የጎን ማውጫ (Sidebar) ዲዛይን */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#111b21, #1e3d59) !important;
        color: white !important;
    }

    /* 2. 'ሲስተም ሜኑ' ጽሑፍ */
    .sidebar-title {
        color: #00d4ff !important;
        font-size: 35px !important;
        font-weight: bold !important;
        text-align: center;
        padding: 20px 0px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }

    /* 3. ዋናው ገጽ ጀርባ (ነጭ) */
    .stApp {
        background-color: #ffffff;
    }
    
    /* 4. አርዕስቶች */
    h1, h2, h3 {
        color: #1e3d59 !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 5. የቁልፍ (Button) ዲዛይን */
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        box-shadow: 0px 6px 10px rgba(0,0,0,0.2);
    }

    /* 6. የካርድ ዲዛይን (ለማናጀር ገጽ) */
    .request-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 6px solid #007bff;
        margin-bottom: 15px;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
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
    st.markdown('<p class="sidebar-title">🏢 ሲስተም ሜኑ</p>', unsafe_allow_html=True)
    st.markdown("---")
    # ... ሌላው ኮድህ ይቀጥላል
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
    # ለጽሑፍ ግልጽነት የሚረዳ CSS
    st.markdown("""
        <style>
        .request-card {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #007bff;
            margin-bottom: 10px;
            color: #212529 !important;
        }
        .request-card b { color: #1e3d59; }
        </style>
        """, unsafe_allow_html=True)

    st.markdown("<h1 style='color: #1e3d59;'>🔐 የአስተዳዳሪ መቆጣጠሪያ</h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    admin_password = st.text_input("የአስተዳዳሪ ፓስወርድ ያስገቡ", type="password")
    
    # 1. ተጠቃሚው ፓስወርድ ማስገባቱን ማረጋገጥ
    if admin_password:
        correct_pwd = st.secrets.get("admin_password", "1234")
        
        # 2. ፓስወርዱ ትክክል ከሆነ የሚሰራው ክፍል
        if admin_password == correct_pwd:
            df = conn.read(ttl=0)
            
            if not df.empty and 'Status' in df.columns:
                pending = df[df['Status'] == 'Pending']
                
                st.subheader(f"📬 የተጠየቁ  ጥያቄዎች ({len(pending)})")
                if not pending.empty:
                    for index, row in pending.iterrows():
                        st.markdown(f"""
                            <div class="request-card">
                                <b>👤 ሰራተኛ:</b> {row['Full Name']}<br>
                                <b>📅 ቀን:</b> {row['Date']}<br>
                                <b>❓ ምክንያት:</b> {row['Reason']}<br>
                                <b>📝 ዝርዝር:</b> {row['Details']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        rem = st.text_input("ማሳሰቢያ (Remark)", key=f"r_{index}")
                        c1, c2 = st.columns(2)
                        
                        if c1.button("✅ አጽድቅ", key=f"a_{index}"):
                            df.at[index, 'Status'] = 'Approved'
                            df.at[index, 'Remark'] = rem
                            conn.update(data=df)
                            st.success("ጸድቋል!")
                            st.rerun()

                        if c2.button("❌ ሰርዝ", key=f"c_{index}"):
                            df.at[index, 'Status'] = 'Cancelled'
                            df.at[index, 'Remark'] = rem
                            conn.update(data=df)
                            st.warning("ተሰርዟል!")
                            st.rerun()
                else:
                    st.info("አዲስ የሚጠበቅ ጥያቄ የለም።")
                
                st.markdown("---")
                st.subheader("📥 ሪፖርት ማውጫ")
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📊 ሙሉ ሪፖርት አውርድ (Excel/CSV)", data=csv, file_name=f"Attendance_Report_{date.today()}.csv", mime="text/csv")
            else:
                st.warning("ምንም ዳታ አልተገኘም።")
        
        # 3. ፓስወርዱ ስህተት ከሆነ የሚታይ መልእክት
        else:
            st.error("❌ You inserted incorrect password. Please try again.")
            
    else:
        # ፓስወርድ ገና ሳይገባ የሚታይ መመሪያ
        st.info("እባክዎ መቆጣጠሪያውን ለመክፈት ፓስወርድ ያስገቡ።")
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
    
    df = conn.read(ttl=0)
    
    if not df.empty and 'Status' in df.columns:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ጠቅላላ ጥያቄ", len(df))
        # በሊስት ውስጥ 'Approved' መኖሩን ቼክ ማድረግ
        m2.metric("የጸደቁ ✅", len(df[df['Status'] == 'Approved']))
        m3.metric("የተሰረዙ ❌", len(df[df['Status'] == 'Cancelled']))
        m4.metric("በሂደት ላይ ⏳", len(df[df['Status'] == 'Pending']))
        
        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.pie(df, names='Reason', title='የቀሩበት ምክንያቶች', hole=0.4), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df, x='Status', title='የውሳኔዎች ሁኔታ', color='Status',
                                  color_discrete_map={'Approved':'#28a745', 'Cancelled':'#dc3545', 'Pending':'#ffc107'}), use_container_width=True)
    else:
        st.info("ለማሳየት የሚበቃ ዳታ እስካሁን አልተመዘገበም።")


