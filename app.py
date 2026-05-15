import streamlit as st
import os
import time
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
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
        # st.sidebar.info("Using Render Chrome Binary")
    
    # IMPORTANT: Do NOT use webdriver-manager. 
    # Simply initializing the driver will trigger Selenium Manager 
    # to find the v148 driver automatically.
    return webdriver.Chrome(options=chrome_options)

def is_success(driver):
    """Detects if the result page has loaded."""
    try:
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements and error_elements[0].is_displayed():
            if error_elements[0].text.strip():
                return False
        
        page_source = driver.page_source.lower()
        keywords = ["marks", "subject", "grade", "total", "percentage", "pass"]
        if any(word in page_source for word in keywords):
            return True
            
        if "result" in driver.current_url.lower() and "html" not in driver.current_url.lower():
            return True
    except:
        pass
    return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Recovery", page_icon="🔍")
st.title("🔍 CBSE 12th Admit ID Recovery")

roll_number = st.text_input("Roll Number", value="18615900")
known_suffix = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Wait time per attempt (Seconds)", 1.0, 5.0, 2.5)

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
                    
                    driver.get(URL)
                    wait = WebDriverWait(driver, 10)
                    
                    try:
                        roll_field = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                        admn_field = driver.find_element(By.ID, "admn_id")
                        
                        roll_field.clear()
                        roll_field.send_keys(roll_number)
                        admn_field.clear()
                        admn_field.send_keys(full_id)
                        
                        driver.find_element(By.ID, "submit").click()
                        time.sleep(delay)

                        if is_success(driver):
                            status.update(label="✅ Success!", state="complete")
                            st.balloons()
                            st.success(f"**MATCH FOUND!** Admit Card ID: `{full_id}`")
                            st.code(full_id)
                            break
                    except Exception:
                        continue
                else:
                    status.update(label="❌ No Match Found", state="error")
                    st.warning("All 676 combinations exhausted.")

            except Exception as e:
                st.error(f"Critical System Error: {e}")
            finally:
                if driver:
                    driver.quit()
