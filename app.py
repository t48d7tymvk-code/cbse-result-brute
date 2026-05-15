import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import string

# ====================== CONFIGURATION ======================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    """Sets up Chrome for both Local and Render environments."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Render's specific Chrome binary path (from render-build.sh)
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    
    if os.path.exists(render_bin):
        chrome_options.binary_location = render_bin
        st.sidebar.success("✅ Using Render Chrome Binary")
    else:
        st.sidebar.info("ℹ️ Using System Chrome (Local Mode)")
    
    # Automatically manages the ChromeDriver version
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def is_success(driver):
    """Detects if we broke through to the result page."""
    try:
        # Check for error text (if it exists, we failed)
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements and error_elements[0].is_displayed():
            if error_elements[0].text.strip():
                return False
        
        # Check for success keywords
        page_source = driver.page_source.lower()
        keywords = ["marks", "subject", "grade", "total", "percentage", "pass"]
        if any(word in page_source for word in keywords):
            return True
            
        # Check for URL change
        if "result" in driver.current_url.lower() and "html" not in driver.current_url.lower():
            return True
    except:
        pass
    return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Result Recovery", layout="centered")
st.title("🔍 CBSE 12th Admit ID Recovery")

# Inputs
roll_number = st.text_input("Roll Number", value="18615900")
known_suffix = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Wait time per attempt (Seconds)", 1.0, 5.0, 2.5)

if st.button("🚀 Start Recovery", type="primary"):
    if len(known_suffix) != 6:
        st.error("The suffix must be exactly 6 characters.")
    else:
        status_box = st.empty()
        progress_bar = st.progress(0)
        log = st.expander("Attempt Log", expanded=True)
        
        driver = None
        try:
            driver = get_driver()
            letters = string.ascii_uppercase
            combos = [f"{a}{b}" for a in letters for b in letters]
            total = len(combos)

            for i, prefix in enumerate(combos):
                full_id = f"{prefix}{known_suffix}"
                
                # Update UI
                status_box.info(f"Trying: **{full_id}** ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)

                try:
                    # RE-LOAD URL every time to avoid stale elements
                    driver.get(URL)
                    wait = WebDriverWait(driver, 10)
                    
                    # Fill inputs
                    roll_field = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                    admn_field = driver.find_element(By.ID, "admn_id")
                    
                    roll_field.clear()
                    roll_field.send_keys(roll_number)
                    admn_field.clear()
                    admn_field.send_keys(full_id)
                    
                    # Submit
                    driver.find_element(By.ID, "submit").click()
                    
                    # Wait for network
                    time.sleep(delay)

                    if is_success(driver):
                        st.balloons()
                        st.success(f"🎊 **FOUND MATCH!**\n\nAdmit Card ID: `{full_id}`")
                        st.code(f"ID: {full_id}", language="text")
                        break
                    else:
                        log.write(f"❌ {full_id} - Incorrect")
                        
                except Exception as e:
                    log.error(f"⚠️ Error on {full_id}: {str(e)[:50]}")
                    continue
            else:
                st.warning("All 676 combinations exhausted. No match found.")

        except Exception as e:
            st.error(f"System Error: {e}")
        finally:
            if driver:
                driver.quit()
