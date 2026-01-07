import requests
from bs4 import BeautifulSoup
import networkx as nx
import matplotlib.pyplot as plt
import urllib.parse
import threading
from concurrent.futures import ThreadPoolExecutor
import time

# ---------------- CONFIG ----------------
MAX_DEPTH = 2
MAX_LINKS_PER_PAGE = 5
MAX_WORKERS = 5
TIMEOUT = 5

HEADERS = {
    "User-Agent": "LiveSiteMapperBot/1.0 (Educational)"
}

# ---------------------------------------

graph = nx.DiGraph()
visited = set()
lock = threading.Lock()

plt.ion()
fig, ax = plt.subplots(figsize=(14, 10))

def shorten(url):
    parsed = urllib.parse.urlparse(url)
    return parsed.path if parsed.path else "/"

def fetch_links(url, base_domain):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        soup = BeautifulSoup(r.text, "html.parser")

        links = []
        for a in soup.find_all("a", href=True):
            full = urllib.parse.urljoin(url, a["href"])
            parsed = urllib.parse.urlparse(full)

            if parsed.scheme.startswith("http") and parsed.netloc == base_domain:
                links.append(full)

        return links[:MAX_LINKS_PER_PAGE]
    except:
        return []

def draw_graph():
    ax.clear()
    pos = nx.spring_layout(graph, k=0.4, seed=42)
    nx.draw(
        graph,
        pos,
        ax=ax,
        with_labels=True,
        node_size=2000,
        node_color="skyblue",
        edge_color="gray",
        arrows=True,
        font_size=8
    )
    plt.pause(0.4)

def crawl(url, depth, base_domain, executor):
    if depth > MAX_DEPTH:
        return

    with lock:
        if url in visited:
            return
        visited.add(url)

    source = shorten(url)
    links = fetch_links(url, base_domain)

    for link in links:
        target = shorten(link)

        with lock:
            if not graph.has_edge(source, target):
                graph.add_edge(source, target)
                draw_graph()  # 🔴 REAL-TIME UPDATE

        executor.submit(crawl, link, depth + 1, base_domain, executor)

# ----------------- MAIN -----------------

start_url = input("Enter URL: ").strip()
parsed_start = urllib.parse.urlparse(start_url)
base_domain = parsed_start.netloc

graph.add_node(shorten(start_url))

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    crawl(start_url, 0, base_domain, executor)

plt.ioff()
plt.show()
