# main.py

import os
import logging
import asyncio
import aiohttp
from datetime import datetime

from modules.utils import setup_logging, get_bl_akhir, get_bl_awal, get_rptag_addition
from modules.loader import load_customer_numbers_from_files, load_customer_numbers_xlsx
from modules.excel_writer import create_excel
from modules.scraper_handler import scrape_customer_data
from modules.scraper_api import ScraperAPI

# Import fungsi cleanup
from cleanup import cleanup_temp_files, clear_cache, clear_pycache


async def main():
    setup_logging()
    scraper = ScraperAPI()

    folder_path = os.path.join(os.getcwd(), 'IDPel')
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        logging.error(f"Folder {folder_path} tidak ditemukan atau bukan folder.")
        return

    # List semua file .txt dan .xlsx di folder IDPel
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.txt') or f.endswith('.xlsx')]
    if not all_files:
        logging.error("Tidak ada file .txt atau .xlsx yang ditemukan di folder IDPel.")
        return

    print("\n=== Daftar File di Folder IDPel ===")
    for idx, file_name in enumerate(all_files, 1):
        print(f"{idx}. {file_name}")
    print("===================================\n")

    # Meminta pengguna untuk memilih file berdasarkan nomor
    selected_indices = input("Masukkan nomor file yang ingin diproses (pisahkan dengan koma jika lebih dari satu): ")
    try:
        selected_indices = [int(i.strip()) for i in selected_indices.split(',') if i.strip().isdigit()]
        if not selected_indices:
            logging.error("Tidak ada file yang dipilih untuk diproses.")
            return

        selected_files = [all_files[i - 1] for i in selected_indices if 0 < i <= len(all_files)]
        if not selected_files:
            logging.error("Tidak ada file yang valid dipilih untuk diproses.")
            return
    except Exception as e:
        logging.error(f"Input tidak valid: {e}")
        return

    # Memuat data tambahan dari semua file .xlsx yang dipilih
    file_data_map = {}
    for selected_file in selected_files:
        selected_file_path = os.path.join(folder_path, selected_file)
        if selected_file_path.endswith('.xlsx'):
            file_data_map.update(load_customer_numbers_xlsx(selected_file_path))

    async with aiohttp.ClientSession() as session:
        access_token_url = "listrik-pln/tagihan-listrik"
        access_token = await scraper.get_access_token(access_token_url, session)
        if not access_token:
            logging.error("Gagal mendapatkan access token. Program dihentikan.")
            return

        output_dir = os.path.join(os.getcwd(), 'output')
        os.makedirs(output_dir, exist_ok=True)

        # Mengatur output file name
        output_file_name = "data_tagihan_listrik_output.xlsx"
        output_file = os.path.join(output_dir, output_file_name)

        # Data yang berhasil di-scrape
        success_data = []
        failed_data = []
        all_periods = set()

        # Definisikan error yang non-retryable
        non_retry_errors = [
            "nomor tidak terdaftar. coba periksa lagi, yuk.",
            "tagihan tidak ditemukan atau sudah dibayar.",
            "tidak terdaftar",
            "tagihan tidak ditemukan"
            # Tambahkan error lain yang tidak ingin Anda retry
        ]

        for selected_file in selected_files:
            selected_file_path = os.path.join(folder_path, selected_file)
            file_name = os.path.basename(selected_file_path)
            logging.info(f"Memproses file: {file_name}")

            customer_numbers, customer_sources = load_customer_numbers_from_files(selected_file_path)
            if not customer_numbers:
                logging.warning(f"Tidak ada customer numbers yang ditemukan dalam file {file_name}.")
                continue

            # Proses scraping untuk setiap ID pelanggan dalam file saat ini
            tasks = [
                scrape_customer_data(
                    scraper,
                    customer,
                    access_token,
                    session,
                    {},  # request_counts
                    [0],  # global_request_count
                    non_retry_errors,  # non_retry_errors
                    max_retries=2,  # jumlah maksimal retry
                    retry_delay=5    # delay antar retry (dalam detik)
                )
                for customer in customer_numbers
            ]
            results = await asyncio.gather(*tasks)

            # Validasi hasil
            for result in results:
                if not isinstance(result, tuple) or len(result) != 2:
                    logging.error(f"Unexpected result format: {result}")
                    continue
                customer_number, data = result
                if data and 'customer_number' in data:
                    # Tambahkan source_file jika ada
                    index = customer_numbers.index(customer_number)
                    data['source_file'] = os.path.basename(customer_sources[index])
                    success_data.append(data)
                    for bill in data.get("bills", []):
                        all_periods.add(bill.get("bill_period"))
                else:
                    # Tambahkan source_file dan ekstrak pesan error
                    index = customer_numbers.index(customer_number)
                    source_file = os.path.basename(customer_sources[index])
                    error_message = "Gagal scraping"  # Default message
                    # Cek apakah data memiliki pesan error yang spesifik
                    if isinstance(data, dict) and 'message' in data:
                        if data['message'].startswith("Error: "):
                            error_message = data['message'].split("Error: ", 1)[1]
                        else:
                            error_message = data['message']
                    failed_data.append({
                        "customer_number": customer_number,
                        "error": error_message,
                        "source_file": source_file
                    })

        # Tambahkan nilai tambahan dan markup
        for record in success_data:
            source = record.get("source_file", "")
            tambahan = file_data_map.get(source, 0)
            record['tambahan'] = tambahan
            tagihan = sum(bill.get("amount", 0) for bill in record.get("bills", []))
            record['markup'] = tagihan + tambahan

        periods = sorted(all_periods, key=lambda x: datetime.strptime(x, "%Y-%m-%d")) if all_periods else []

        # Menulis hasil ke file Excel
        create_excel(success_data, failed_data, periods, output_file, file_data_map)

    # Jalankan cleanup setelah proses selesai
    cleanup_temp_files()
    clear_cache()
    clear_pycache()

if __name__ == "__main__":
    asyncio.run(main())
