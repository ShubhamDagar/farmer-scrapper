const fs = require("fs");

try {
  // Load your scraped data
  const mandiData = JSON.parse(fs.readFileSync("mandi_data.json", "utf-8"));

  // Flatten all rows from each mandi into one list
  const flattened = mandiData.flatMap((market) =>
    market.data.map((row) => ({
      ...row,
      marketId: market.marketId,
      marketName: market.marketName,
    }))
  );

  // Save to a new file
  fs.writeFileSync("mandi_flat.json", JSON.stringify(flattened, null, 2));

  console.log(`✅ Flattened ${flattened.length} rows into mandi_flat.json`);
} catch (err) {
  console.error("❌ Error flattening data:", err.message);
}
