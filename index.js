const axios = require("axios"),
  cheerio = require("cheerio"),
  express = require("express"),
  cors = require("cors"),
  app = express();
const fs = require("fs");
const { Cluster } = require("puppeteer-cluster");

app.use(express.json());
app.use(cors());

//READ Request Handlers
app.get("/", (req, res) => {
  res.status(200).send({
    response: "OK",
    message: "Mandi Details API",
    "api-routes": {
      "all-details": "/api",
    },
  });
});

// const headers = {
//   "User-Agent":
//     "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
//   Accept:
//     "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
//   "Accept-Encoding": "gzip, deflate, br, zstd",
//   "Accept-Language": "en-US,en;q=0.9",
//   "Cache-Control": "no-cache",
//   Pragma: "no-cache",
//   Referer: "https://www.google.com/",
//   "Sec-Fetch-Dest": "document",
//   "Sec-Fetch-Mode": "navigate",
//   "Sec-Fetch-Site": "none",
//   "Sec-Fetch-User": "?1",
//   "Upgrade-Insecure-Requests": "1",
//   Connection: "keep-alive",
// };

// app.get("/api", async (req, res) => {
//   mandiData = [];
//   const mainURL = "https://www.commodityonline.com/mandiprices/";
//   const urls = ["https://www.commodityonline.com/mandiprices/"];

//   let axios_requests = [];
//   axios_requests.push(axios.get(`${mainURL}`, { headers: headers }));

//   // for (let i = 1; i <= 10; ++i) {
//   //   axios_requests.push(
//   //     axios.get(`${mainURL}${36 * i}`, {
//   //       headers: {
//   //         "User-Agent":
//   //           "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
//   //         "Accept-Language": "en-US,en;q=0.9",
//   //         Accept:
//   //           "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
//   //         Referer: "https://www.google.com/",
//   //       },
//   //     })
//   //   );
//   // }

//   Promise.all([...axios_requests])
//     .then(function (results) {
//       for (let i = 0; i < results.length; ++i) {
//         console.log("hitted api: ", i);

//         const result = results[i].data;
//         let $ = cheerio.load(result);

//         $("#tdm_base_scroll > div > div.dt_ta_09").each(function (i, elm) {
//           let price = $("div.dt_ta_14", elm);
//           let newObject = {
//             commodity: $("div.dt_ta_10", elm).text().trim(),
//             marketCenter: $("div.dt_ta_11", elm)
//               .text()
//               .trim()
//               .replace("\n", ","),
//             variety: $("div.dt_ta_12", elm).text().trim(),
//             arrrivals: $("div.dt_ta_13", elm).text().trim(),
//             modalPrice: $(price[0]).text().trim(),
//             minMaxPrice: $(price[1]).text().trim().replace("\n", " "),
//           };
//           mandiData.push(newObject);
//         });
//       }

//       console.log("end");
//       res.status(200).send(mandiData);
//     })
//     .catch((err) => {
//       console.log(err);
//       res.status(400).send("error fetching");
//     });
// });

const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");

puppeteer.use(StealthPlugin());

// app.get("/api", async (req, res) => {
//   try {
//     const browser = await puppeteer.launch({
//       headless: true,
//       args: [
//         "--no-sandbox",
//         "--disable-setuid-sandbox",
//         "--disable-blink-features=AutomationControlled",
//       ],
//     });

//     const page = await browser.newPage();
//     await page.setUserAgent(
//       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
//     );

//     console.log(
//       "Navigating to:",
//       "https://www.commodityonline.com/mandiprices/"
//     );
//     await page.goto("https://www.commodityonline.com/mandiprices/", {
//       waitUntil: "networkidle2",
//       timeout: 0,
//     });

//     // Wait extra time for Cloudflare verification JS to finish
//     // await new Promise((resolve) => setTimeout(resolve, 8000));

//     // Check if human verification page is gone
//     const challenge = await page.$("iframe, #challenge-running, #cf-chl-cap");
//     if (challenge) {
//       console.log("⚠️ Cloudflare challenge still active!");
//       await page.screenshot({ path: "cf_challenge.png", fullPage: true });
//     }

//     // Wait for table
//     // await page.waitForSelector("#main-table2 tbody tr", { timeout: 2000 });

//     const data = await page.$$eval("#main-table2 tbody tr", (rows) => {
//       return rows.map((row) => {
//         const tds = Array.from(row.querySelectorAll("td"));
//         return {
//           commodity: tds[0]?.innerText.trim() || null,
//           commodityLink: tds[0]?.querySelector("a")?.href || null,
//           arrivalDate: tds[1]?.innerText.trim() || null,
//           variety: tds[2]?.innerText.trim() || null,
//           state: tds[3]?.innerText.trim() || null,
//           district: tds[4]?.innerText.trim() || null,
//           market: tds[5]?.innerText.trim() || null,
//           minPrice: tds[6]?.innerText.trim() || null,
//           maxPrice: tds[7]?.innerText.trim() || null,
//           avgPrice: tds[8]?.innerText.trim() || null,
//           mobileAppLink: tds[9]?.querySelector("a")?.href || null,
//         };
//       });
//     });

//     await browser.close();
//     res.status(200).json(data);
//   } catch (err) {
//     console.error("Error:", err.message);
//     res.status(500).send("Failed to fetch data");
//   }
// });

// app.get("/api", async (req, res) => {
//   try {
//     console.log("🚀 Starting mandi scraper...");

//     // Load markets.json file (the one you saved earlier)
//     const markets = JSON.parse(fs.readFileSync("markets.json", "utf-8"));

//     const browser = await puppeteer.launch({
//       headless: true,
//       args: [
//         "--no-sandbox",
//         "--disable-setuid-sandbox",
//         "--disable-blink-features=AutomationControlled",
//       ],
//     });

//     const page = await browser.newPage();
//     await page.setUserAgent(
//       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
//     );

//     const mandiData = [];

//     // 🔁 Loop through all markets
//     for (let i = 0; i < 5; i++) {
//       const market = markets[i];
//       const marketUrl = `https://www.commodityonline.com/mandiprices/market/${market.id}`;

//       console.log(`(${i + 1}/${markets.length}) Scraping: ${market.name}`);

//       try {
//         await page.goto(marketUrl, { waitUntil: "networkidle2", timeout: 0 });

//         // Wait extra time for JS/Cloudflare rendering
//         // await new Promise((r) => setTimeout(r, 500));

//         // Detect if blocked
//         const challenge = await page.$("#challenge-running, #cf-chl-cap");
//         if (challenge) {
//           console.log(`⚠️ Blocked by Cloudflare on ${market.id}, skipping.`);
//           await page.screenshot({ path: "cf_challenge.png", fullPage: true });
//           continue;
//         }

//         // Scrape table rows
//         const rowsData = await page.$$eval("#main-table2 tbody tr", (rows) => {
//           return rows.map((row) => {
//             const tds = Array.from(row.querySelectorAll("td"));
//             return {
//               commodity: tds[0]?.innerText.trim() || null,
//               commodityLink: tds[0]?.querySelector("a")?.href || null,
//               arrivalDate: tds[1]?.innerText.trim() || null,
//               variety: tds[2]?.innerText.trim() || null,
//               state: tds[3]?.innerText.trim() || null,
//               district: tds[4]?.innerText.trim() || null,
//               market: tds[5]?.innerText.trim() || null,
//               minPrice: tds[6]?.innerText.trim() || null,
//               maxPrice: tds[7]?.innerText.trim() || null,
//               avgPrice: tds[8]?.innerText.trim() || null,
//               mobileAppLink: tds[9]?.querySelector("a")?.href || null,
//             };
//           });
//         });

//         if (rowsData.length > 0) {
//           mandiData.push({
//             marketId: market.id,
//             marketName: market.name,
//             count: rowsData.length,
//             data: rowsData,
//           });
//           console.log(`✅ ${rowsData.length} rows scraped from ${market.name}`);
//         } else {
//           console.log(`⚠️ No rows found for ${market.name}`);
//         }

//         // Small delay between markets (prevent rate limiting)
//         await new Promise((r) => setTimeout(r, 2500));
//       } catch (err) {
//         console.log(`❌ Error scraping ${market.id}:`, err.message);
//       }
//     }

//     await browser.close();

//     // Save big JSON file
//     fs.writeFileSync("mandi_data.json", JSON.stringify(mandiData, null, 2));
//     console.log(
//       `💾 Saved all mandi data to mandi_data.json (${mandiData.length} markets)`
//     );

//     res.status(200).json({
//       success: true,
//       message: `Scraped ${mandiData.length} markets`,
//       outputFile: "mandi_data.json",
//     });
//   } catch (err) {
//     console.error("Error:", err.message);
//     res.status(500).send("Failed to fetch data");
//   }
// });

app.get("/api", async (req, res) => {
  try {
    console.log("🚀 Starting mandi scraper with Puppeteer Cluster...");

    // Load your markets file
    const all_markets = JSON.parse(fs.readFileSync("markets.json", "utf-8"));
    const markets = all_markets.slice(0, 10); // for testing, limit to first 10 markets
    // const mandiData = [];

    // 🔧 Launch Puppeteer Cluster
    const cluster = await Cluster.launch({
      puppeteer,
      concurrency: Cluster.CONCURRENCY_PAGE, // one tab per worker
      maxConcurrency: 20, // ⚙️ tweak this (5–20 is safe)
      timeout: 5 * 60 * 1000, // 5 minutes max per market
      puppeteerOptions: {
        headless: true,
        args: [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-blink-features=AutomationControlled",
        ],
      },
      monitor: true, // optional progress display in console
    });

    // 🎯 Define what each worker does
    await cluster.task(async ({ page, data: market }) => {
      const marketUrl = `https://www.commodityonline.com/mandiprices/market/${market.id}`;

      try {
        await page.setUserAgent(
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        );

        await page.goto(marketUrl, { waitUntil: "networkidle2", timeout: 0 });

        // Detect Cloudflare challenge
        const challenge = await page.$("#challenge-running, #cf-chl-cap");
        if (challenge) {
          console.log(`⚠️ Blocked by Cloudflare on ${market.name}, skipping.`);
          // return null;
        }

        // Scrape table rows
        const rowsData = await page.$$eval("#main-table2 tbody tr", (rows) => {
          return rows.map((row) => {
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
              avgPrice: tds[8]?.innerText.trim() || null,
            };
          });
        });

        if (rowsData.length === 0) {
          console.log(`⚠️ No data for ${market.name}`);
          return null;
        }

        console.log(`✅ Scraped ${rowsData.length} rows from ${market.name}`);

        return {
          marketId: market.id,
          marketName: market.name,
          count: rowsData.length,
          data: rowsData,
        };
      } catch (err) {
        console.log(`❌ Error scraping ${market.name}:`, err.message);
        return null;
      }
    });

    // 🧾 Queue all markets in parallel
    const results = await Promise.all(
      markets.map((market) => cluster.execute(market))
    );

    // Filter only valid ones
    const mandiData = results.filter(Boolean);

    await cluster.idle();
    await cluster.close();

    // 💾 Save results
    fs.writeFileSync("mandi_data.json", JSON.stringify(mandiData, null, 2));
    console.log(`💾 Saved mandi data (${mandiData.length} markets)`);

    res.json({
      success: true,
      message: `Scraped ${mandiData.length} markets using Puppeteer Cluster`,
      outputFile: "mandi_data.json",
    });
  } catch (err) {
    console.error("❌ Error:", err.message);
    res.status(500).send("Failed to scrape data");
  }
});

app.get("*", (req, res) => res.status(400).send("Wrong route use /api"));

//PORT ENVIRONMENT VARIABLE
const port = process.env.PORT || 8080;
app.listen(port, () => console.log(`Running API Server on ${port}..`));
