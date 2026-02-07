import requests
from bs4 import BeautifulSoup
import json
import time

# --- CONFIG ---
# Make sure these URLs are the EXACT pages where the full tables live
SCHEDULE_URLS = [
    "https://nbsleague.wordpress.com/2026-regular-season-schedule/",
    "https://nbsleague.wordpress.com/2026-preseason-schedule/",
    "https://nbsleague.wordpress.com/2025-playoff-schedule/",
    "https://nbsleague.wordpress.com/2025-regular-season-schedule/"
]

STANDINGS_URLS = [
    "https://nbsleague.wordpress.com/2026-standings/",
    "https://nbsleague.wordpress.com/2025-standings/"
]

def scrape_all():
    all_data = {}
    
    # 1. SCRAPE SCHEDULES
    for url in SCHEDULE_URLS:
        season_name = url.split('/')[-2].replace('-', '_')
        print(f"Scraping Schedule: {season_name}...")
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Look for ALL tables on the page, just in case they are split
        tables = soup.find_all('table')
        season_games = []
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) < 4: continue
                
                # Using separator=" " captures text inside <br> tags properly
                game = {
                    "date": cols[0].get_text(separator=" ").strip(),
                    "time": cols[1].get_text(separator=" ").strip(),
                    "away_team": cols[2].get_text(separator=" ").split()[0] if cols[2].text else "???",
                    "home_team": cols[2].get_text(separator=" ").split()[-1] if cols[2].text else "???",
                    "away_score": cols[3].get_text(separator=" ").split()[0] if cols[3].text else "0",
                    "home_score": cols[3].get_text(separator=" ").split()[-1] if cols[3].text else "0",
                    "status": cols[4].text.strip() if len(cols) > 4 else "Final"
                }
                season_games.append(game)
        
        all_data[season_name] = season_games
        time.sleep(1) # Be nice to the server

    # Save Schedule
    with open('nbs_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)

    # 2. SCRAPE STANDINGS
    standings_data = {}
    for url in STANDINGS_URLS:
        season_name = url.split('/')[-2].replace('-', '_')
        print(f"Scraping Standings: {season_name}...")
        
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        
        rows = table.find_all('tr')[1:] if table else [] # Skip header
        season_standings = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 5: continue
            season_standings.append({
                "rank": cols[0].text.strip(),
                "team": cols[1].text.strip(),
                "record": cols[3].text.strip(),
                "pct": cols[4].text.strip()
            })
        standings_data[season_name] = season_standings

    # Save Standings to its OWN file
    with open('nbs_standings.json', 'w') as f:
        json.dump(standings_data, f, indent=2)

if __name__ == "__main__":
    scrape_all()
