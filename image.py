from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

class MirrorHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        website_url = "http://chat.openai.com"
        website_content = self.mirror_website(website_url)
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(website_content.encode('utf-8'))

    def mirror_website(self, url):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                response.encoding = 'utf-8'  # 设置响应的编码为UTF-8
                website_content = response.text
                fixed_content = self.fix_relative_paths(url, website_content)
                return fixed_content
            else:
                print("Failed to retrieve the website. Status code:", response.status_code)
        except requests.exceptions.RequestException as e:
            print("An error occurred:", str(e))

    def fix_relative_paths(self, base_url, content):
        parsed_url = urlparse(base_url)
        base_path = parsed_url.scheme + "://" + parsed_url.netloc

        soup = BeautifulSoup(content, 'html.parser')

        # Fix image src attributes
        for img in soup.find_all('img'):
            img_src = img.get('src')
            if img_src and not img_src.startswith(('http://', 'https://')):
                img['src'] = urljoin(base_path, img_src)

        # Fix link href attributes
        for link in soup.find_all('link'):
            link_href = link.get('href')
            if link_href and not link_href.startswith(('http://', 'https://')):
                link['href'] = urljoin(base_path, link_href)

        # Fix script src attributes
        for script in soup.find_all('script'):
            script_src = script.get('src')
            if script_src and not script_src.startswith(('http://', 'https://')):
                script['src'] = urljoin(base_path, script_src)

        return str(soup)

def run_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, MirrorHandler)
    print('Starting server...')
    httpd.serve_forever()

run_server()
