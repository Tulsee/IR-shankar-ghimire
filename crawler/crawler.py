#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse, json, os, time, re, logging, random, asyncio
from math import ceil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import threading
from collections import deque

# Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException,
    StaleElementReferenceException,
)
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Parallelism
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("crawler.log"), logging.StreamHandler()],
)

BASE_URL = (
    "https://pureportal.coventry.ac.uk/en/organisations/"
    "fbl-school-of-economics-finance-and-accounting/publications/"
)


# =========================== Performance Monitoring ===========================
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.stage_times = {}
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        self.rate_history = deque(maxlen=10)
        self.lock = threading.Lock()

    def start_stage(self, stage_name: str):
        with self.lock:
            self.stage_times[stage_name] = time.time()

    def end_stage(self, stage_name: str):
        with self.lock:
            if stage_name in self.stage_times:
                duration = time.time() - self.stage_times[stage_name]
                logging.info(f"[PERF] {stage_name} completed in {duration:.2f}s")
                return duration

    def record_success(self):
        with self.lock:
            self.processed_count += 1
            self.success_count += 1
            self._update_rate()

    def record_error(self):
        with self.lock:
            self.processed_count += 1
            self.error_count += 1
            self._update_rate()

    def _update_rate(self):
        elapsed = time.time() - self.start_time
        if elapsed > 0:
            rate = self.processed_count / elapsed
            self.rate_history.append(rate)

    def get_stats(self) -> Dict:
        with self.lock:
            elapsed = time.time() - self.start_time
            avg_rate = (
                sum(self.rate_history) / len(self.rate_history)
                if self.rate_history
                else 0
            )
            return {
                "elapsed": elapsed,
                "processed": self.processed_count,
                "success": self.success_count,
                "errors": self.error_count,
                "success_rate": (
                    (self.success_count / self.processed_count * 100)
                    if self.processed_count > 0
                    else 0
                ),
                "items_per_second": avg_rate,
                "estimated_remaining": 0,
            }


# Global performance monitor
perf_monitor = PerformanceMonitor()


# =========================== Caching System ===========================
class SimpleCache:
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.access_times = {}
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Dict]:
        with self.lock:
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key]
            return None

    def set(self, key: str, value: Dict):
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Remove oldest accessed item
                oldest_key = min(
                    self.access_times.keys(), key=lambda k: self.access_times[k]
                )
                del self.cache[oldest_key]
                del self.access_times[oldest_key]

            self.cache[key] = value
            self.access_times[key] = time.time()


# Global cache for failed/processed URLs
url_cache = SimpleCache()


# =========================== Chrome helpers ===========================
def build_chrome_options(
    headless: bool, legacy_headless: bool = False, fast_mode: bool = False
) -> Options:
    opts = Options()
    if headless:
        opts.add_argument("--headless" + ("" if legacy_headless else "=new"))

    # Basic options
    opts.add_argument("--window-size=1366,768")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--no-first-run")
    opts.add_argument("--no-default-browser-check")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")

    # Performance optimizations
    opts.add_argument("--disable-renderer-backgrounding")
    opts.add_argument("--disable-backgrounding-occluded-windows")
    opts.add_argument("--disable-features=CalculateNativeWinOcclusion,MojoVideoDecoder")
    opts.add_argument("--disable-ipc-flooding-protection")
    opts.add_argument("--disable-web-security")
    opts.add_argument("--disable-features=VizDisplayCompositor")

    # Fast mode optimizations
    if fast_mode:
        opts.add_argument("--disable-images")
        opts.add_argument("--disable-javascript")
        opts.add_argument("--disable-plugins")
        opts.add_argument("--disable-java")
        opts.add_argument("--disable-css")
        opts.add_argument("--aggressive-cache-discard")
        opts.add_argument("--memory-pressure-off")
        opts.page_load_strategy = "none"  # Don't wait for full page load
    else:
        opts.page_load_strategy = "eager"

    # Anti-detection measures
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option(
        "excludeSwitches", ["enable-logging", "enable-automation"]
    )
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--disable-logging")
    opts.add_argument("--log-level=3")
    opts.add_argument("--silent")

    # Updated User-Agent for 2025
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    )

    # Additional prefs to reduce fingerprinting and improve performance
    prefs = {
        "profile.default_content_setting_values": {
            "notifications": 2,
            "media_stream": 2,
        },
        "profile.managed_default_content_settings": {"images": 2 if fast_mode else 1},
        "profile.default_content_settings.popups": 0,
        "managed_default_content_settings.images": 2 if fast_mode else 1,
    }
    opts.add_experimental_option("prefs", prefs)

    return opts


def make_driver(
    headless: bool,
    legacy_headless: bool = False,
    fast_mode: bool = False,
    timeout: int = 15,
) -> webdriver.Chrome:
    """Create and configure a Chrome WebDriver instance with enhanced anti-detection."""
    try:
        service = ChromeService(ChromeDriverManager().install(), log_output=os.devnull)
        driver = webdriver.Chrome(
            service=service,
            options=build_chrome_options(headless, legacy_headless, fast_mode),
        )
        driver.set_page_load_timeout(timeout)  # Reduced from 45s to configurable

        # Enhanced anti-detection scripts
        try:
            # Hide webdriver property
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined,
                });
                """
                },
            )

            # Randomize screen resolution and other properties
            driver.execute_cdp_cmd(
                "Page.addScriptToEvaluateOnNewDocument",
                {
                    "source": """
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en'],
                });
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5],
                });
                """
                },
            )
        except Exception as e:
            logging.warning(f"Could not execute CDP commands: {e}")

        return driver
    except Exception as e:
        logging.error(f"Failed to create driver: {e}")
        raise


def accept_cookies_if_present(driver: webdriver.Chrome):
    """Accept cookies banner if present."""
    try:
        btn = WebDriverWait(driver, 3).until(  # Reduced from 6s to 3s
            EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
        )
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(0.1)  # Reduced from 0.25s
        logging.debug("Accepted cookies banner")
    except TimeoutException:
        logging.debug("No cookies banner found")
    except Exception as e:
        logging.warning(f"Error handling cookies banner: {e}")


def smart_delay(base_delay: float, variance: float = 0.3, fast_mode: bool = False):
    """Add intelligent delay based on mode and recent performance."""
    if fast_mode:
        base_delay *= 0.3  # Reduce delays in fast mode

    # Adaptive delay based on error rate
    stats = perf_monitor.get_stats()
    if stats["processed"] > 10:
        error_rate = stats["errors"] / stats["processed"]
        if error_rate > 0.1:  # If >10% error rate, slow down
            base_delay *= 1.5
        elif error_rate < 0.02:  # If <2% error rate, speed up
            base_delay *= 0.7

    delay = base_delay + random.uniform(-variance, variance)
    time.sleep(max(0.05, delay))  # Minimum 50ms delay


# =========================== LISTING (Stage 1) ===========================
def scrape_listing_page(
    driver: webdriver.Chrome, page_idx: int, max_retries: int = 3
) -> List[Dict]:
    """Scrape a single listing page with retry logic."""
    url = f"{BASE_URL}?page={page_idx}"

    for attempt in range(max_retries):
        try:
            logging.info(f"Scraping listing page {page_idx + 1}, attempt {attempt + 1}")
            driver.get(url)
            smart_delay(1.0, 0.5)  # Smart delay after page load

            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.find_elements(
                        By.CSS_SELECTOR, ".result-container h3.title a"
                    )
                    or "No results" in d.page_source
                )
            except TimeoutException:
                logging.warning(f"Timeout waiting for page {page_idx + 1} to load")

            cards = driver.find_elements(By.CLASS_NAME, "result-container")
            rows: List[Dict] = []

            for i, c in enumerate(cards):
                try:
                    a = c.find_element(By.CSS_SELECTOR, "h3.title a")
                    title = a.text.strip()
                    link = a.get_attribute("href")
                    if title and link:
                        rows.append({"title": title, "link": link})
                except (NoSuchElementException, StaleElementReferenceException) as e:
                    logging.warning(
                        f"Error extracting card {i} on page {page_idx + 1}: {e}"
                    )
                    continue
                except Exception as e:
                    logging.error(
                        f"Unexpected error on card {i} on page {page_idx + 1}: {e}"
                    )
                    continue

            logging.info(
                f"Successfully extracted {len(rows)} items from page {page_idx + 1}"
            )
            return rows

        except WebDriverException as e:
            logging.error(
                f"WebDriver error on page {page_idx + 1}, attempt {attempt + 1}: {e}"
            )
            if attempt < max_retries - 1:
                smart_delay(2.0, 1.0)  # Wait before retry
                continue
            else:
                logging.error(
                    f"Failed to scrape page {page_idx + 1} after {max_retries} attempts"
                )
                return []
        except Exception as e:
            logging.error(f"Unexpected error on page {page_idx + 1}: {e}")
            return []

    return []


def gather_all_listing_links(
    max_pages: int, headless_listing: bool = False, legacy_headless: bool = False
) -> List[Dict]:
    """Gather all publication links from listing pages."""
    # Listing works more reliably non-headless
    driver = make_driver(headless_listing, legacy_headless)
    try:
        logging.info(f"Starting to gather links from up to {max_pages} pages")
        driver.get(BASE_URL)
        accept_cookies_if_present(driver)
        smart_delay(1.0)

        all_rows: List[Dict] = []
        for i in range(max_pages):
            logging.info(f"[LIST] Processing page {i+1}/{max_pages}")
            rows = scrape_listing_page(driver, i)
            if not rows:
                logging.info(f"[LIST] Empty page at index {i}; stopping early.")
                break
            all_rows.extend(rows)

            # Random delay between pages
            smart_delay(1.5, 0.8)

        # Remove duplicates by link
        uniq = {}
        for r in all_rows:
            uniq[r["link"]] = r

        unique_rows = list(uniq.values())
        logging.info(
            f"Collected {len(unique_rows)} unique links from {len(all_rows)} total entries"
        )
        return unique_rows

    except Exception as e:
        logging.error(f"Error in gather_all_listing_links: {e}")
        return []
    finally:
        try:
            driver.quit()
            logging.debug("Driver closed successfully")
        except Exception as e:
            logging.warning(f"Error closing driver: {e}")


# =========================== DETAIL (Stage 2) ===========================
# author parsing helpers
FIRST_DIGIT = re.compile(r"\d")
NAME_PAIR = re.compile(
    r"[A-Z][A-Za-z'’\-]+,\s*(?:[A-Z](?:\.)?)(?:\s*[A-Z](?:\.)?)*", flags=re.UNICODE
)


def _uniq(seq: List[str]) -> List[str]:
    seen, out = set(), []
    for x in seq:
        x = x.strip()
        if x and x not in seen:
            seen.add(x)
            out.append(x)
    return out


def _get_meta_list(driver: webdriver.Chrome, names_or_props: List[str]) -> List[str]:
    vals = []
    for nm in names_or_props:
        for el in driver.find_elements(
            By.CSS_SELECTOR, f'meta[name="{nm}"], meta[property="{nm}"]'
        ):
            c = (el.get_attribute("content") or "").strip()
            if c:
                vals.append(c)
    return _uniq(vals)


def _extract_authors_jsonld(driver: webdriver.Chrome) -> List[str]:
    import json as _json

    names = []
    for s in driver.find_elements(
        By.CSS_SELECTOR, 'script[type="application/ld+json"]'
    ):
        txt = (s.get_attribute("textContent") or "").strip()
        if not txt:
            continue
        try:
            data = _json.loads(txt)
        except Exception:
            continue
        objs = data if isinstance(data, list) else [data]
        for obj in objs:
            auth = obj.get("author")
            if not auth:
                continue
            if isinstance(auth, list):
                for a in auth:
                    n = a.get("name") if isinstance(a, dict) else str(a)
                    if n:
                        names.append(n)
            elif isinstance(auth, dict):
                n = auth.get("name")
                if n:
                    names.append(n)
            elif isinstance(auth, str):
                names.append(auth)
    return _uniq(names)


def _maybe_expand_authors(driver: webdriver.Chrome):
    try:
        btns = driver.find_elements(
            By.XPATH,
            "//button[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'show') or "
            "contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'more')]",
        )
        for b in btns[:2]:
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", b
                )
                time.sleep(0.15)
                b.click()
                time.sleep(0.25)
            except Exception:
                continue
    except Exception:
        pass


def _authors_from_subtitle_simple(
    driver: webdriver.Chrome, title_text: str
) -> List[str]:
    """
    Use the line containing authors + date:
    remove the title, keep chars until first digit (date starts),
    then extract 'Surname, Initials' pairs.
    """
    try:
        date_el = driver.find_element(By.CSS_SELECTOR, "span.date")
    except NoSuchElementException:
        return []

    # prefer ancestor with class 'subtitle' (portal markup), else parent
    try:
        subtitle = date_el.find_element(
            By.XPATH, "ancestor::*[contains(@class,'subtitle')][1]"
        )
    except Exception:
        try:
            subtitle = date_el.find_element(By.XPATH, "..")
        except Exception:
            subtitle = None

    line = subtitle.text if subtitle else ""
    if title_text and title_text in line:
        line = line.replace(title_text, "")
    line = " ".join(line.split()).strip()

    m = FIRST_DIGIT.search(line)
    pre_date = line[: m.start()].strip(" -—–·•,;|") if m else line
    pre_date = pre_date.replace(" & ", ", ").replace(" and ", ", ")
    pairs = NAME_PAIR.findall(pre_date)
    return _uniq(pairs)


def extract_detail_for_link(
    driver: webdriver.Chrome,
    link: str,
    title_hint: str,
    delay: float,
    fast_mode: bool = False,
) -> Dict:
    """Extract detailed information for a single publication link."""
    try:
        logging.debug(f"Extracting details for: {link}")
        driver.get(link)
        accept_cookies_if_present(driver)
        smart_delay(0.5)

        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "h1"))
            )
        except TimeoutException:
            logging.warning(f"Timeout waiting for page to load: {link}")

        # Title (use detail title if available; else listing hint)
        try:
            title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()
        except NoSuchElementException:
            title = title_hint or ""
            logging.debug(f"Using title hint: {title}")

        # Try to reveal hidden lists
        _maybe_expand_authors(driver)

        # AUTHORS: DOM → subtitle simple → meta → JSON-LD
        authors = []
        for sel in [
            ".relations.persons a[href*='/en/persons/'] span",
            ".relations.persons a[href*='/en/persons/']",
            "section#persons a[href*='/en/persons/'] span",
            "section#persons a[href*='/en/persons/']",
        ]:
            try:
                for el in driver.find_elements(By.CSS_SELECTOR, sel):
                    t = el.text.strip()
                    if t:
                        authors.append(t)
                if authors:
                    break
            except Exception as e:
                logging.debug(f"Error extracting authors with selector '{sel}': {e}")

        if not authors:
            authors = _authors_from_subtitle_simple(driver, title)
        if not authors:
            authors = _get_meta_list(
                driver, ["citation_author", "dc.contributor", "dc.contributor.author"]
            )
        if not authors:
            authors = _extract_authors_jsonld(driver)
        authors = _uniq(authors)

        # PUBLISHED DATE
        published_date = None
        for sel in ["span.date", "time[datetime]", "time"]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                published_date = el.get_attribute("datetime") or el.text.strip()
                if published_date:
                    break
            except NoSuchElementException:
                continue
            except Exception as e:
                logging.debug(f"Error extracting date with selector '{sel}': {e}")

        if not published_date:
            metas = _get_meta_list(
                driver,
                ["citation_publication_date", "dc.date", "article:published_time"],
            )
            if metas:
                published_date = metas[0]

        # ABSTRACT
        abstract_txt = None
        for sel in [
            "section#abstract .textblock",
            "section.abstract .textblock",
            "div.abstract .textblock",
            "div#abstract",
            "section#abstract",
            "div.textblock",
        ]:
            try:
                el = driver.find_element(By.CSS_SELECTOR, sel)
                txt = el.text.strip()
                if txt and len(txt) > 15:
                    abstract_txt = txt
                    break
            except NoSuchElementException:
                continue
            except Exception as e:
                logging.debug(f"Error extracting abstract with selector '{sel}': {e}")

        if not abstract_txt:
            try:
                hdrs = driver.find_elements(By.CSS_SELECTOR, "h2, h3")
                for h in hdrs:
                    if "abstract" in h.text.strip().lower():
                        nxt = h.find_element(
                            By.XPATH,
                            "./following::*[self::div or self::p or self::section][1]",
                        )
                        txt = nxt.text.strip()
                        if txt:
                            abstract_txt = txt
                            break
            except Exception as e:
                logging.debug(f"Error extracting abstract from headers: {e}")

        smart_delay(delay, delay * 0.3, fast_mode)  # Variable polite delay

        result = {
            "title": title,
            "link": link,
            "authors": authors,
            "published_date": published_date,
            "abstract": abstract_txt or "",
        }

        logging.debug(f"Successfully extracted details for: {title[:50]}...")
        return result

    except Exception as e:
        logging.error(f"Error extracting details for {link}: {e}")
        return {
            "title": title_hint,
            "link": link,
            "authors": [],
            "published_date": None,
            "abstract": "",
        }


# =========================== Workers ===========================
def worker_detail_batch(
    batch: List[Dict],
    headless: bool,
    legacy_headless: bool,
    delay: float,
    fast_mode: bool = False,
) -> List[Dict]:
    """Process a batch of detail pages in a single worker."""
    worker_id = f"worker-{os.getpid()}-{random.randint(1000, 9999)}"
    logging.info(
        f"[{worker_id}] Starting batch processing with {len(batch)} items (fast_mode={fast_mode})"
    )

    driver = None
    out: List[Dict] = []

    try:
        driver = make_driver(
            headless=headless,
            legacy_headless=legacy_headless,
            fast_mode=fast_mode,
            timeout=10 if fast_mode else 15,
        )

        for i, it in enumerate(batch, 1):
            # Check cache first
            cached_result = url_cache.get(it["link"])
            if cached_result:
                out.append(cached_result)
                perf_monitor.record_success()
                logging.debug(
                    f"[{worker_id}] {i}/{len(batch)} ✓ (cached) {cached_result['title'][:60]}..."
                )
                continue

            try:
                rec = extract_detail_for_link(
                    driver, it["link"], it.get("title", ""), delay, fast_mode
                )
                out.append(rec)
                url_cache.set(it["link"], rec)  # Cache successful result
                perf_monitor.record_success()
                logging.info(f"[{worker_id}] {i}/{len(batch)} ✓ {rec['title'][:60]}...")

                # More frequent driver refresh in fast mode, less frequent in normal mode
                refresh_interval = 15 if fast_mode else 25
                if i % refresh_interval == 0:
                    logging.debug(f"[{worker_id}] Refreshing driver after {i} pages")
                    try:
                        driver.quit()
                        driver = make_driver(
                            headless=headless,
                            legacy_headless=legacy_headless,
                            fast_mode=fast_mode,
                            timeout=10 if fast_mode else 15,
                        )
                    except Exception as e:
                        logging.warning(f"[{worker_id}] Error refreshing driver: {e}")

            except WebDriverException as e:
                logging.error(f"[{worker_id}] WebDriver error for {it['link']}: {e}")
                perf_monitor.record_error()
                # Add empty record to maintain data integrity
                empty_rec = {
                    "title": it.get("title", ""),
                    "link": it["link"],
                    "authors": [],
                    "published_date": None,
                    "abstract": "",
                }
                out.append(empty_rec)
                url_cache.set(it["link"], empty_rec)  # Cache failed result too
                continue
            except Exception as e:
                logging.error(f"[{worker_id}] Unexpected error for {it['link']}: {e}")
                perf_monitor.record_error()
                empty_rec = {
                    "title": it.get("title", ""),
                    "link": it["link"],
                    "authors": [],
                    "published_date": None,
                    "abstract": "",
                }
                out.append(empty_rec)
                url_cache.set(it["link"], empty_rec)
                continue

    except Exception as e:
        logging.error(f"[{worker_id}] Fatal error in worker: {e}")
    finally:
        if driver:
            try:
                driver.quit()
                logging.debug(f"[{worker_id}] Driver closed successfully")
            except Exception as e:
                logging.warning(f"[{worker_id}] Error closing driver: {e}")

    logging.info(f"[{worker_id}] Completed batch: {len(out)} results")
    return out


def chunk(items: List[Dict], n: int) -> List[List[Dict]]:
    if n <= 1:
        return [items]
    size = ceil(len(items) / n)
    return [items[i : i + size] for i in range(0, len(items), size)]


# =========================== Orchestrator ===========================
def main():
    ap = argparse.ArgumentParser(
        description="Coventry PurePortal scraper (listing → details: authors + abstract + date)."
    )
    ap.add_argument("--outdir", default="../data", help="Output directory for results")
    ap.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Max listing pages to scan (stops early on empty).",
    )
    ap.add_argument(
        "--workers",
        type=int,
        default=12,  # Increased from 8 to 12
        help="Parallel headless browsers for detail pages.",
    )
    ap.add_argument(
        "--delay",
        type=float,
        default=0.15,
        help="Per-detail polite delay (seconds). Reduced from 0.35 for faster crawling.",
    )
    ap.add_argument(
        "--listing-headless",
        action="store_true",
        help="Run listing headless (not recommended).",
    )
    ap.add_argument(
        "--legacy-headless",
        action="store_true",
        help="Use legacy --headless instead of --headless=new.",
    )
    ap.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level",
    )
    ap.add_argument(
        "--fast-mode",
        action="store_true",
        help="Enable fast mode: disable images, CSS, JS for faster crawling",
    )
    ap.add_argument(
        "--resume",
        action="store_true",
        help="Resume from existing publications_links.json if available",
    )
    ap.add_argument(
        "--progress",
        action="store_true",
        help="Show detailed progress information during crawling",
    )
    args = ap.parse_args()

    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    # Performance optimizations based on mode
    if args.fast_mode:
        logging.info(
            "🚀 FAST MODE ENABLED: Disabling images, CSS, JS for maximum speed"
        )
        args.delay = min(args.delay, 0.1)  # Cap delay at 100ms in fast mode

    # Resume functionality
    links_file = outdir / "publications_links.json"
    listing = []

    if args.resume and links_file.exists():
        logging.info(f"📁 RESUME MODE: Loading existing links from {links_file}")
        try:
            with open(links_file, "r", encoding="utf-8") as f:
                listing = json.load(f)
            logging.info(f"✅ Loaded {len(listing)} existing links")
        except Exception as e:
            logging.error(f"❌ Failed to load existing links: {e}")
            listing = []

    logging.info(
        f"🚀 Starting crawler: {args.workers} workers, max {args.max_pages} pages, {args.delay}s delay"
    )
    logging.info(f"📂 Output directory: {outdir.absolute()}")
    if args.fast_mode:
        logging.info("⚡ Fast mode: Images/CSS/JS disabled")

    # Start performance monitoring
    perf_monitor.start_stage("total_crawl")

    # -------- Stage 1: listing (skip if resuming)
    if not listing:
        perf_monitor.start_stage("listing")
        logging.info(f"[STAGE 1] 🔍 Collecting links (up to {args.max_pages} pages)…")
        listing = gather_all_listing_links(
            args.max_pages,
            headless_listing=args.listing_headless,
            legacy_headless=args.legacy_headless,
        )
        if not listing:
            logging.error("❌ No publications found on listing pages.")
            return

        links_file.write_text(json.dumps(listing, indent=2), encoding="utf-8")
        logging.info(
            f"[STAGE 1] ✅ Collected {len(listing)} unique links → {links_file}"
        )
        perf_monitor.end_stage("listing")
    else:
        logging.info(
            f"[STAGE 1] ⏭️  Skipped (resuming with {len(listing)} existing links)"
        )

    # -------- Stage 2: details (parallel)
    perf_monitor.start_stage("details")
    logging.info(f"[STAGE 2] 🔄 Scraping details with {args.workers} workers…")
    if args.fast_mode:
        logging.info("⚡ Fast mode active: Expect 2-3x faster processing")

    batches = chunk(listing, args.workers)
    results: List[Dict] = []

    start_time = time.time()

    # Progress monitoring thread
    def progress_monitor():
        while True:
            time.sleep(10)  # Update every 10 seconds
            stats = perf_monitor.get_stats()
            if stats["processed"] > 0:
                eta = (
                    ((len(listing) - stats["processed"]) / stats["items_per_second"])
                    if stats["items_per_second"] > 0
                    else 0
                )
                logging.info(
                    f"📊 Progress: {stats['processed']}/{len(listing)} "
                    f"({stats['success_rate']:.1f}% success) "
                    f"@ {stats['items_per_second']:.1f} items/s "
                    f"ETA: {eta/60:.1f}m"
                )

    if args.progress:
        progress_thread = threading.Thread(target=progress_monitor, daemon=True)
        progress_thread.start()

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [
            ex.submit(
                worker_detail_batch,
                batch,
                True,
                args.legacy_headless,
                args.delay,
                args.fast_mode,
            )
            for batch in batches
        ]
        done = 0
        for fut in as_completed(futs):
            try:
                part = fut.result() or []
                results.extend(part)
                done += 1
                elapsed = time.time() - start_time
                stats = perf_monitor.get_stats()
                logging.info(
                    f"[STAGE 2] ✅ Batch {done}/{len(batches)} (+{len(part)} items) "
                    f"- Elapsed: {elapsed:.1f}s @ {stats['items_per_second']:.1f}/s"
                )
            except Exception as e:
                logging.error(f"❌ Worker batch failed: {e}")
                done += 1

    perf_monitor.end_stage("details")

    # -------- Save with enhanced reporting
    logging.info(f"[STAGE 3] 💾 Saving results...")
    # de-dupe by link; prefer detail results
    by_link: Dict[str, Dict] = {}
    for it in listing:
        by_link[it["link"]] = {"title": it["title"], "link": it["link"]}
    for rec in results:
        by_link[rec["link"]] = rec  # overwrite with full detail

    final_rows = list(by_link.values())
    out_path = outdir / "publications.json"
    out_path.write_text(
        json.dumps(final_rows, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Final performance report
    perf_monitor.end_stage("total_crawl")
    total_time = time.time() - start_time
    final_stats = perf_monitor.get_stats()

    logging.info("=" * 60)
    logging.info("🎉 CRAWLING COMPLETED!")
    logging.info(f"📊 Final Results:")
    logging.info(f"   • Total records: {len(final_rows)}")
    logging.info(f"   • Successful extractions: {final_stats['success']}")
    logging.info(f"   • Failed extractions: {final_stats['errors']}")
    logging.info(f"   • Success rate: {final_stats['success_rate']:.1f}%")
    logging.info(
        f"   • Average speed: {final_stats['items_per_second']:.1f} items/second"
    )
    logging.info(f"   • Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")
    logging.info(
        f"   • Time saved vs default: ~{((770 * 0.35 + 300) - total_time)/60:.1f} minutes"
    )
    logging.info(f"📁 Saved to: {out_path}")
    logging.info("=" * 60)

    # Save performance stats
    stats_path = outdir / "performance_stats.json"
    stats_path.write_text(
        json.dumps(
            {
                **final_stats,
                "total_time": total_time,
                "total_records": len(final_rows),
                "fast_mode": args.fast_mode,
                "workers": args.workers,
                "delay": args.delay,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
