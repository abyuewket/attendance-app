import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date, datetime
from streamlit_gsheets import GSheetsConnection
import smtplib
from email.mime.text import MIMEText

# --- የገጽ አቀማመጥ ---
st.set_page_config(page_title="የሰራተኞች አቴንዳንስ ሲስተም", page_icon="🏢", layout="wide")

# --- 1. የተስተካከለ CSS (ለጽሑፍ ግልጽነት እና ለጀርባ ቀለም) ---
st.markdown("""
    <style>
    /* 1. የጎን ማውጫው ጀርባ ቀለም */
    [data-testid="stSidebar"] {
        background-color: #111b21 !important; /* ጠቆር ያለ የሚያምር ቀለም */
    }

    /* 2. 'ሲስተም ሜኑ' የሚለውን ጽሑፍ በግልጽ ማሳያ */
    .sidebar-title {
        color: #00d4ff !important; /* ደማቅ ሰማያዊ ቀለም */
        font-size: 100px!important;
        font-weight: bold !important;
        text-align: center;
        padding: 20px 0px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }

    /* 3. ሌሎች የጎን ማውጫ ጽሑፎች (Labels) */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }

    /* 4. የተመረጠው ገጽ ምልክት (Active Radio Button) */
    div[data-testid="stSidebarUserContent"] .stRadio > div {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
    <style>
    /* ዋናው ገጽ ጀርባ - ሙሉ በሙሉ ነጭ */
    .stApp {
        background-color: #ffffff;
    }
    
    /* አርዕስቶች በግልጽ እንዲታዩ (Dark Blue/Black color) */
    h1, h2, h3 {
        color: #1e3d59 !important;
        font-weight: 800 !important;
    }

    /* የጽሑፍ መግለጫዎች ቀለም */
    .stMarkdown p, label {
        color: #2c3e50 !important;
        font-weight: 500 !important;
    }

    /* ባዶ ሳጥኖችን (Cards) እና ጥላዎችን ማጥፊያ */
    [data-testid="stVerticalBlock"] > div:has(div.stMarkdown), 
    [data-testid="stVerticalBlock"] > div {
        background-color: transparent !important;
        padding: 0px !important;
        box-shadow: none !important;
        border: none !important;
    }

    /* የአርዕስት ማስዋቢያ - ከጀርባው ጋር እንዳይዋሃድ */
    .header-box {
        background-color: #f1f4f9;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }

    /* የቁልፍ (Button) ዲዛይን */
    .stButton > button {
        width: 100%;
        border-radius: 6px;
        height: 3em;
        background-color: #007bff;
        color: white;
        border: none;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ዳታ መጫኛ ---
# --- 2. ዳታ መጫኛ (ከጎግል ሺት ብቻ) ---
@st.cache_data(ttl=0)  # ttl=0 ሁልጊዜ አዲስ መረጃ እንዲያመጣ ያደርገዋል
def load_staff_list():
    try:
        # የጎግል ሺት ግንኙነት መፍጠር
        conn = st.connection("gsheets", type=GSheetsConnection)
        
        # "StaffList" ከተባለው ገጽ ላይ ዳታውን ማንበብ
        staff_data = conn.read(worksheet="StaffList", ttl=0)
        
        # ኮለምኖቹ ባዶ አለመሆናቸውን ማረጋገጥ
        if staff_data.empty:
            return pd.DataFrame(columns=['ID', 'Name'])
        return staff_data
    except Exception as e:
        st.error(f"ከጎግል ሺት ጋር መገናኘት አልተቻለም: {e}")
        return pd.DataFrame(columns=['ID', 'Name'])

# ዳታውን መጫን
staff_df = load_staff_list()
conn = st.connection("gsheets", type=GSheetsConnection)
# --- የጎን ማውጫ ማሳመሪያ ---

with st.sidebar:
    # 1. 'ሲስተም ሜኑ' የሚለውን ጽሑፍ በትልቁ እና በደማቅ ቀለም ለማሳየት
    # font-size: 35px በማድረግ መጠኑን በከፍተኛ ሁኔታ መጨመር ትችላለህ
    st.markdown("""
        <div style='text-align: center; padding: 10px;'>
            <span style='font-size: 35px; font-weight: bold; color: #00d4ff; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>
                🏢 ሲስተም ሜኑ
            </span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # የገጽ መምረጫ
    page = st.radio(
        "ገጽ ይምረጡ", 
        ["🏠 የሰራተኞች መሙያ", "🔐 የማናጀር ገጽ", "📊 ዳሽቦርድ"],
        key="main_nav"
    )
    
    st.markdown("---")
    
    # የግርጌ መረጃ (Footer)
    st.markdown("""
        <div style='background-color: #1e293b; padding: 15px; border-radius: 10px; border: 1px solid #334155;'>
            <p style='margin:0; color: #38bdf8; font-size: 0.9rem; font-weight: bold;'>📍 የኢትዮጵያ አቴንዳንስ</p>
            <p style='margin:0; color: #94a3b8; font-size: 0.8rem;'>📅 February 12, 2026</p>
            <p style='margin:0; color: #94a3b8; font-size: 0.8rem;'>🚀 Version 2.0</p>
        </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* 1. የጎን ማውጫው አጠቃላይ ዳራ (Sidebar Background) */
    [data-testid="stSidebar"] {
        background-image: linear-gradient(#1e3d59, #17252a); /* የሚያምር ጥቁር ሰማያዊ Gradient */
        color: white !important;
    }

    /* 2. በጎን ማውጫ ላይ ያሉ ጽሑፎች ቀለም */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stRadio div {
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }

    /* 3. የሬዲዮ በተኖች (Radio Buttons) ማስዋቢያ */
    div[data-testid="stSidebarUserContent"] .stRadio > div {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* 4. የተመረጠው በተን (Hover & Selection) */
    [data-testid="stSidebar"] .stRadio input:checked + div {
        background-color: #007bff !important;
        color: white !important;
        font-weight: bold !important;
        border-radius: 8px;
    }

    /* 5. ከታች ያለው የቨርዥን ጽሑፍ (Footer) */
    .sidebar-footer {
        position: fixed;
        bottom: 20px;
        left: 20px;
        font-size: 0.8rem;
        color: #8892b0;
    }
    </style>
    """, unsafe_allow_html=True)


# --- ገጽ 1: የሰራተኞች መሙያ ---
if page == "🏠 የሰራተኞች መሙያ":
    st.markdown("<div class='header-box'><h1>📝 የአቴንዳንስ መሙያ ፎርም</h1></div>", unsafe_allow_html=True)
    
    emp_id = st.text_input("የሰራተኛ መለያ ቁጥር (Employee ID) ያስገቡ", placeholder="ለምሳሌ: 117102").strip()
    
    if emp_id:
        # 1. የአምድ ስሞችን በትክክል መያዝ (KeyErrorን ለመከላከል)
        # በምስል image_beac7e.png መሰረት 'Full Name' እና 'Employee_ID' መሆናቸውን ያረጋግጡ
        try:
            is_valid = emp_id in staff_df['Employee_ID'].astype(str).values
            if is_valid:
                # እዚህ ጋር 'Full Name' ተብሎ ተስተካክሏል (ምስል image_beac7e.png)
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
                    current_start = datetime.combine(start_date, start_time)
                    current_end = datetime.combine(end_date, end_time)
                    
                    if current_start >= current_end:
                        st.error("❌ ስህተት፦ መነሻ ሰዓት ከመድረሻ ሰዓት ቀደም ማለት አለበት!")
                    else:
                        # 2. ዳታቤዙን በቀጥታ ማንበብ (ምንም Cache የለም)
                        all_data = conn.read(ttl=0)
                        
                        is_overlap = False
                        conflict_time = ""

                        if not all_data.empty:
                            # የዚህን ሰራተኛ መዝገቦች ብቻ በ "ID" አምድ መለየት
                            user_records = all_data[all_data['ID'].astype(str) == str(emp_id)]
                            
                            for _, record in user_records.iterrows():
                                try:
                                    # በሺቱ ላይ ያሉትን ቀናት እና ሰዓቶች ማውጣት
                                    p_date = pd.to_datetime(record['Date']).date()
                                    p_start_time = pd.to_datetime(record['Start_Time']).time()
                                    p_end_time = pd.to_datetime(record['End_Time']).time()
                                    
                                    p_start = datetime.combine(p_date, p_start_time)
                                    p_end = datetime.combine(p_date, p_end_time)
                                    
                                    # 🔍 የመደራረብ ሎጂክ
                                    if current_start < p_end and current_end > p_start:
                                        is_overlap = True
                                        conflict_time = f"{p_start.strftime('%H:%M')} - {p_end.strftime('%H:%M')}"
                                        break
                                except:
                                    continue

                        # 3. የመጨረሻ ውሳኔ
                        if is_overlap:
                            st.error(f"❌ ስህተት፦ ቀደም ሲል በ {conflict_time} ሰዓት ውስጥ ጥያቄ አቅርበዋል።")
                        else:
                            new_row = pd.DataFrame([{
                                "Full Name": staff_name, # በምስል image_beac7e.png መሰረት
                                "ID": emp_id,
                                "Reason": reason,
                                "Details": details,
                                "Status": "Pending",
                                "Remark": "",
                                "Email": "",
                                "Date": start_date.strftime('%Y-%m-%d'),
                                "Start_Time": start_time.strftime('%H:%M:%S'),
                                "End_Time": end_time.strftime('%H:%M:%S')
                            }])
                            
                            updated_df = pd.concat([all_data, new_row], ignore_index=True)
                            conn.update(data=updated_df)
                            st.cache_data.clear() 
                            st.balloons()
                            st.success("✅ ጥያቄዎ ተመዝግቧል!")
            else:
                st.error("❌ የሰራተኛ መለያ ቁጥር አልተገኘም!")
        except KeyError as e:
            st.error(f"❌ የዳታቤዝ ስህተት፦ አምድ {e} አልተገኘም። እባክዎ የሺት ርዕሶችን ይፈትሹ!")
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
