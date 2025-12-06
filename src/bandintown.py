# """
# Module bandintown

# """

# import os
# import json
# import time
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# ARTIST_URLS_JSON = os.path.join("outputs", "artist_urls.json")

# def load_artist_urls():
#     """Charge le dictionnaire artist_name -> URL depuis artist_urls.json"""
#     if not os.path.exists(ARTIST_URLS_JSON):
#         return {}
#     with open(ARTIST_URLS_JSON, "r", encoding="utf-8") as f:
#         return json.load(f)

# def save_artist_urls(artist_urls):
#     """Sauvegarde le dictionnaire artist_name -> URL dans artist_urls.json"""
#     os.makedirs(os.path.dirname(ARTIST_URLS_JSON), exist_ok=True)
#     with open(ARTIST_URLS_JSON, "w", encoding="utf-8") as f:
#         json.dump(artist_urls, f, indent=2, ensure_ascii=False)

# def find_artist_link(driver, artist_name, timeout=10):
#     words = artist_name.lower().split()
#     links = WebDriverWait(driver, timeout).until(
#         lambda d: [
#             a for a in d.find_elements(By.XPATH, "//a[contains(@href,'/a/')]")
#             if all(word in a.text.lower() for word in words)
#         ] or False 
#     )
#     return links if links else None

# def find_bandintown_url(artist_name):
#     url_explore = "https://www.bandsintown.com/u/explore"
#     options = Options()
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument("--disable-gpu")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--lang=en-US")
#     options.add_argument("accept-language=en-US")
#     options.add_experimental_option("prefs", {"intl.accept_languages": "en,en_US"})
#     driver = webdriver.Chrome(
#         service=Service(ChromeDriverManager().install()),
#         options=options
#     )
#     try:
#         driver.get(url_explore)
#         input_elem = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
#         input_elem.clear()
#         input_elem.send_keys(artist_name)
#         links = find_artist_link(driver, artist_name, timeout=10)
#         if links:
#             return links[0].get_attribute("href").split("?")[0]
#         else:
#             return None
#     except Exception as e:
#         print(f"[!] Erreur lors de la recherche Bandintown pour {artist_name}: {e}")
#         return None
#     finally:
#         driver.quit()

# def get_bandintown_url(artist_name, artist_urls=None):
#     if artist_urls is None:
#         artist_urls = load_artist_urls()
#     url = artist_urls.get(artist_name)
#     if url is None:
#         print(f"[i] URL inconnue pour {artist_name}, recherche...")
#         url = find_bandintown_url(artist_name)
#         if url:
#             print(f"[✓] URL trouvée : {url}")
#             artist_urls[artist_name] = url
#             save_artist_urls(artist_urls)
#         else:
#             print(f"[!] Impossible de trouver l'URL de {artist_name}")
#     return url

# def find_visible_element_by_text(driver, text):
#     elems = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
#     for e in elems:
#         if e.is_displayed():
#             return e
#     return None

# def get_shows_section_state(driver, timeout=10):
#     wait = WebDriverWait(driver, timeout)
#     wait.until(lambda d: len(d.find_elements(
#         By.XPATH, "//*[contains(text(),'No upcoming shows')]")) > 0)
#     wait.until(lambda d: len(d.find_elements(
#         By.XPATH, "//*[contains(text(),'all concerts')]")) > 0)
#     for _ in range(timeout * 10):
#         no_shows = find_visible_element_by_text(driver, "No upcoming shows")
#         all_shows = find_visible_element_by_text(driver, "all concerts")
#         if no_shows:
#             return "no_shows", no_shows
#         if all_shows:
#             return "shows", all_shows
#         time.sleep(0.1)
#     raise TimeoutError("Impossible de détecter la section visible.")

# def safe_click(driver, element):
#     driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
#     driver.execute_script("arguments[0].click();", element)

# def parse_concerts(driver, event_links):
#     events_data = []
#     for link in event_links:
#         try:
#             event_block = link.find_element(By.XPATH, "./ancestor::div[3]")
#             month = event_block.find_element(By.XPATH, ".//div[.='JAN' or .='FEB' or .='MAR' or .='APR' or .='MAY' or .='JUN' or .='JUL' or .='AUG' or .='SEP' or .='OCT' or .='NOV' or .='DEC']").text.strip()
#             day = month_elem = event_block.find_element(By.XPATH, f".//div[.='{month}']/following-sibling::div[1]").text.strip()
#             venue = link.find_element(By.XPATH, "./div[1]").text.strip()
#             city = link.find_element(By.XPATH, "./div[2]").text.strip()
#             url = link.get_attribute("href")
#             events_data.append({
#                 "date": f"{day} {month}",
#                 "venue": venue,
#                 "city": city,
#                 "url": url
#             })
#         except Exception as e:
#             print("[!] Impossible de parser un événement :", e)
#             continue
#     return events_data

# def get_bandintown_concerts(driver, artist_url, timeout=15):
#     driver.get(artist_url)
#     wait = WebDriverWait(driver, timeout)
#     state, header = get_shows_section_state(driver)
#     if state == "no_shows":
#         return []
#     container = header.find_element(By.XPATH, "./ancestor::div[1]")
#     try:
#         wait.until(
#             lambda d: container.find_elements(By.XPATH, ".//a[contains(@href,'/e/')]")
#         )
#     except:
#         return []
#     try:
#         show_more = container.find_element(By.XPATH, ".//*[contains(text(), 'Show More')]")
#         safe_click(driver, show_more)
#         time.sleep(1)
#     except:
#         pass
#     event_links = container.find_elements(By.XPATH, ".//a[contains(@href,'/e/')]")
#     results = parse_concerts(driver, event_links)
#     return results

# def get_bandintown_events(artist_name, artist_urls=None):
#     try:
#         artist_url = get_bandintown_url(artist_name, artist_urls=artist_urls)
#         options = Options()
#         options.add_argument("--disable-blink-features=AutomationControlled")
#         options.add_argument("--disable-gpu")
#         options.add_argument("--no-sandbox")
#         options.add_argument("--lang=en-US")
#         options.add_argument("accept-language=en-US")
#         options.add_experimental_option("prefs", {"intl.accept_languages": "en,en_US"})
#         driver = webdriver.Chrome(
#             service=Service(ChromeDriverManager().install()),
#             options=options
#         )
#         return get_bandintown_concerts(driver, artist_url)
#     finally:
#         driver.quit()

"""
Module bandsintown – version refactorisée avec une classe et un driver unique.
"""

import os
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


ARTIST_URLS_JSON = os.path.join("outputs", "artist_urls.json")
MONTHS = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]

class BandsintownClient:
    """
    Client Bandsintown réutilisant une seule instance Selenium.
    Permet :
    - d'obtenir l'URL d'un artiste
    - de récupérer la liste des concerts
    - de maintenir un cache JSON artist_name -> URL
    """

    def __init__(self):
        self.artist_urls = self._load_artist_urls()
        self.driver = self._create_driver()

    def _create_driver(self):
        """Crée un driver Selenium partagé pour toute la durée de vie du client."""
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--lang=en-US")
        options.add_argument("accept-language=en-US")
        options.add_experimental_option("prefs", {"intl.accept_languages": "en,en_US"})
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
        return driver

    def quit(self):
        """Ferme proprement le driver Selenium."""
        if self.driver:
            self.driver.quit()

    def _load_artist_urls(self):
        """Charge le fichier JSON de cache."""
        if not os.path.exists(ARTIST_URLS_JSON):
            return {}
        with open(ARTIST_URLS_JSON, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_artist_urls(self):
        """Sauvegarde le cache JSON."""
        os.makedirs(os.path.dirname(ARTIST_URLS_JSON), exist_ok=True)
        with open(ARTIST_URLS_JSON, "w", encoding="utf-8") as f:
            json.dump(self.artist_urls, f, indent=2, ensure_ascii=False)


    def _wait_artist_link(self, artist_name, timeout=10):
        """Attente d’un lien d’artiste correspondant aux mots du nom."""
        words = artist_name.lower().split()
        return WebDriverWait(self.driver, timeout).until(
            lambda d: [
                a for a in d.find_elements(By.XPATH, "//a[contains(@href,'/a/')]")
                if all(w in a.text.lower() for w in words)
            ] or False
        )

    def _find_bandintown_url(self, artist_name):
        """Recherche l'URL Bandsintown depuis la page Explore."""
        self.driver.get("https://www.bandsintown.com/u/explore")
        try:
            input_elem = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
            input_elem.clear()
            input_elem.send_keys(artist_name)
            links = self._wait_artist_link(artist_name)
            if not links:
                return None
            return links[0].get_attribute("href").split("?")[0]
        except Exception as e:
            print(f"[!] Erreur recherche artiste {artist_name}: {e}")
            return None

    def get_artist_url(self, artist_name):
        """Retourne l’URL Bandsintown d’un artiste, en l’ajoutant au cache si besoin."""
        if artist_name in self.artist_urls:
            return self.artist_urls[artist_name]

        print(f"[i] Recherche de l'URL Bandsintown pour {artist_name}...")
        url = self._find_bandintown_url(artist_name)
        if url:
            print(f"[✓] Trouvé : {url}")
            self.artist_urls[artist_name] = url
            self._save_artist_urls()
        else:
            print(f"[!] URL introuvable pour {artist_name}")
        return url

    def _find_visible_element_by_text(self, text):
        elems = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
        return next((e for e in elems if e.is_displayed()), None)

    def _detect_shows_section(self, timeout=10):
        """Détecte si l'artiste a des concerts ou non."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(By.XPATH, "//*[contains(text(),'No upcoming shows')]")
        )
        WebDriverWait(self.driver, timeout).until(
            lambda d: d.find_elements(By.XPATH, "//*[contains(text(),'all concerts')]")
        )
        for _ in range(timeout * 10):
            no_shows = self._find_visible_element_by_text("No upcoming shows")
            all_shows = self._find_visible_element_by_text("all concerts")
            if no_shows:
                return "no_shows", no_shows
            if all_shows:
                return "shows", all_shows
            time.sleep(0.1)

        raise TimeoutError("Impossible de détecter la section concerts.")

    def _safe_click(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        self.driver.execute_script("arguments[0].click();", element)

    def _parse_event_blocks(self, links):
        """Extrait date, salle, ville pour chaque évènement."""
        events = []
        for link in links:
            try:
                block = link.find_element(By.XPATH, "./ancestor::div[3]")
                month = block.find_element(
                    By.XPATH,
                    ".//div[" + " or ".join(f"text()='{m}'" for m in MONTHS) + "]"
                ).text
                day = block.find_element(
                    By.XPATH, f".//div[text()='{month}']/following-sibling::div[1]"
                ).text
                venue = link.find_element(By.XPATH, "./div[1]").text
                city = link.find_element(By.XPATH, "./div[2]").text
                url = link.get_attribute("href")
                events.append({
                    "date": f"{day} {month}",
                    "venue": venue,
                    "city": city,
                    "url": url,
                })
            except Exception as e:
                print("[!] Erreur parsing évènement :", e)
        return events

    # ---------------------------------------
    # Fonction principale : obtenir les concerts
    # ---------------------------------------
    def get_concerts(self, artist_name):
        """Renvoie la liste des concerts d'un artiste."""
        url = self.get_artist_url(artist_name)
        if not url:
            return []
        self.driver.get(url)
        state, header = self._detect_shows_section()
        if state == "no_shows":
            return []
        container = header.find_element(By.XPATH, "./ancestor::div[1]")
        WebDriverWait(self.driver, 10).until(
            lambda d: container.find_elements(By.XPATH, ".//a[contains(@href,'/e/')]")
        )
        # bouton "Show More"
        try:
            show_more = container.find_element(By.XPATH, ".//*[contains(text(), 'Show More')]")
            self._safe_click(show_more)
            time.sleep(1)
        except:
            pass
        links = container.find_elements(By.XPATH, ".//a[contains(@href,'/e/')]")
        return self._parse_event_blocks(links)
