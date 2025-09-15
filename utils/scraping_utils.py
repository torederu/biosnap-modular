import time
import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import requests
import html
from bs4 import BeautifulSoup
import re
import threading
from datetime import datetime
from zoneinfo import ZoneInfo

# Default timezone for date formatting (matches common UI expectations)
LOCAL_TZ = "US/Eastern"

def local_label(ts_utc_str, tz=LOCAL_TZ):
    """Convert UTC timestamp to local date in mm/dd/yyyy format."""
    dt = datetime.fromisoformat(ts_utc_str.replace("Z", "+00:00")).astimezone(ZoneInfo(tz))
    # Match the UI dropdown format (mm/dd/yyyy)
    return dt.strftime("%m/%d/%Y")

def build_date_index(reports):
    """Map local date -> list of reports with that date."""
    idx = {}
    for r in reports:
        if "createdTimestamp" not in r:
            continue
        lbl = local_label(r["createdTimestamp"])
        idx.setdefault(lbl, []).append(r)
    # Sort each bucket by exact UTC createdTimestamp newest→oldest just in case
    for k in idx:
        idx[k].sort(key=lambda rr: rr["createdTimestamp"], reverse=True)
    return idx

def choose_report_by_created_date(reports, target_local_date):
    """Select a specific report by its local creation date."""
    idx = build_date_index(reports)
    if target_local_date is None:
        # pick most recent by default
        target_local_date = sorted(idx.keys(), reverse=True)[0]
    if target_local_date not in idx:
        raise ValueError(f"No report for local date {target_local_date}. Available: {sorted(idx.keys())}")
    # If more than one report shares the same local date, take the newest createdTimestamp
    return idx[target_local_date][0], target_local_date

def fetch_all_thorne_reports(cookies):
    """Fetch all Gut Health reports from the Thorne API."""
    url = "https://www.thorne.com/account/data/tests/reports/GUTHEALTH/details"
    r = requests.get(url, cookies=cookies, headers={"Accept": "application/json"})
    r.raise_for_status()
    data = r.json() or []
    # Some responses come as dict-with-list; normalize to list of reports
    if isinstance(data, dict) and "reports" in data:
        data = data["reports"]
    return data

def update_progress(status, bar, message, percent):
    if status:
        status.write(message)
    if bar:
        bar.progress(percent)

def scrape_function_health(user_email, user_pass, status=None):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    try:
        service = Service(ChromeDriverManager().install())
    except Exception:
        service = Service("/usr/bin/chromedriver")
        options.add_argument("--binary=/usr/bin/chromium")
    driver = None
    data = []
    def update_status(message):
        status.markdown(
            f'<div style="margin-left:2.0em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ {message}</div>',
            unsafe_allow_html=True
        )
    try:
        update_status("Launching remote browser")
        driver = webdriver.Chrome(service=service, options=options)
        time.sleep(1)
        update_status("Accessing Function Health")
        driver.get("https://my.functionhealth.com/")
        driver.maximize_window()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        ).send_keys(user_email)
        update_status("Logging into Function Health")
        driver.find_element(By.ID, "password").send_keys(user_pass + Keys.RETURN)
        time.sleep(5)
        if "login" in driver.current_url.lower():
            raise ValueError("Login failed — please check your Function Health credentials.")
        update_status("Importing biomarkers")
        driver.get("https://my.functionhealth.com/biomarkers")
        WebDriverWait(driver, 12).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[class^='biomarkerResultRow-styled__BiomarkerName']"))
        )
        everything = driver.find_elements(By.XPATH, "//h4 | //div[contains(@class, 'biomarkerResult-styled__ResultContainer')]")
        current_category = None
        total = len(everything)
        for i, el in enumerate(everything):
            tag = el.tag_name
            if tag == "h4":
                current_category = el.text.strip()
            elif tag == "div":
                try:
                    name = el.find_element(By.CSS_SELECTOR, "[class^='biomarkerResultRow-styled__BiomarkerName']").text.strip()
                    status_text = value = units = ""
                    values = el.find_elements(By.CSS_SELECTOR, "[class*='biomarkerChart-styled__ResultValue']")
                    texts = [v.text.strip() for v in values]
                    if len(texts) == 3:
                        status_text, value, units = texts
                    elif len(texts) == 2:
                        status_text, value = texts
                    elif len(texts) == 1:
                        value = texts[0]
                    try:
                        unit_el = el.find_element(By.CSS_SELECTOR, "[class^='biomarkerChart-styled__UnitValue']")
                        units = unit_el.text.strip()
                    except:
                        pass
                    data.append({
                        "category": current_category,
                        "name": name,
                        "status": status_text,
                        "value": value,
                        "units": units
                    })
                except Exception:
                    continue
        update_status("Closing remote browser")
        driver.quit()
        time.sleep(1)
        update_status("Cleaning data")
        time.sleep(1)
    except Exception as e:
        if driver:
            driver.quit()
        raise e
    return pd.DataFrame(data)

def scrape_thorne_gut_report(user_email, user_pass, status=None):
    import streamlit as st
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")
    try:
        service = Service(ChromeDriverManager().install())
    except Exception:
        service = Service("/usr/bin/chromedriver")
        options.add_argument("--binary=/usr/bin/chromium")
    driver = None
    def update_status(message):
        status.markdown(
            f'<div style="margin-left:2.0em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ {message}</div>',
            unsafe_allow_html=True
        )
    try:
        update_status("Launching remote browser")
        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://www.thorne.com/login")
        wait = WebDriverWait(driver, 15)
        update_status("Logging into Thorne")
        wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(user_email)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(user_pass + Keys.RETURN)
        try:
            wait.until(lambda d: "/login" not in d.current_url)
        except Exception:
            raise ValueError("Login failed — please check your Thorne credentials.")
        time.sleep(0.5)
        update_status("Navigating to Gut Health test")
        driver.get("https://www.thorne.com/account/tests")
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "View Results"))).click()
        wait.until(EC.url_contains("/account/tests/GUTHEALTH/"))
        update_status("Extracting session data")
        for popup_text in ["×", "Got it"]:
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, f"//button[contains(., '{popup_text}')]"))).click()
            except:
                pass
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        update_status("Closing remote browser")
        driver.quit()
        
        # Fetch the most recent report
        update_status("Fetching report data")
        all_reports = fetch_all_thorne_reports(cookies)
        report, _ = choose_report_by_created_date(all_reports, None)  # None gets most recent
        
        update_status("Processing report data")
    except Exception as e:
        if driver:
            driver.quit()
        raise e
    rows = []
    for sec in report.get("bodySections", []):
        results = sec.get("results") or []
        if not results:
            continue
        
        # Find insights section
        insp = next(
            (s for s in report["bodySections"]
             if s.get("anchorId") == sec.get("anchorId", "").replace("_markers", "_insights")),
            {}
        )
        insights_html = insp.get("content", "").strip()
        
        # Find section summary/range text
        summary_html = pick_section_summary(results)
        
        # Look for composite-like item
        sec_title_norm = (sec.get("title") or "").strip().lower()
        comp = next((r for r in results if is_composite_like(r, sec_title_norm)), None)
        
        # Section header row
        if comp:
            rows.append({
                "section":       sec.get("title", ""),
                "item":          "Composite",
                "score":         comp.get("valueNumeric", comp.get("value")),
                "risk":          comp.get("riskClassification", ""),
                "optimal_range": summary_html,
                "insights":      insights_html
            })
        else:
            rows.append({
                "section":       sec.get("title", ""),
                "item":          "",      
                "score":         "",    
                "risk":          "",      
                "optimal_range": summary_html,
                "insights":      insights_html
            })
        
        # Child microbes
        for it in results:
            if comp is not None and it is comp:
                continue
            name = (it.get("title") or it.get("name") or "").strip()
            if not name:
                continue
            rows.append({
                "section":       sec.get("title", ""),
                "item":          name,
                "score":         it.get("valueNumeric", it.get("value")),
                "risk":          it.get("riskClassification", ""),
                "optimal_range": None,
                "insights":      ""
            })
    df = pd.DataFrame(rows)
    
    # Post-processing and cleanup
    df = (
        df.rename(columns={
            'section': 'Category',
            'item': 'Microbe',
            'optimal_range': 'Summary',
            'insights': 'Insights',
            'score': 'Score',
            'risk': 'Risk'
        })
        .assign(
            Risk=lambda x: x['Risk'].str.title() if x['Risk'].dtype == 'object' else x['Risk']
        )
    )
    # Deduplicate Insights: only keep the first non-empty per Category
    df['Insights'] = df.groupby('Category')['Insights'] \
                       .transform(lambda grp: grp.where(grp.ne('').cumsum() <= 1, ''))
    # Cleaning function: un-escape entities, strip citations, remove HTML tags
    def clean_text(text):
        if not text:
            return ''
        text = html.unescape(text)
        text = re.sub(r'<div class="references".*$', '', text, flags=re.DOTALL)
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        return re.sub(r'\s+', ' ', text).strip()
    for col in ['Insights', 'Summary']:
        df[col] = df[col].apply(clean_text)
    # Clear Summary for non-summary categories
    valid_categories = [
        'Digestion', 'Inflammation', 'Gut Dysbiosis',
        'Intestinal Permeability', 'Nervous System',
        'Diversity Score', 'Immune Readiness Score',
        'Pathogens'
    ]
    df.loc[~df['Category'].isin(valid_categories), 'Summary'] = ''
    return df


def get_thorne_available_tests(user_email, user_pass, status=None):
    """Get available Thorne Gut Health test dates for selection using API."""
    from datetime import datetime
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")

    try:
        service = Service(ChromeDriverManager().install())
    except Exception:
        service = Service("/usr/bin/chromedriver")
        options.add_argument("--binary=/usr/bin/chromium")

    driver = None

    def update_status(message):
        if status:
            status.markdown(
                f'<div style="margin-left:2.0em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ {message}</div>',
                unsafe_allow_html=True
            )

    try:
        update_status("Launching remote browser")
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 15)

        # Log in
        update_status("Logging into Thorne")
        driver.get("https://www.thorne.com/login")
        wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(user_email)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(user_pass + Keys.RETURN)
        
        try:
            wait.until(lambda d: "/login" not in d.current_url)
        except Exception:
            raise ValueError("Login failed — please check your Thorne credentials.")

        # Get session cookies for API calls
        update_status("Fetching available Gut Health tests")
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
        
        update_status("Closing remote browser")
        driver.quit()
        
        # Use API to get test data
        resp = requests.get(
            "https://www.thorne.com/account/data/tests",
            cookies=cookies,
            headers={"Accept": "application/json"}
        )
        resp.raise_for_status()
        all_tests = resp.json()
        
        # Filter for completed Gut Health tests only
        gut_health_tests = []
        for test in all_tests:
            if (test.get("packageIdentifier") == "GUTHEALTH" and 
                test.get("completed") == True and 
                test.get("completedTimestamp")):
                
                # Format the completion date
                try:
                    formatted_date = local_label(test["completedTimestamp"])
                    label = f"Gut Health Test - Completed on {formatted_date}"
                except Exception:
                    label = f"Gut Health Test - Completed on {test.get('completedTimestamp', 'Unknown date')}"
                
                gut_health_tests.append({
                    "id": test["id"],
                    "label": label, 
                    "date": test["completedTimestamp"],
                    "local_date": formatted_date,
                    "packageName": test.get("packageName", "Gut Health Test")
                })
        
        # Sort by completion date (newest first)
        gut_health_tests.sort(key=lambda x: x["date"], reverse=True)
        
        return gut_health_tests

    except Exception as e:
        if driver:
            driver.quit()
        raise e


def is_number(val):
    """Check if a value is numeric."""
    if val is None:
        return False
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False

def is_composite_like(item, sec_title_norm):
    """Check if an item represents a composite/section score."""
    title = (item.get("title") or item.get("name") or "").strip()
    content = (item.get("content") or "")
    val = item.get("valueNumeric", item.get("value"))

    has_value = (val is not None) and (str(val).strip() != "")
    is_num = False
    try:
        float(val)
        is_num = True
    except Exception:
        pass

    looks_summary = bool(re.search(r"(optimal range|reference range|your .* score)", content, re.I))
    title_is_score = bool(re.search(r"\bscore\b", title, re.I))

    # NEW: title matches section title and has any value (numeric or text)
    title_matches_section = title.strip().lower() == sec_title_norm

    return (
        (title == "" and (is_num or looks_summary)) or
        (title_is_score and is_num) or
        (title_matches_section and has_value)
    )

def pick_section_summary(results):
    """Find the first content snippet that contains a range."""
    for it in results:
        c = it.get("content") or ""
        if re.search(r"(optimal range|reference range)", c, re.I):
            return c
        if re.search(r"[≤≥<>]?\s*\d+(?:\.\d+)?\s*(–|-|to)\s*[≤≥<>]?\s*\d+(?:\.\d+)?", c):
            return c
    # fallback: any "*Score" item's content
    for it in results:
        t = it.get("title") or it.get("name") or ""
        if "score" in t.lower() and it.get("content"):
            return it["content"]
    return ""

def scrape_thorne_gut_report_by_date(user_email, user_pass, target_local_date, status=None):
    """Scrape Thorne Gut Health report data for a specific date."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920x1080")

    try:
        service = Service(ChromeDriverManager().install())
    except Exception:
        service = Service("/usr/bin/chromedriver")
        options.add_argument("--binary=/usr/bin/chromium")

    driver = None

    def update_status(message):
        if status:
            status.markdown(
                f'<div style="margin-left:2.0em; font-size:1rem; font-weight:400; line-height:1.2; margin-top:-0.6em; margin-bottom:0.1em;">⤷ {message}</div>',
                unsafe_allow_html=True
            )

    try:
        update_status("Launching remote browser")
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 15)

        # Log in
        update_status("Logging into Thorne")
        driver.get("https://www.thorne.com/login")
        wait.until(EC.element_to_be_clickable((By.NAME, "email"))).send_keys(user_email)
        wait.until(EC.element_to_be_clickable((By.NAME, "password"))).send_keys(user_pass + Keys.RETURN)

        try:
            wait.until(lambda d: "/login" not in d.current_url)
        except Exception:
            raise ValueError("Login failed — please check your Thorne credentials.")

        # Navigate to tests page to establish session
        update_status("Opening Gut Health tests")
        driver.get("https://www.thorne.com/account/tests")

        # Get session cookies for API call
        update_status("Extracting session data")
        cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

        update_status("Closing remote browser")
        driver.quit()

        # Fetch all reports and select the specific one by date
        update_status("Fetching all report data")
        all_reports = fetch_all_thorne_reports(cookies)
        
        update_status("Selecting report by date")
        report, selected_date = choose_report_by_created_date(all_reports, target_local_date)
        
        update_status(f"Processing report from {selected_date}")

    except Exception as e:
        if driver:
            driver.quit()
        raise e

    # Process the report data
    rows = []
    for sec in report.get("bodySections", []):
        results = sec.get("results") or []
        if not results:
            continue
        
        # Find insights section
        insp = next(
            (s for s in report["bodySections"]
             if s.get("anchorId") == sec.get("anchorId", "").replace("_markers", "_insights")),
            {}
        )
        insights_html = insp.get("content", "").strip()
        
        # Find section summary/range text
        summary_html = pick_section_summary(results)
        
        # Look for composite-like item
        sec_title_norm = (sec.get("title") or "").strip().lower()
        comp = next((r for r in results if is_composite_like(r, sec_title_norm)), None)
        
        # Add section header row
        if comp:
            rows.append({
                "section":       sec.get("title", ""),
                "item":          "Composite",
                "score":         comp.get("valueNumeric", comp.get("value")),
                "risk":          comp.get("riskClassification", ""),
                "optimal_range": summary_html,
                "insights":      insights_html
            })
        else:
            rows.append({
                "section":       sec.get("title", ""),
                "item":          "",      
                "score":         "",    
                "risk":          "",      
                "optimal_range": summary_html,
                "insights":      insights_html
            })
        
        # Child microbes
        for it in results:
            if comp is not None and it is comp:
                continue
            name = (it.get("title") or it.get("name") or "").strip()
            if not name:
                continue
            rows.append({
                "section":       sec.get("title", ""),
                "item":          name,
                "score":         it.get("valueNumeric", it.get("value")),
                "risk":          it.get("riskClassification", ""),
                "optimal_range": None,
                "insights":      ""
            })

    df = pd.DataFrame(rows)

    # Cleaning/post-processing logic
    df = (
        df.rename(columns={
            'section': 'Category',
            'item': 'Microbe',
            'optimal_range': 'Summary',
            'insights': 'Insights',
            'score': 'Score',
            'risk': 'Risk'
        })
        .assign(
            Risk=lambda x: x['Risk'].str.title() if x['Risk'].dtype == 'object' else x['Risk']
        )
    )

    # Deduplicate Insights: only keep the first non-empty per Category
    df['Insights'] = df.groupby('Category')['Insights']                        .transform(lambda grp: grp.where(grp.ne('').cumsum() <= 1, ''))

    # Cleaning function: un-escape entities, strip citations, remove HTML tags
    def clean_text(text):
        if not text:
            return ''
        text = html.unescape(text)
        text = re.sub(r'<div class="references".*$', '', text, flags=re.DOTALL)
        text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
        return re.sub(r'\s+', ' ', text).strip()

    for col in ['Insights', 'Summary']:
        df[col] = df[col].apply(clean_text)

    # Clear Summary for non-summary categories
    valid_categories = [
        'Digestion', 'Inflammation', 'Gut Dysbiosis',
        'Intestinal Permeability', 'Nervous System',
        'Diversity Score', 'Immune Readiness Score',
        'Pathogens'
    ]
    df.loc[~df['Category'].isin(valid_categories), 'Summary'] = ''
    return df
