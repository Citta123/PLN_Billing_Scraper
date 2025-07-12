# cleanup.py

import os
import logging
import shutil

logger = logging.getLogger(__name__)


def cleanup_temp_files():
    """
    Menghapus file sementara dan direktori jika diperlukan.
    """
    temp_dir = os.path.join(os.getcwd(), 'temp')
    if os.path.exists(temp_dir):
        try:
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logging.info(f"Deleted temporary file: {file_path}")
            os.rmdir(temp_dir)
            logging.info(f"Deleted temporary directory: {temp_dir}")
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
    else:
        logging.info("No temporary files to clean up.")


def clear_cache(cache_file='token_cache.json'):
    """
    Menghapus file cache seperti token_cache.json.
    """
    if os.path.exists(cache_file):
        try:
            os.remove(cache_file)
            logger.info(f"Cache ({cache_file}) telah dihapus.")
        except Exception as e:
            logger.error(f"Error saat menghapus cache {cache_file}: {e}")


def clear_pycache():
    """
    Menghapus direktori __pycache__ di direktori utama dan di dalam folder modules.
    """
    pycache_dirs = [
        os.path.join(os.getcwd(), '__pycache__'),  # __pycache__ di direktori utama
        os.path.join(os.getcwd(), 'modules', '__pycache__')  # __pycache__ di dalam modules
    ]

    for pycache_dir in pycache_dirs:
        if os.path.exists(pycache_dir):
            try:
                shutil.rmtree(pycache_dir)
                logger.info(f"{pycache_dir} telah dihapus.")
            except Exception as e:
                logger.error(f"Error saat menghapus {pycache_dir}: {e}")
        else:
            logger.info(f"{pycache_dir} tidak ditemukan.")
