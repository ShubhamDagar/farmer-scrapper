from flask import Flask, jsonify
import asyncio
import json
import os
from playwright.async_api import async_playwright

app = Flask(__name__)


async def scrape_market_prices(context, market):
    """Scrape mandi data for one market entry (marketId, marketName)."""
    market_id = market["marketId"]
    #  market_name = market["marketName"]
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


async def scrape_all_markets(markets):
    """Scrape all markets in parallel with limited concurrency."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )

        semaphore = asyncio.Semaphore(20)

        async def limited_scrape(m):
            async with semaphore:
                return await scrape_market_prices(context, m)

        results = await asyncio.gather(*(limited_scrape(m) for m in markets))
        await browser.close()
        return results


@app.route("/scrape", methods=["GET"])
def scrape_endpoint():
    """Scrape all markets defined in markets.json and return as JSON."""
    json_file = "mandi_data.json"

    if not os.path.exists(json_file):
        return jsonify({"error": f"{json_file} not found"}), 404

    with open(json_file, "r", encoding="utf-8") as f:
        markets = json.load(f)

    if not isinstance(markets, list):
        return jsonify({"error": "markets.json must contain a list of market objects"}), 400

    try:
        result = asyncio.run(scrape_all_markets(markets))
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
