import requests
import streamlit as st
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from st_click_detector import click_detector
import urllib.parse#for getting base urls of pages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
st.set_page_config("SkySearch", layout="wide")#layout wide allows for canvases to be better (viewing in the web)
st.title("SkySearch Proxy Engine")
st.caption("Version 2.0a")
st.write("----RULES----")
st.caption("1. Do not talk about SkySearch")
st.caption("2. Do NOT talk about SkySearch")
st.caption("3. Protect SkySearch from anyone who may want to take it down")
#each proxy (from https://spys.one/free-proxy-list/US/)
if "p" not in st.session_state:
    st.session_state.p = [{"https": "https://152.26.229.52:9443", "http": "http://154.16.146.46:80"},
       {"https": "https://69.49.228.101:3128", "http": "http://212.56.35.27:3128"},
       {"https": "https://152.26.229.34:9443", "http": "http://89.117.22.218:8080"},
       {"https": "https://38.180.138.18:3128", "http": "http://103.152.112.157:80"},
       {"https": "https://69.75.172.51:8080", "http": "http://23.82.137.158:80"},
       {"https": "https://3.144.74.192:8090", "http": "http://103.152.112.120:80"},
       {"https": "https://3.145.65.108:8090", "http": "http://74.48.78.52:80"},
       {"https": "https://24.49.117.86:8888", "http": "http://107.174.127.90:3128"}]
#if "p" not in st.session_state:
#    st.session_state.p = [
#        {"https": "69.49.228.101:3128"},
#        {"https": "152.26.229.34:9443"},
#        {"https": "38.180.138.18:3128"},
#        {"https": "152.26.229.52:9443"},
#        {"https": "69.75.172.51:8080"},
#        {"https": "3.144.74.192:8090"},
#        {"https": "3.145.65.108:8090"},
#        {"https": "24.49.117.86:8888"}]
if "b_id" not in st.session_state:#button id
    st.session_state.b_id = 0
if "url" not in st.session_state:#keeps track of the url of the current page.
    st.session_state.url = ""#used for reloading the page
if "site_title" not in st.session_state:
    st.session_state.site_title = ""
if "ordered" not in st.session_state:
    st.session_state.ordered = False#we use this because ddg is the best way to find working proxies. When the ddg is successful, the proxies are re-ordered with the working one first
use_proxies = st.toggle("Use proxies? Not recommended unless search is not working")
#initialize selenium browser
def get_browser(open_browser = True):
    if "driver" not in st.session_state and open_browser:
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        if use_proxies:#we have to find a proxy, then activate it
            if not st.session_state.ordered:
                update_proxies()
            if st.session_state.ordered:#make sure we still ordered them properly
                chrome_options.add_argument(f"--proxy-server={st.session_state.p[0]}")
                st.session_state.driver = webdriver.Chrome(options=chrome_options)#now, initialize the browser
            else:
                st.error("Failed to connect to any proxy")
        else:
            st.session_state.driver = webdriver.Chrome(options=chrome_options)#now, initialize the browser
    if "driver" in st.session_state:
        return st.session_state.driver
def update_proxies():
    working = None
    with st.status("Finding a working proxy...") as proxy_try:
        i = 0
        for proxy in st.session_state.p:
            i += 1
            proxy_try.update(label="Now trying proxy #"+str(i))
            try:
                response = requests.get("https://www.google.com", proxies=proxy, timeout=10)
                if response.status_code == 200:
                    working = proxy
                    break
                else:
                    print(f"Unexpected status code: {response.status_code}")
                    print("Proxy failed: "+proxy['https'])
                    continue
            except requests.exceptions.RequestException as e:
                print(f"Proxy check failed: {e}")
                print("Proxy failed: "+proxy['https'])
                continue
        if working != None:
            st.session_state.ordered = True
            i = st.session_state.p.index(working)
            if i != 1:#swap the working one to be the first one
                this = st.session_state.p[i-1]#make a temp
                st.session_state.p[i-1] = st.session_state.p[0]#replace this with index 0
                st.session_state.p[0] = this#Set index zero to this
if st.button("Load browser"):
    st.session_state.url = "https://lite.duckduckgo.com/lite/"
    browser = get_browser(open_browser=False)
    try:
        print(browser.current_url)
    except:#browser has been closed
        if "driver" in st.session_state:
            del st.session_state["driver"]#delete so that it is re-initialized
        browser = get_browser()
    
    browser.get(st.session_state.url)