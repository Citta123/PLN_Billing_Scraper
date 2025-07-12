# modules/utils.py

import os
import logging
from datetime import datetime

# Konfigurasi untuk BL Awal dan BL Akhir pada sheet TUL
BL_CONFIG = {
    "BL_AKHIR": "DES-2024",  # Untuk semua Baris pada kolom BL Akhir
    "BL_AWAL": {
        "1": "DES-2024",  # Untuk kolom BL Awal dengan kategori LBR (1)
        "2": "NOV-2024",  # Untuk kolom BL Awal dengan kategori LBR (2)
        "3": "OKT-2024"   # Untuk kolom BL Awal dengan kategori LBR (3)
    }
}

# Konfigurasi Tambahan untuk kolom RPTAG pada sheet TUL
RPTAG_ADDITIONS = {
    "Dalbo.xlsx": 10000,
    "JAB.xlsx": 5000,
    "JAK.xlsx": 4000,
    "kherudin.xlsx": 12000,
    "Sukron.xlsx": 15000
}


def setup_logging():
    log_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'scraper.log')
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging telah dikonfigurasi dengan benar.")


def get_month_name(date_str):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        month_names = ["Januari", "Februari", "Maret", "April", "Mei", "Juni",
                       "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
        return month_names[date_obj.month - 1]
    except Exception as e:
        logging.error(f"Error saat mengonversi bulan dari tanggal {date_str}: {e}")
        return date_str


def format_number(value):
    try:
        return int(value.replace('.', '').replace(',', ''))
    except ValueError:
        return 0


def get_bl_akhir():
    """
    Mengembalikan nilai BL_AKHIR dari konfigurasi.

    Returns:
        str: Nilai BL_AKHIR.
    """
    return BL_CONFIG.get("BL_AKHIR", "Unknown")


def get_bl_awal(lbr_category):
    """
    Mengembalikan nilai BL_AWAL berdasarkan kategori LBR.

    Parameters:
        lbr_category (int): Kategori LBR sebagai integer (misalnya, 1, 2, 3).

    Returns:
        str: Nilai BL_AWAL yang sesuai atau "Unknown" jika kategori tidak ditemukan.
    """
    return BL_CONFIG["BL_AWAL"].get(str(lbr_category), "Unknown")


def get_rptag_addition(source_file):
    """
    Mengembalikan nilai tambahan untuk RPTAG berdasarkan nama file sumber.

    Parameters:
        source_file (str): Nama file sumber (misalnya, "Dalbo.xlsx").

    Returns:
        int: Nilai tambahan untuk RPTAG atau 0 jika file tidak ditemukan.
    """
    return RPTAG_ADDITIONS.get(source_file, 0)
