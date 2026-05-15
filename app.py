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
    """Sets up the Chrome driver for both Local and Render environments."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Path where render-build.sh installs Chrome on Render's servers
    render_chrome_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    
    if os.path.exists(render_chrome_bin):
        chrome_options.binary_location = render_chrome_bin
    
    # webdriver-manager automatically downloads the matching ChromeDriver
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def is_success(driver):
    """Detects if the result was found based on keywords or URL changes."""
    try:
        # 1. Check for specific error message text
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements and error_elements[0].is_displayed():
            if error_elements[0].text.strip():
                return False
        
        # 2. Check for success keywords in page content
        page_text = driver.page_source.lower()
        success_indicators = ["marks", "subject", "grade", "total", "percentage", "pass"]
        if any(ind in page_text for ind in success_indicators):
            return True
            
        # 3. Check if the URL changed to a result page
        if "result" in driver.current_url.lower() and "html" not in driver.current_url.lower():
            return True
    except:
        pass
    return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Result Recovery", layout="centered")
st.title("🔍 CBSE 12th Result Recovery Tool")
st.info("Note: This tool is for recovering lost Admit Card IDs using known suffixes.")

# User Inputs
roll_number = st.text_input("Roll Number", value="18615900")
known_suffix = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Seconds between attempts", 1.0, 5.0, 2.5, 0.5)

if st.button("🚀 Start Recovery Process", type="primary"):
    if len(known_suffix) != 6:
        st.error("The last 6 characters must be exactly 6 digits/letters.")
    else:
        status = st.empty()
        progress = st.progress(0)
        log_expander = st.expander("Detailed Attempt Log", expanded=True)
        
        driver = None
        try:
            driver = get_driver()
            letters = string.ascii_uppercase
            combinations = [f"{a}{b}" for a in letters for b in letters]
            total_attempts = len(combinations)

            for index, prefix in enumerate(combinations):
                full_id = f"{prefix}{known_suffix}"
                
                # Update UI
                status.info(f"Testing: **{full_id}** ({index+1}/{total_attempts})")
                progress.progress((index + 1) / total_attempts)

                try:
                    # RE-LOAD URL every time to prevent 'StaleElementReferenceException'
                    driver.get(URL)
                    wait = WebDriverWait(driver, 10)
                    
                    # Locate and Fill
                    roll_input = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                    admn_input = driver.find_element(By.ID, "admn_id")
                    
                    roll_input.clear()
                    roll_input.send_keys(roll_number)
                    admn_input.clear()
                    admn_input.send_keys(full_id)
                    
                    # Submit
                    driver.find_element(By.ID, "submit").click()
                    
                    # Wait for server response
                    time.sleep(delay)

                    # Check Success
                    if is_success(driver):
                        st.balloons()
                        st.success(f"✅ **FOUND MATCH!**\n\nAdmit Card ID: `{full_id}`")
                        st.code(f"Roll: {roll_number}\nAdmit Card ID: {full_id}", language="text")
                        break
                    else:
                        log_expander.write(f"❌ {full_id} - Incorrect")

                except Exception as e:
                    log_expander.error(f"⚠️ Error testing {full_id}: {str(e)[:50]}")
                    continue

            else:
                st.warning("Finished all 676 combinations without a match.")

        except Exception as e:
            st.error(f"Critical System Error: {e}")
        finally:
            if driver:
                driver.quit()
