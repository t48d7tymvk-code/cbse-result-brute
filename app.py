import streamlit as st
import os
import time
import string
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ====================== CONFIGURATION ======================
URL = "https://umangresults.digilocker.gov.in/CBSE12th2026resultmayzaqw.html"

def get_driver():
    """Sets up a memory-optimized Chrome instance for Render."""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=800,600")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    
    # Render's specific Chrome binary path
    render_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(render_bin):
        chrome_options.binary_location = render_bin
    
    # Using Selenium 4.10+ native manager (No webdriver-manager needed)
    return webdriver.Chrome(options=chrome_options)

def is_success(driver):
    """Checks for the absence of the 'No data found' error message."""
    try:
        time.sleep(1.2) 
        error_elements = driver.find_elements(By.ID, "err_msg")
        if not error_elements:
            return True
            
        error_msg = error_elements[0]
        if error_msg.is_displayed() and "no data found" in error_msg.text.lower():
            return False
            
        return True
    except:
        return False

# ====================== STREAMLIT UI ======================
st.set_page_config(page_title="CBSE Recovery", page_icon="🔍")
st.title("🔍 CBSE 12th Admit ID Recovery")

st.sidebar.header("Inputs")
roll_val = st.sidebar.text_input("Roll Number", value="18615895")
suffix_val = st.sidebar.text_input("Known Suffix (Last 6)", value="954511")
delay_val = st.sidebar.slider("Delay (Seconds)", 0.5, 5.0, 1.5)

if st.button("🚀 Start Recovery Process", type="primary"):
    status_container = st.empty()
    progress_bar = st.progress(0)
    log_area = st.expander("Attempt Logs", expanded=False)
    
    driver = None
    try:
        driver = get_driver()
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Update UI
            status_container.info(f"Testing: **{full_id}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Use JS injection to fill and submit
                driver.execute_script(f"document.getElementById('rroll').value = '{roll_val}';")
                driver.execute_script(f"document.getElementById('admn_id').value = '{full_id}';")
                driver.execute_script("document.getElementById('submit').click();")
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **MATCH FOUND!** Admit Card ID: `{full_id}`")
                    st.code(full_id, language="text")
                    break
                else:
                    log_area.write(f"❌ {full_id}: Incorrect")
                    
            except Exception:
                driver.get(URL)
                continue
                
        else:
            st.warning("All combinations tested. No match found.")
            
    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()        driver = get_driver()
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Update UI
            status_container.info(f"Testing: **{full_id}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Use JS injection to fill and submit
                driver.execute_script(f"document.getElementById('rroll').value = '{roll_val}';")
                driver.execute_script(f"document.getElementById('admn_id').value = '{full_id}';")
                driver.execute_script("document.getElementById('submit').click();")
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **MATCH FOUND!** Admit Card ID: `{full_id}`")
                    st.code(full_id, language="text")
                    break
                else:
                    log_area.write(f"❌ {full_id}: Incorrect")
                    
            except Exception:
                driver.get(URL)
                continue
                
        else:
            st.warning("All combinations tested. No match found.")
            
    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Update UI
            status_container.info(f"Testing: **{full_id}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Use JS injection to fill and submit
                driver.execute_script(f"document.getElementById('rroll').value = '{roll_val}';")
                driver.execute_script(f"document.getElementById('admn_id').value = '{full_id}';")
                driver.execute_script("document.getElementById('submit').click();")
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **MATCH FOUND!** Admit Card ID: `{full_id}`")
                    st.code(full_id, language="text")
                    break
                else:
                    log_area.write(f"❌ {full_id}: Incorrect")
                    
            except Exception:
                driver.get(URL)
                continue
                
        else:
            st.warning("All combinations tested. No match found.")
            
    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()    try:
        driver = get_driver()
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Update UI
            status_container.info(f"Testing: **{full_id}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Use JS injection to fill and submit (Saves RAM)
                driver.execute_script(f"document.getElementById('rroll').value = '{roll_val}';")
                driver.execute_script(f"document.getElementById('admn_id').value = '{full_id}';")
                driver.execute_script("document.getElementById('submit').click();")
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **MATCH FOUND!** Admit Card ID: `{full_id}`")
                    st.code(full_id, language="text")
                    break
                else:
                    log_area.write(f"❌ {full_id}: Incorrect")
                    
            except Exception:
                driver.get(URL)
                continue
                
        else:
            st.warning("All combinations tested. No match found.")
            
    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()    progress_bar = st.progress(0)
    log_area = st.expander("Attempt Logs", expanded=False)
    
    driver = None
    try:
        driver = get_driver()
        driver.get(URL)
        
        letters = string.ascii_uppercase
        combos = [f"{a}{b}" for a in letters for b in letters]
        
        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            
            # Update UI
            status_container.info(f"Testing: **{full_id}** ({i+1}/{len(combos)})")
            progress_bar.progress((i + 1) / len(combos))
            
            try:
                # Use JS injection to fill and submit
                driver.execute_script(f"document.getElementById('rroll').value = '{roll_val}';")
                driver.execute_script(f"document.getElementById('admn_id').value = '{full_id}';")
                driver.execute_script("document.getElementById('submit').click();")
                
                time.sleep(delay_val)
                
                if is_success(driver):
                    st.balloons()
                    st.success(f"🎉 **MATCH FOUND!** Admit Card ID: `{full_id}`")
                    st.code(full_id, language="text")
                    break
                else:
                    log_area.write(f"❌ {full_id}: Incorrect")
                    
            except Exception:
                # Basic error recovery: refresh page and continue
                driver.get(URL)
                continue
                
        else:
            st.warning("All combinations tested. No match found.")
            
    except Exception as e:
        st.error(f"Critical System Error: {e}")
    finally:
        if driver:
            driver.quit()
