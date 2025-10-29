const axios = require("axios");
const cheerio = require("cheerio");
const fs = require("fs");

const headers = {
  "accept": "*/*",
  "accept-language": "en-US,en;q=0.9,hi;q=0.8",
  "priority": "u=1, i",
  "referer": "https://www.commodityonline.com/mandiprices/market/aabu-road",
  "sec-ch-ua": '"Google Chrome";v="141", "Not?A_Brand";v="8", "Chromium";v="141"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"macOS"',
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-origin",
  "user-agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
  "x-requested-with": "XMLHttpRequest",
  "cookie": "_ga=GA1.1.606475146.1761227984; ext_name=ojplmecpdpgccookcobabopnaifgidhf; __gads=ID=8199be8dc0dc72ff:T=1761227983:RT=1761730000:S=ALNI_MZk-bpSqaHOYFWfwMp4WRFsDfL2gQ; __gpi=UID=000011a7b3543ba7:T=1761227983:RT=1761730000:S=ALNI_MaqvYSRCcG87aBf2loyALKRi9A74g; __eoi=ID=ebcd14c4f563f78e:T=1761227983:RT=1761730000:S=AA-AfjY2QfQT7dCW8vZM34lZvuFE; _ga_R6BLX04KX4=GS2.1.s1761729998$o3$g1$t1761730144$j27$l0$h0; XSRF-TOKEN=eyJpdiI6ImhkcFB4aHpycTJFRHdVcHo4QXp6S2c9PSIsInZhbHVlIjoiNTJtaVFkeWkxK0dqdkxDOEg4Yk5WSmVySzg0UFVVN1FXL1ZhaC9rVGlPRmt3K0E4eGprUTNwaEFWb0hNY3RTT0d2dHdleWhqWGJteFo2U3NwS05qY3UrM2FtY0tnKzFHL1p0MElHRHQvL0R6c2s3R0RtTlMvZjF2Q0xENndjUkciLCJtYWMiOiJiOGZhOTlhM2NhMDQzMTc5NWM5YTQ3YjZmZDNlNWE3Mzg5MTQ0NThiYzY2ODIzNzRiYzExYmU1OWJkOWViNDFhIiwidGFnIjoiIn0%3D; laravel_session=eyJpdiI6InNxQm5XTVhsNE4xbDcxU3piOW5VNXc9PSIsInZhbHVlIjoiVm9xcFdTQnk2cU5OSFgzQi9EWDI2dWY1Tm5RczMzd2hKTHdPbi9DS0djWUJpQU9acUxyY2k2TmdKWHUyYnY4T0lBbTNWaVdXQ09HaENBak5iOXBMU3pKSjYwTHNyWnpQRzJScW1UUGdJQmMwNjBvL3U5TUZxbUJPQXFqYTR6M3IiLCJtYWMiOiJhZGI2ZDNkYTg3YWMxZDJjNjZlYjYxZGU3ZjExNzc1MmI1MDlmOWU0OGI5MDBhMmNhZTNlNjgzM2MwYTAxZjc5IiwidGFnIjoiIn0%3D"
};


(async () => {
  try {
    // Fetch the API that returns <option> HTML
    const { data } = await axios.get("https://www.commodityonline.com/mandiprices?state=all&commodity=all&_=1761730144445", { headers: headers });

    // Load it into Cheerio
    const $ = cheerio.load(data);

    // Parse all <option> tags
    const options = [];
    $("option").each((i, el) => {
      const id = $(el).attr("value")?.trim();
      const name = $(el).text().trim();

      // skip placeholders like "Select Market"
      if (id && id !== "") {
        options.push({ id, name });
      }
    });

    // Save to JSON file
    fs.writeFileSync("markets.json", JSON.stringify(options, null, 2));

    console.log("✅ Saved markets.json with", options.length, "entries");
  } catch (err) {
    console.error("❌ Error fetching:", err.message);
  }
})();
