import asyncio
from playwright.async_api import async_playwright
import pandas as pd
import json
import os

# ───────────────────────────────────────────────
# Scrape one market
# ───────────────────────────────────────────────
async def scrape_market_prices(context, market_id: int):
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
# Main logic
# ───────────────────────────────────────────────
async def main():
    # Read market IDs
    with open("ids", "r") as f:
        market_ids = [line.strip() for line in f if line.strip()]

    if not market_ids:
        print("No valid market IDs found in ids")
        return

    print(f"Loaded {len(market_ids)} market IDs.")

    os.makedirs("data", exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 1000},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/120.0.0.0 Safari/537.36"
        )

        # Limit concurrency to avoid overloading server
        SEMAPHORE = asyncio.Semaphore(20)

        async def limited_scrape(mid):
            async with SEMAPHORE:
                return await scrape_market_prices(context, mid)

        # Run all scrapes concurrently
        results = await asyncio.gather(*(limited_scrape(mid) for mid in market_ids))

        await browser.close()

    # Flatten all results
    all_data = [row for dataset in results for row in dataset]

    # Save to JSON and CSV
    if all_data:
        json_path = "data/all_markets_prices.json"
        csv_path = "data/all_markets_prices.csv"

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\nSaved combined JSON data to {json_path}")

        df = pd.DataFrame(all_data)
        df.to_csv(csv_path, index=False)
        print(f"Saved combined CSV data to {csv_path}")
    else:
        print("No data scraped.")


if __name__ == "__main__":
    asyncio.run(main())
