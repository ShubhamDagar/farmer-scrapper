import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import os
from flask import Flask, jsonify, request
import time, os
from utilites.plotting_test import plotting
app = Flask(__name__)

MANDI_ID_FILE = "mandi_ids.txt"

# ───────────────────────────────────────────────
# Scrape one market
# ───────────────────────────────────────────────
async def scrape_market_prices(context, market_id: str):
    """Scrape mandi data for a single market ID."""
    url = f"https://www.commodityonline.com/mandiprices/market/{market_id}"
    print(f"Fetching: {url}")

    page = await context.new_page()
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        await page.wait_for_selector("#main-table2 tbody tr", timeout=15000)

        rows_data = await page.evaluate("""
        () => {
            const rows = document.querySelectorAll("#main-table2 tbody tr");
            return Array.from(rows).map(row => {
                const tds = Array.from(row.querySelectorAll("td"));
                return {
                    commodity: tds[0]?.innerText.trim() || null,
                    arrivalDate: tds[1]?.innerText.trim() || null,
                    variety: tds[2]?.innerText.trim() || null,
                    state: tds[3]?.innerText.trim() || null,
                    district: tds[4]?.innerText.trim() || null,
                    market: tds[5]?.innerText.trim() || null,
                    minPrice: tds[6]?.innerText.trim() || null,
                    maxPrice: tds[7]?.innerText.trim() || null,
                    avgPrice: tds[8]?.innerText.trim() || null
                };
            });
        }
        """)

        for row in rows_data:
            row["market_id"] = market_id

        print(f"Market {market_id}: {len(rows_data)} rows")
        return rows_data

    except Exception as e:
        print(f"Error scraping market {market_id}: {e}")
        return []
    finally:
        await page.close()


# ───────────────────────────────────────────────
# Flask endpoint to trigger scraping
# ───────────────────────────────────────────────
@app.route("/scrape")
async def scrape_all():
    """Flask endpoint to scrape all market pages from a list of string IDs."""
    if not os.path.exists(MANDI_ID_FILE):
        return jsonify({"error": "File 'ids' not found"}), 400

    # Read market IDs as strings
    with open(MANDI_ID_FILE, "r", encoding="utf-8") as f:
        market_ids = [line.strip() for line in f if line.strip()]

    if not market_ids:
        return jsonify({"error": "No valid market IDs found"}), 400

    print(f"Loaded {len(market_ids)} market IDs")

    os.makedirs("data", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        SEMAPHORE = asyncio.Semaphore(10)  # limit concurrency

        async def limited_scrape(mid: str):
            async with SEMAPHORE:
                return await scrape_market_prices(context, mid)

        results = await asyncio.gather(*(limited_scrape(mid) for mid in market_ids))
        await browser.close()

    # Flatten list of lists
    all_data = [row for dataset in results for row in dataset]

    if all_data:
        ts = str(int(time.time()))
        json_path = "data/" + ts + "_all_markets_prices.json"
        csv_path = "data/" + ts + "_all_markets_prices.csv"

        # Save JSON
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        # Save CSV
        pd.DataFrame(all_data).to_csv(csv_path, index=False)

        print(f"Saved {len(all_data)} rows to {json_path}")
        return jsonify({
            "message": "Scraping completed successfully",
            "count": len(all_data),
            "saved_json": json_path,
            "saved_csv": csv_path
        })

    else:
        return jsonify({"message": "No data scraped"}), 500
    
@app.route("/api")
async def return_data():
    directory = "./data/"
    files = os.listdir(directory)
    highest = max(files)
    print(highest)
    ts = highest.split('_')[0]

    with open(directory + highest, "r", encoding="utf-8") as f:
        data = json.load(f)
    

    return jsonify({
        "data": data,
        "timestamp" : ts
    })

@app.post("/api/generate-charts")
def generate_charts():
    # data = request.json
    data = {"commodity": "Wheat",
      "state": "Punjab",
      "market": "Ludhiana"}
    commodity = data["commodity"]
    state = data["state"]
    market = data["market"]
    return plotting(commodity, state, market)


if __name__ == "__main__":
    app.run(debug=True)
