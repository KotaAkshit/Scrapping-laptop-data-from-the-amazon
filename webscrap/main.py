from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Setup Chrome with custom user-agent
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36")
driver = webdriver.Chrome(options=options)

query = "laptop"

# Data storage
data = {
    'brand': [],
    'model': [],
    'screen_size': [],
    'color': [],
    'storage': [],
    'processor': [],
    'RAM': [],
    'os': [],
    'special_feature': [],
    'graphics': [],
    'price': []
}

product_links = []
prices = []

# Step 1: Collect product links and prices
for i in range(1, 30):  # Scrape pages 1 to 25
    print(f"\n🔍 Scraping search results page {i}")
    driver.get(f"https://www.amazon.in/s?k={query}&page={i}&crid=3GF5BIOO8QFKS&sprefix=laptop%2Caps%2C322&ref=nb_sb_noss_2")
    time.sleep(random.uniform(1.5, 3))  # Anti-throttling delay

    elems = driver.find_elements(By.CLASS_NAME, "puis-card-container")
    print(f"Found {len(elems)} products")

    for elem in elems:
        d = elem.get_attribute("outerHTML")
        soup = BeautifulSoup(d, "html.parser")

        link_tag = soup.find('a', class_='a-link-normal s-line-clamp-2 s-line-clamp-3-for-col-12 s-link-style a-text-normal')
        if link_tag and 'href' in link_tag.attrs:
            product_links.append("https://www.amazon.in" + link_tag['href'])

        price_tag = soup.find('span', class_='a-offscreen')
        prices.append(price_tag.text.strip() if price_tag else None)

# Step 2: Visit each product page and extract specs
for idx, link in enumerate(product_links):
    print(f"➡️ Scraping product {idx + 1} of {len(product_links)}")
    driver.get(link)
    time.sleep(random.uniform(1.5, 3))  # Anti-throttling delay

    row = {k: None for k in data.keys()}
    row['price'] = prices[idx]

    try:
        product_section = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "productOverview_feature_div"))
        )
        inner_html = product_section.get_attribute("outerHTML")
        soup = BeautifulSoup(inner_html, "html.parser")

        rows = soup.find_all("tr")
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 2:
                continue
            key_td = tds[0].get_text(strip=True)
            val_td = tds[1].get_text(strip=True)

            if "Brand" in key_td:
                row['brand'] = val_td
            elif "Model Name" in key_td:
                row['model'] = val_td
            elif "Screen Size" in key_td:
                row['screen_size'] = val_td
            elif "Colour" in key_td:
                row['color'] = val_td
            elif "Hard Disk Size" in key_td:
                row['storage'] = val_td
            elif "CPU Model" in key_td:
                row['processor'] = val_td
            elif "RAM Memory" in key_td:
                row['RAM'] = val_td
            elif "Operating System" in key_td:
                row['os'] = val_td
            elif "Special Feature" in key_td:
                row['special_feature'] = val_td
            elif "Graphics Card" in key_td:
                row['graphics'] = val_td
    except:
        print(f"⚠️ Specs not found for: {link}")

    for k in data.keys():
        data[k].append(row[k])

    # Auto-save every 100 products
    if (idx + 1) % 100 == 0:
        df = pd.DataFrame(data)
        df.to_csv(f"amazon_laptops_partial_{idx + 1}.csv", index=False)
        print(f"💾 Saved partial data at product {idx + 1}")

# Step 3: Final save
df = pd.DataFrame(data)
df.to_csv("amazon_laptops_final.csv", index=False)
print("\n✅ Scraping complete. Final data saved to amazon_laptops_final.csv")

# Cleanup
driver.quit()