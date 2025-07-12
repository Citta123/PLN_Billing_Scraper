# ⚡ PLN Tagihan Scraper: Async Python Tool for Electric Bill Extraction and Excel Export

[![CI](https://github.com/Citta123/PLN_Tagihan_Scraper/actions/workflows/ci.yaml/badge.svg)](https://github.com/Citta123/PLN_Tagihan_Scraper/actions)

A modular, interactive, and high-performance Python tool designed to scrape PLN (state electricity company) billing data for customer IDs, and output consolidated Excel files. Built with `asyncio` and `aiohttp` to efficiently handle concurrent scraping tasks while providing clear logging and cleanup mechanisms.

---

## 🌟 Project Purpose

Many businesses, analysts, and field teams require timely access to PLN billing data for multiple customers:

* Manually inputting or copying billing data is **time-consuming and error-prone**.
* Handling dozens (or hundreds) of IDs means synchronous scraping is **too slow**.
* A **consolidated Excel report** simplifies downstream processing and analysis.

This tool automates the entire pipeline:

1. **Load** customer IDs from `.txt` or `.xlsx`.
2. **Scrape** billing data concurrently using PLN APIs.
3. **Export** results into a tidy Excel workbook.
4. **Cleanup** temporary activity logs and caches.

---

## 🚀 Key Features

* **🔣 Multi Format ID Input** – Reads customer IDs from plain text and Excel sheets automagically.
* **🌐 Async Web Scraping** – Uses `asyncio` and `aiohttp` for concurrent HTTP requests, boosting speed significantly.
* **📝 Interactive Prompt** – User chooses input file at runtime (no CLI flags needed).
* **📊 Excel Output** – Writes results to `output/data_tagihan_listrik_output.xlsx`.
* **🩼 Cleanup Module** – Deletes temporary files via `cleanup.py`.
* **🛠 Error Handling & Logging** – Robust logging for success/error per ID.

---

## 🧰 Project Structure

```
project_root/
├── main.py
├── modules/
│   ├── reader.py
│   ├── scraper.py
│   ├── writer.py
│   └── cleanup.py
├── IDPel/
│   ├── customer_ids.txt
│   └── customer_ids.xlsx
├── output/
│   └── data_tagihan_listrik_output.xlsx
├── tmp/
└── requirements.txt
```

---

## 🧠 Detailed Workflow Logic

1. **ID Loading** (`reader.py`):
   Uses `openpyxl` for `.xlsx` and standard file read for `.txt`, with trimming and deduplication.

2. **Async Scraping Setup** (`scraper.py`):

   * Builds tasks using `aiohttp.ClientSession`.
   * Executes `asyncio.gather(tasks, return_exceptions=True)` for concurrency.
   * Handles rate-limiting and retries gracefully.

3. **Response Parsing**:
   Extracts relevant fields (e.g., `meterNumber`, `token`, `tagihan`) from the PLN API response.

4. **Excel Writing** (`writer.py`):
   Aggregates results into a pandas DataFrame and saves to `output/data_tagihan_listrik_output.xlsx`.

5. **Cleanup** (`cleanup.py`):
   Removes `tmp/` folder and temporary logs post-process.

---

## 💪 Requirements

```bash
pip install aiohttp asyncio openpyxl pandas
```

---

## ⚙️ How to Run

```bash
python main.py
```

1. Select input file (`.txt` or `.xlsx`) from prompt.
2. Script shows progress and logs for each ID.
3. On completion, check `output/data_tagihan_listrik_output.xlsx`.

---

## 👨‍💻 About the Developer

I’m a freelance Python developer specializing in automation, data extraction, and web scraping.
This project demonstrates scalable async pipelines, concurrent HTTP integration, and structured Excel export.

💬 Interested in custom automation for your data workflows?
📩 Contact me at: [plusenergi77@gmail.com](mailto:plusenergi77@gmail.com)

---

## 📄 License

Licensed under the Apache License 2.0 – free to use, modify, and distribute with proper attribution.
