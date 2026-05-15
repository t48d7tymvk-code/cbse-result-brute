import streamlit as st
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # Path where render-build.sh installs Chrome
    chrome_bin = "/opt/render/project/src/.render/chrome/opt/google/chrome/google-chrome"
    
    if os.path.exists(chrome_bin):
        options.binary_location = chrome_bin
    
    # In 2026, webdriver-manager + Selenium 4.x handles the version matching
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# --- Your Brute Force Logic Here ---
st.title("CBSE Result Tool")
# ... (rest of your code)
