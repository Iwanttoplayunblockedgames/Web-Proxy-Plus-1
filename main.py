from urllib.parse import urlparse, urlunparse, urljoin

from bs4 import BeautifulSoup
import requests
from flask import Flask, Response, request

def clear():
  print("\n" * 100)

clear()

REAL_SITE = input("Enter a website: \n")
WT_STAT = "webproxyplus-static.pstatic.net"
WP_STAT = "webproxyplus-phinf.pstatic.net"
THIS_URL = "web-proxy-plus--replitcode.repl.co"

def replace_href(url, curr):
  print(url)
  if url.startswith("http://") or url.startswith("https://"):
    p_url = list(urlparse(url))
    print(p_url)
    if p_url[1] == WT_STAT:
      print("wt-stat detect")
      p_url[2] = "wt_stat" + p_url[2]
    elif p_url[1] == WP_STAT:
      print("wp-stat detect")
      p_url[2] = "wp_stat" + p_url[2]
    p_url[1] = THIS_URL
    print(p_url)
    print(urlunparse(p_url))
    return urlunparse(p_url)
  else:
    print(urljoin(curr, url))
    return urljoin(urljoin(THIS_URL, curr), url)

def get_content(url, curr):
  print("getting url", url)
  req = requests.get(url, headers={'referer': REAL_SITE})
  #print(url)
  if req.headers.get("Content-Type", "text/html").startswith("text/html"):
    html = req.text
    b = BeautifulSoup(html, "html.parser")
    for tag in b.findAll(href=True):
      print(tag["href"])
      tag["href"] = replace_href(tag["href"], curr)
    for tag in b.findAll(src=True):
      print(tag["src"])
      tag["src"] = replace_href(tag["src"], curr)
    for tag in b.findAll(attrs={"data-url": True}):
      print(tag["data-url"])
      tag["data-url"] = replace_href(tag["data-url"], curr)
    return b.prettify(), req.headers
  else:
    return req.content, req.headers

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  path = request.full_path[1:]
  #print("pth",path)
  if path.startswith("wt_stat/"):
    base = WT_STAT
    path = path[8:]
  elif path.startswith("wp_stat/"):
    base = WP_STAT
    path = path[8:]
  else:
    base = REAL_SITE
  text, head = get_content("http://" + base + "/" + path, path)
  resp = Response(text)
  resp.headers["Content-Type"] = head.get("Content-Type", "text/html")
  return resp

app.run(host="0.0.0.0")