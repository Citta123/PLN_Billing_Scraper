# modules/scraper_handler.py

import logging
import asyncio


async def scrape_customer_data(
        scraper,
        customer_number,
        access_token,
        session,
        request_counts,
        global_request_count,
        non_retry_errors,
        max_retries=2,
        retry_delay=5):
    """
    Scrapes data for a given customer number with a retry mechanism.

    Parameters:
        scraper (ScraperAPI): Instance of ScraperAPI.
        customer_number (str): Customer ID.
        access_token (str): Access token for API.
        session (aiohttp.ClientSession): Session for making HTTP requests.
        request_counts (dict): Tracking request counts per customer.
        global_request_count (list): Tracking global request count.
        non_retry_errors (list): List of error messages that should not trigger retries.
        max_retries (int): Maximum number of retry attempts.
        retry_delay (int): Delay in seconds between retries.

    Returns:
        tuple: (customer_number, data) where data is the scraped data or a dict containing the error message.
    """
    attempt = 0
    while attempt <= max_retries:
        try:
            # Increment request counts
            request_counts[customer_number] = request_counts.get(customer_number, 0) + 1
            global_request_count[0] += 1

            logging.info(
                f"Memulai scraping untuk customer_number: {customer_number}, permintaan ke-{request_counts[customer_number]}, upaya ke-{attempt + 1}")

            # Scrape data
            data = await scraper.scrape_tagihan(customer_number, access_token, session)

            logging.info(f"Permintaan ke-{global_request_count[0]} untuk {customer_number} selesai.")

            # Cek apakah data valid
            if data and 'customer_number' in data:
                message = data.get('message', '').lower()
                # Jika ada pesan error yang termasuk non-retryable
                if any(error.lower() in message for error in non_retry_errors):
                    logging.warning(
                        f"Non-retryable error untuk {customer_number}: {data.get('message', 'Unknown error')}")
                    return customer_number, data
                else:
                    # Data valid tanpa error non-retryable
                    return customer_number, data
            else:
                # Data tidak valid, periksa apakah errornya retryable
                if data and 'message' in data:
                    message = data['message'].lower()
                    if any(error.lower() in message for error in non_retry_errors):
                        logging.warning(
                            f"Non-retryable error untuk {customer_number}: {data.get('message', 'Unknown error')}")
                        return customer_number, data
                    else:
                        logging.warning(
                            f"Retryable error untuk {customer_number}: {
                                data.get(
                                    'message', 'Unknown error')}")
                else:
                    logging.warning(f"Gagal scraping data untuk {customer_number}: Data tidak valid.")

            # Jika mencapai sini, berarti ada error yang bisa dicoba ulang
            attempt += 1
            if attempt > max_retries:
                logging.error(f"Max retries tercapai untuk {customer_number}. Menandai sebagai gagal.")
                return customer_number, {"message": "Max retries exceeded."}
            else:
                logging.info(f"Mencoba ulang scraping untuk {customer_number} dalam {retry_delay} detik...")
                await asyncio.sleep(retry_delay)

        except Exception as e:
            logging.error(f"Exception scraping data untuk {customer_number}: {e}")
            # Tentukan apakah exception ini retryable
            # Misalnya, network errors biasanya retryable
            if attempt < max_retries:
                logging.info(
                    f"Mencoba ulang scraping untuk {customer_number} dalam {retry_delay} detik karena exception.")
                attempt += 1
                await asyncio.sleep(retry_delay)
            else:
                logging.error(f"Max retries tercapai untuk {customer_number} karena exception.")
                return customer_number, {"message": str(e)}
