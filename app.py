import streamlit as st
import os
import time
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ====================== CONFIGURATION ======================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    """Sets up Chrome using the built-in Selenium Manager for 2026."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1280,720")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Path where render-build.sh installs Chrome on Render
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        chrome_options.binary_location = render_bin
    
    # Selenium 4.10+ automatically finds the matching driver
    return webdriver.Chrome(options=chrome_options)

def is_success(driver):
    """
    Logic: Returns True if the 'No data found' error message 
    is NOT visible after clicking submit.
    """
    try:
        # Short wait to let the site process the click
        time.sleep(1.5) 
        
        error_elements = driver.find_elements(By.ID, "err_msg")
        
        # If the element is missing entirely, we likely bypassed the login
        if not error_elements:
            return True
            
        error_msg = error_elements[0]
        
        # If the error is visible and contains 'no data', this attempt failed
        if error_msg.is_displayed() and "no data found" in error_msg.text.lower():
            return False
            
        # If the error is hidden or contains different text, it's a success
        return True
    except:
        # In case of doubt (like a page crash), assume success to be safe
        return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Admit ID Recovery", page_icon="🔍")
st.title("🔍 CBSE 12th Admit ID Recovery")

col1, col2 = st.columns(2)
with col1:
    roll_number = st.text_input("Roll Number", value="18615900", help="7 or 8 digit roll number")
with col2:
    known_suffix = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)

delay = st.slider("Request Delay (Seconds)", 0.5, 5.0, 2.0, help="Higher delay prevents IP blocking")

if st.button("🚀 Start Recovery", type="primary"):
    if len(known_suffix) != 6:
        st.error("The suffix must be exactly 6 characters.")
    else:
        with st.status("Initializing Browser...", expanded=True) as status:
            driver = None
            try:
                driver = get_driver()
                letters = string.ascii_uppercase
                combos = [f"{a}{b}" for a in letters for b in letters]
                
                for i, prefix in enumerate(combos):
                    full_id = f"{prefix}{known_suffix}"
                    status.update(label=f"Testing: {full_id} ({i+1}/{len(combos)})", state="running")
                    
                    # 1. Reset page to ensure a clean state
                    driver.get(URL)
                    wait = WebDriverWait(driver, 10)
                    
                    try:
                        # 2. Locate Elements
                        roll_field = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                        admn_field = driver.find_element(By.ID, "admn_id")
                        submit_btn = driver.find_element(By.ID, "submit")
                        
                        # 3. Input Data (Clear first to be safe)
                        roll_field.clear()
                        roll_field.send_keys(roll_number)
                        admn_field.clear()
                        admn_field.send_keys(full_id)
                        
                        # 4. Click Submit
                        submit_btn.click()
                        
                        # 5. Check Result
                        if is_success(driver):
                            status.update(label="✅ Success!", state="complete")
                            st.balloons()
                            st.success(f"**MATCH FOUND!**\n\nAdmit Card ID: `{full_id}`")
                            st.code(f"Full Admit ID: {full_id}", language="text")
                            break
                        
                    except Exception as e:
                        # If a single attempt fails due to timeout, just keep going
                        continue
                else:
                    status.update(label="❌ No Match Found", state="error")
                    st.warning("Finished all 676 combinations without a result.")

            except Exception as e:
                st.error(f"Critical System Error: {e}")
            finally:
                if driver:
                    driver.quit()
