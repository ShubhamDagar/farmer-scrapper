import asyncio
import pandas as pd
import json
import os
from flask import Flask, jsonify, request
import time, os
from utilites.plotting_test import plotting
from flask_cors import CORS

app = Flask(__name__)
CORS(
    app,
    resources={r"/*": {
        "origins": [
            "http://localhost:3000",
            "https://farmerportal-2xfo.onrender.com"
        ]
    }},
    supports_credentials=True
)

MANDI_ID_FILE = "mandi_ids.txt"


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

    results = []

    # async with async_playwright() as p:
    #     browser = await p.chromium.launch(headless=True)
    #     context = await browser.new_context(
    #         viewport={"width": 1280, "height": 1000},
    #         user_agent=(
    #             "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #             "AppleWebKit/537.36 (KHTML, like Gecko) "
    #             "Chrome/120.0.0.0 Safari/537.36"
    #         )
    #     )

    #     SEMAPHORE = asyncio.Semaphore(10)  # limit concurrency

    #     async def limited_scrape(mid: str):
    #         async with SEMAPHORE:
    #             return await scrape_market_prices(context, mid)

    #     results = await asyncio.gather(*(limited_scrape(mid) for mid in market_ids))
    #     await browser.close()

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
    
@app.get("/api")
def return_data():
    directory = "./data/"
    files = os.listdir(directory)
    highest = max(files)
    print(highest)
    ts = highest.split('_')[0]

    with open(directory + highest, "r", encoding="utf-8") as f:
        data = json.load(f)

    unique_combinations = set()
    unique_data = []
    for item in data:
        unique_key = (item["commodity"], item["market_id"]
                    #   , item["variety"]
                      )

        if unique_key not in unique_combinations:
            unique_combinations.add(unique_key)
            unique_data.append(item)

    return jsonify({
        "data": unique_data,
        "timestamp" : ts
    })

@app.post("/api/generate-charts")
def generate_charts():
    data = request.json
    commodity = data["commodity"]
    state = data["state"]
    market = data["market"]
    plots = plotting(commodity, state, market)

    return json.dumps(plots)

if __name__ == "__main__":
    app.run(port=5002, debug=True)
