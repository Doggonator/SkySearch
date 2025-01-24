#Version 1.1
import requests
import streamlit as st
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
st.set_page_config("SkySearch")
st.title("SkySearch Proxy Engine")
#each proxy (from https://spys.one/free-proxy-list/US/)
#p = [{"https": "152.26.229.52:9443", "http": "154.16.146.46:80"},
#        {"https": "69.49.228.101:3128", "http": "212.56.35.27:3128"},
#        {"https": "152.26.229.34:9443", "http": "89.117.22.218:8080"},
#        {"https": "38.180.138.18:3128", "http": "103.152.112.157:80"},
#        {"https": "69.75.172.51:8080", "http": "23.82.137.158:80"},
#        {"https": "3.144.74.192:8090", "http": "103.152.112.120:80"},
#        {"https": "3.145.65.108:8090", "http": "74.48.78.52:80"},
#        {"https": "24.49.117.86:8888", "http": "107.174.127.90:3128"}]
if "p" not in st.session_state:
    st.session_state.p = [
        {"https": "69.49.228.101:3128"},
        {"https": "152.26.229.34:9443"},
        {"https": "38.180.138.18:3128"},
        {"https": "152.26.229.52:9443"},
        {"https": "69.75.172.51:8080"},
        {"https": "3.144.74.192:8090"},
        {"https": "3.145.65.108:8090"},
        {"https": "24.49.117.86:8888"}]
if "html" not in st.session_state:
    st.session_state.html = ""
if "b_id" not in st.session_state:#button id
    st.session_state.b_id = 0
use_proxies = st.toggle("Use proxies? Not recommended unless on a very restricted network.")
def search_duckduckgo(query):
    #url = "https://duckduckgo.com/html/"
    #params = {"q": query}
    with st.spinner("Getting search results..."):
        with st.status("Booting up systems") as proxy_try:
            i = 1
            for proxy in st.session_state.p:
                try:
                    #send the search request through the proxy
                    if use_proxies:
                        proxy_try.update(label = ("Now trying proxy: "+str(i)))
                        #response = requests.get(url, params=params, proxies=proxies, timeout=1)#1 second timeout, using the proxies
                        #response.raise_for_status()  #raise an error for bad HTTP responses
                        #return response.text
                        ddgs = DDGS(proxy=proxy["https"], timeout=5)  # "tb" proxy is an alias for "socks5://127.0.0.1:9150"
                        results = ddgs.text(query, max_results=10)

                        print(proxy["https"])
                        #swap out to use the best proxy we have, which is this one, if it is not the first in the list already
                        if i != 1:
                            this = st.session_state.p[i-1]#make a temp
                            st.session_state.p[i-1] = st.session_state.p[0]#replace this with index 0
                            st.session_state.p[0] = this#Set index zero to this
                        return results
                    else:
                        proxy_try.update(label="Getting non-proxied results")
                        #response = requests.get(url, params=params, timeout=1)
                        #response.raise_for_status()  #raise an error for bad HTTP responses
                        #return response.text
                        return DDGS().text(query, max_results = 10)
                except Exception as e:
                    print(f"Error: {e}")
                    print("Proxy used (if proxies active): "+proxy["https"])
                i += 1
            return None
def get_html_from_site(url):
    i = 1
    for proxies in st.session_state.p:
        try:
            #send the search request through the proxy
            if use_proxies:
                response = requests.get(url, proxies=proxies, timeout=5)#5 second timeout, using the proxies
                response.raise_for_status()  #raise an error for bad HTTP responses
                #swap out to use the best proxy we have, which is this one, if it is not the first in the list already
                if i != 1:
                    this = st.session_state.p[i-1]#make a temp
                    st.session_state.p[i-1] = st.session_state.p[0]#replace this with index 0
                    st.session_state.p[0] = this#Set index zero to this
                   
                return response.text
            else:
                response = requests.get(url, timeout=5)#5 second timeout, using the proxies
                response.raise_for_status()  #raise an error for bad HTTP responses
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        i += 1
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
def inject_js_to_html(html_content, url):
    soup = BeautifulSoup(html_content, 'html.parser')
   
    #find all <script> tags that reference external JS files
    js_files = [script['src'] for script in soup.find_all('script', src=True)]
   
    #step 3: Download the JS files
    js_contents = {}
    for js_file in js_files:
        if js_file.startswith('http'):  #check if the URL is absolute
            js_url = js_file
        else:  #if it's a relative URL, make it absolute
            js_url = requests.compat.urljoin(url, js_file)
        js_response = requests.get(js_url)
        js_contents[js_file] = js_response.text
   
    #step 4: inject JS files into the HTML
    for js_file, js_content in js_contents.items():
        #inject the JS content directly into the HTML using a <script> tag
        script_tag = f'<script>{js_content}</script>'
        soup.body.append(script_tag)
    return str(soup)#return this updated html
if st.session_state.html == "":
    query = st.text_input("Input your query to search here: ")
    if query != "":
        st.session_state.b_id = 0
        result = search_duckduckgo(query)
        if result:
            #links = extract_links(result)
            #print(links)
            #if len(links) == 0:
            #    st.error("Search backend rate limit error, please try again later")
            links = result
            print(links)
            #Turn those links into buttons that go to the webpage
            for link in links:
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button(link["title"]+str(st.session_state.b_id), link["href"])
                    st.session_state.b_id += 1
                with c2:
                    text = "Preview Site ("+link["title"]+")"+str(st.session_state.b_id)
                    st.session_state.b_id += 1
                    if st.button(text):
                        with st.spinner("Loading preview for site..."):
                            html = get_html_from_site(link["href"])#get html
                            html = inject_js_to_html(html, link["href"])#inject js
                            st.session_state.html = html#update html
                            st.rerun()#rerun
        else:
            st.error("Search failed, likely due to a proxy failure or a lack of response from our search backend")
else:#we are now rendering the html
    st.components.v1.html(st.session_state.html, height=600, scrolling=True)
    if st.button("Back to search"):
        st.session_state.html = ""
        st.rerun()#go back to search