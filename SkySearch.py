import requests
import streamlit as st
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from st_click_detector import click_detector
import urllib.parse#for getting base urls of pages
st.set_page_config("SkySearch", layout="wide")#layout wide allows for canvases to be better (viewing in the web)
st.title("SkySearch Proxy Engine")
st.caption("Version 1.5a")
st.write("----RULES----")
st.caption("1. There is no SkySearch")
st.caption("2. There is no SkySearch")
st.caption("3. We don't talk about SkySearch")
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
if "g_mode" not in st.session_state:#game mode
    st.session_state.g_mode = False
if "url" not in st.session_state:#keeps track of the url of the current page.
    st.session_state.url = ""#used for reloading the page
use_proxies = st.toggle("Use proxies? Not recommended unless search is not working")
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
#def extract_links(html):
#    #parse response
#    soup = BeautifulSoup(html, "html.parser")
#    links = []
#   
#    #find result links
#    for link in soup.find_all("a", class_="result__a"):
#        href = link.get("href")
#        text = link.get_text(strip=True)
#        is_https = ("https" in href)#so that we know later whether to add https or http
#        #now, strip the href of unneeded things, like duckduckgo url and ending &rut=, which are generated by duckduckgo search results
#        href = href[href.find("%2F%2F")+6:]#strip off everything before the url, as this is always the indicator for that
#        href = href[:href.find("&rut=")]#anything after the &rut=
#        if is_https:
#            href = "https://"+href
#        else:
#            href = "http://"+href
#        #add in the slashes and dashes (%2F and %2D, respectively)
#        href = href.replace("%2F", "/")
#        href = href.replace("%2D", "-")
#        links.append({"text": text, "url": href})
#        print(href)
#  
#    return links
def ensure_has_base_link(path, link):
    if path.startswith("http"):
        return path
    else:
        #get base of link
        url = link
        parsed = urllib.parse.urlparse(url)
        with_path = False#fragment because the base url get code is from https://stackoverflow.com/questions/35616434/how-can-i-get-the-base-of-a-url-in-python
        path   = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
        parsed = parsed._replace(path=path)
        parsed = parsed._replace(params='')
        parsed = parsed._replace(query='')
        parsed = parsed._replace(fragment='')
        base_url = parsed.geturl()+'/'
        return base_url+path
def fetch_and_inject_css(html_content,url):#add the css files into the html
    try:#in case proxy errors
        #parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        #find all <link> tags that link to CSS files
        link_tags = soup.find_all('link', rel='stylesheet')
        status = st.empty()
        for link in link_tags:
            css_url = link['href']
            print("Loading "+css_url)
            with status.container():
                st.status("Loading "+css_url)
            #fetch the CSS content
            try:
                if use_proxies:
                    for proxy in st.session_state.p:
                        try:
                            response = requests.get(ensure_has_base_link(css_url, url), proxies = proxy, timeout = 5)
                            response.raise_for_status()
                            css_content = response.text
                            
                            #create a <style> tag with the fetched CSS
                            style_tag = soup.new_tag('style')
                            style_tag.string = css_content
                            
                            #replace the <link> tag with the <style> tag
                            link.replace_with(style_tag)
                        except:
                            print("Likely timed out with proxy: "+proxy)
                else:
                    response = requests.get(ensure_has_base_link(css_url, url))
                    response.raise_for_status()
                    css_content = response.text
                    
                    #create a <style> tag with the fetched CSS
                    style_tag = soup.new_tag('style')
                    style_tag.string = css_content
                    
                    #replace the <link> tag with the <style> tag
                    link.replace_with(style_tag)
            except requests.RequestException as e:
                print(f"Failed to fetch CSS from {css_url}: {e}")
        
        # Return the modified HTML
        return str(soup)
    except:
        return html_content
def inject_js_to_html(html_content, url):
    try:#in case there are problems with the proxies
        soup = BeautifulSoup(html_content, 'html.parser')
    
        #find all <script> tags that reference external JS files
        js_files = [script['src'] for script in soup.find_all('script', src=True)]
    
        #step 3: Download the JS files
        js_contents = {}
        status = st.empty
        for js_file in js_files:
            print("Loading "+js_file)
            with status.container():
                st.status("Loading "+js_file)
            js_url = ensure_has_base_link(js_file, url)
            if use_proxies:
                for proxy in st.session_state.p:
                    try:
                        js_response = requests.get(js_url, proxies = proxy, timeout = 5)
                        js_contents[js_file] = js_response.text
                    except:
                        print("Likely timed out with proxy: "+proxy)
            else:
                js_response = requests.get(js_url)
                js_contents[js_file] = js_response.text
    
        #step 4: inject JS files into the HTML
        for js_file, js_content in js_contents.items():
            #inject the JS content directly into the HTML using a <script> tag
            script_tag = f'<script>{js_content}</script>'
            soup.body.append(script_tag)
        return str(soup)#return this updated html
    except:
        return html_content
def add_link_ids(html, link):#link is used to add if we are referencing internals of this page or another page entirely
    soup = BeautifulSoup(html, 'html.parser')
    for i, tag in enumerate(soup.find_all('a'), start=1):
        if not tag.has_attr('id'):
            if tag.has_attr('href'):#add tags to the valid links that go to another site
                #we need to figure out if this link is referencing a page of the same site or another site
                tag['id'] = ensure_has_base_link(tag['href'], link)
    return str(soup)
def load_page(url):#loads the page, fully parsed with js, css, etc
    container = st.empty()#status updates
    with st.spinner("Loading site..."):
        with container.container():
            st.status("Loading HTML")
        html = get_html_from_site(url)#get html
        with container.container():
            st.status("Loading JS")
        html = inject_js_to_html(html, url)#inject js
        with container.container():
            st.status("Loading CSS")
        html = fetch_and_inject_css(html, url)#inject css
        with container.container():
            st.status("Adding Link IDs")
        html = add_link_ids(html, url)#add link ids for click detection
        st.session_state.html = html#update html
        st.session_state.url = url#make sure we are storing the right url of the page we're on
        st.rerun()#rerun
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
            #Turn those links into buttons that go to the webpage
            for link in links:
                c1, c2 = st.columns(2)
                with c1:
                    st.link_button("Open new tab (exits SkySearch) "+link["title"], link["href"])
                with c2:
                    text = "View Site within SkySearch ("+link["title"]+")"
                    if st.button(text, key = str(st.session_state.b_id)):
                        load_page(link["href"])
                    st.session_state.b_id += 1
        else:
            st.error("Search failed, likely due to a proxy failure or a lack of response from our search backend")
else:#we are now rendering the html
    spinner_slot = st.empty()
    if st.button("Back to search"):#back to search button, which must be above the html
        st.session_state.html = ""
        st.rerun()#go back to search
    st.caption("Game mode disables links, but allows games to function. It may help for other things like video playback")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Toggle game mode (Currently active: "+str(st.session_state.g_mode)+")"):#Allows games to work better if we use a different canvas type
            st.session_state.g_mode = not st.session_state.g_mode
            st.rerun()
    with c2:
        if st.button("Reload page"):
            load_page(st.session_state.url)
    if st.session_state.g_mode == False:
        click_id = click_detector(st.session_state.html)#render html and find clicks
        if click_id:
            print(click_id)
            with spinner_slot.container():
                load_page(click_id)
    else:
        st.components.v1.html(st.session_state.html, scrolling = True, height = 600)