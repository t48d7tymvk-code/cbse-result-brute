from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ... (inside your loop)

        for i, prefix in enumerate(combos):
            full_id = f"{prefix}{suffix_val}"
            debug_text.info(f"Currently Testing: **{full_id}**")
            
            driver.get(URL)
            
            try:
                # NEW: Wait up to 10 seconds for the roll number field to actually exist
                wait = WebDriverWait(driver, 10)
                roll_in = wait.until(EC.presence_of_element_located((By.ID, "rroll")))
                
                # If we get here, the element was found!
                admn_in = driver.find_element(By.ID, "admn_id")
                sub_btn = driver.find_element(By.ID, "submit")
                
                roll_in.send_keys(roll_val)
                admn_in.send_keys(full_id)
                sub_btn.click()
                
                time.sleep(delay)
                
                # Check for success...
                
            except Exception as loop_err:
                # Take a screenshot to see WHY it failed (is it a captcha? a 403 error?)
                screenshot = driver.get_screenshot_as_png()
                debug_image.image(screenshot, caption=f"Error Screenshot for {full_id}")
                log_window.error(f"❌ Could not find form at {full_id}. Check the image!")
                continue
