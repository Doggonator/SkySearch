import requests
import streamlit as st
from bs4 import BeautifulSoup
import random
st.set_page_config("SkySearch")
st.title("Get search results")
if "prev_query" not in st.session_state:
    st.session_state.prev_query = ""
#each proxy (from https://spys.one/free-proxy-list/US/)
p = [{"https": "152.26.229.52:9443", "http": "154.16.146.46:80"}, 
        {"https": "69.49.228.101:3128", "http": "212.56.35.27:3128"}, 
        {"https": "152.26.229.34:9443", "http": "89.117.22.218:8080"},
        {"https": "38.180.138.18:3128", "http": "103.152.112.157:80"},
        {"https": "69.75.172.51:8080", "http": "23.82.137.158:80"},
        {"https": "3.144.74.192:8090", "http": "103.152.112.120:80"},
        {"https": "3.145.65.108:8090", "http": "74.48.78.52:80"},
        {"https": "24.49.117.86:8888", "http": "107.174.127.90:3128"}]
use_proxies = st.toggle("Use proxies? Recommended.")
def search_duckduckgo(query):
    url = "https://duckduckgo.com/html/"
    params = {"q": query}
    print(query)
    for proxies in p:
        try:
            #send the search request through the proxy
            if use_proxies:
                response = requests.get(url, params=params, proxies=proxies, timeout=1)#1 second timeout, using the proxies
                response.raise_for_status()  #raise an error for bad HTTP responses
                if len(extract_links(response.text)) != 0:#make sure we get a response that is not rate limited
                    print("Success")
                    return response.text
                print(f"Error: Rate Limited")
            else:
                response = requests.get(url, params=params, timeout=1)
                response.raise_for_status()  #raise an error for bad HTTP responses
                if len(extract_links(response.text)) != 0:#make sure we get a response that is not rate limited
                    print("Success")
                    return response.text
                print(f"Error: Rate Limited")
                break
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
    return None
def get_html_from_site(url):
    for proxies in p:
        try:
            #send the search request through the proxy
            if use_proxies:
                response = requests.get(url, proxies=proxies, timeout=1)#1 second timeout, using the proxies
                response.raise_for_status()  #raise an error for bad HTTP responses
                return response.text
            else:
                response = requests.get(url, timeout=1)#1 second timeout, using the proxies
                response.raise_for_status()  #raise an error for bad HTTP responses
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
def extract_links(html):
    #parse response
    soup = BeautifulSoup(html, "html.parser")
    links = []
    
    #find result links
    for link in soup.find_all("a", class_="result__a"):
        href = link.get("href")
        text = link.get_text(strip=True)
        is_https = ("https" in href)#so that we know later whether to add https or http
        #now, strip the href of unneeded things, like duckduckgo url and ending &rut=, which are generated by duckduckgo search results
        href = href[href.find("%2F%2F")+6:]#strip off everything before the url, as this is always the indicator for that
        href = href[:href.find("&rut=")]#anything after the &rut=
        if is_https:
            href = "https://"+href
        else:
            href = "http://"+href
        #add in the slashes and dashes (%2F and %2D, respectively)
        href = href.replace("%2F", "/")
        href = href.replace("%2D", "-")
        links.append({"text": text, "url": href})
        print(href)
    
    return links
query = st.text_input("Input your query to search here: ")
if query != st.session_state.prev_query:
    random.shuffle(p)#shuffle our proxies, to reduce timeouts
    result = search_duckduckgo(query)
    if result:
        links = extract_links(result)
        print(links)
        if len(links) == 0:
            st.error("Search backend rate limit error, please try again later")
        #Turn those links into buttons that go to the webpage
        for link in links:
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(link["text"], link["url"])
            with c2:
                text = "Preview Site ("+link["text"]+")"
                if st.button(text):
                    with st.spinner("Loading preview for site..."):
                        html = get_html_from_site(link["url"])
                        st.components.v1.html(html, height=600, scrolling=True)
    else:
        st.error("Search failed, likely due to a proxy failure or a lack of response from our search backend")