import json
import os
import logging
import aiohttp
import time
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class ScraperAPI:
    BASE_URL = "https://www.bukalapak.com/"
    API_URL = "https://api.bukalapak.com/"
    CACHE_FILE = 'token_cache.json'
    TOKEN_EXPIRY_TIME = timedelta(hours=1)
    MAX_RETRIES = 2
    RETRY_DELAY = 3
    MAX_RETRY_FOR_EMPTY_RESPONSE = 3

    def __init__(self):
        self.access_token = None

    def _load_token_from_cache(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    token_time = datetime.strptime(cache_data['timestamp'], "%Y-%m-%dT%H:%M:%S")
                    if datetime.now() - token_time < self.TOKEN_EXPIRY_TIME:
                        logger.info("Menggunakan token dari cache.")
                        return cache_data['access_token']
                    else:
                        logger.warning("Token telah kadaluarsa.")
            except Exception as e:
                logger.error(f"Error saat memuat token dari cache: {e}")
        return None

    def _save_token_to_cache(self, token):
        try:
            cache_data = {
                'access_token': token,
                'timestamp': datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            }
            with open(self.CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f)
            logger.info("Token berhasil disimpan ke cache.")
        except Exception as e:
            logger.error(f"Error saat menyimpan token ke cache: {e}")

    def _clear_token_cache(self):
        if os.path.exists(self.CACHE_FILE):
            try:
                os.remove(self.CACHE_FILE)
                logger.info("Cache token dihapus.")
            except Exception as e:
                logger.error(f"Error menghapus cache: {e}")

    def _is_token_near_expiry(self, margin_minutes=5):
        if os.path.exists(self.CACHE_FILE):
            with open(self.CACHE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                token_time = datetime.strptime(data['timestamp'], "%Y-%m-%dT%H:%M:%S")
                remaining = self.TOKEN_EXPIRY_TIME - (datetime.now() - token_time)
                return remaining < timedelta(minutes=margin_minutes)
        return True

    async def get_access_token(self, url, session):
        self.access_token = self._load_token_from_cache()
        if self.access_token and self._is_token_near_expiry():
            logger.info("Token hampir kadaluarsa. Memperbarui token...")
            self._clear_token_cache()
            self.access_token = None

        if not self.access_token:
            try:
                async with session.get(self.BASE_URL + url, timeout=60) as response:
                    if response.status == 200:
                        text = await response.text()
                        start = text.find("localStorage.setItem('bl_token', '")
                        if start != -1:
                            start += len("localStorage.setItem('bl_token', '")
                            end = text.find("');", start)
                            token_str = text[start:end]
                            try:
                                access_token_data = json.loads(token_str)
                                self.access_token = access_token_data.get('access_token')
                                if self.access_token:
                                    self._save_token_to_cache(self.access_token)
                                else:
                                    logger.error("Access token tidak ditemukan.")
                            except json.JSONDecodeError:
                                logger.error("JSONDecodeError saat memuat access token.")
                        else:
                            logger.error("Access token tidak ditemukan dalam halaman.")
                    else:
                        logger.error("Halaman token tidak dapat diakses.")
            except Exception as e:
                logger.error(f"Error saat mencoba mendapatkan access token: {e}")

        return self.access_token

    async def scrape_tagihan(self, customer_number, access_token, session, retries=0, empty_response_retries=0):
        try:
            async with session.post(
                f"{self.API_URL}electricities/postpaid-inquiries",
                params={"access_token": access_token},
                json={"customer_number": customer_number},
                timeout=60
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    data_api = data.get('data', {})
                    if data_api:
                        return data_api
                    else:
                        if empty_response_retries < self.MAX_RETRY_FOR_EMPTY_RESPONSE:
                            time.sleep(self.RETRY_DELAY)
                            return await self.scrape_tagihan(customer_number, access_token, session, retries, empty_response_retries + 1)
                        else:
                            return {"status": False, "message": "Data kosong"}
                else:
                    try:
                        data = await resp.json()
                        error_message = data.get('errors', [{'message': 'Unknown error'}])[0]['message']
                    except BaseException:
                        error_message = "Unknown error"

                    if "Invalid Oauth Token" in error_message:
                        self._clear_token_cache()
                        new_token = await self.get_access_token("listrik-pln/tagihan-listrik", session)
                        if new_token:
                            return await self.scrape_tagihan(customer_number, new_token, session, retries, empty_response_retries)
                        else:
                            return {"status": False, "message": "Gagal memperbarui token"}

                    if retries < self.MAX_RETRIES and "Unexpected error" in error_message:
                        time.sleep(self.RETRY_DELAY)
                        return await self.scrape_tagihan(customer_number, access_token, session, retries + 1, empty_response_retries)

                    return {"status": False, "message": f"Error: {error_message}"}
        except Exception as e:
            logger.error(f"Error saat scraping data untuk {customer_number}: {e}")
            return {"status": False, "message": f"Error: {str(e)}"}
