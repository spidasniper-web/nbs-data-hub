import requests
from bs4 import BeautifulSoup
import json
import re

# --- CONFIGURATION ---
SCHEDULE_PAGES = {
    "2026_Regular_Season": "https://nbsleague.wordpress.com/2026-regular-season-schedule/",
    "2026_Preseason": "https://nbsleague.wordpress.com/2026-preseason-schedule/",
    "2025_Playoffs": "https://nbsleague.wordpress.com/2025-playoff-schedule/",
    "2024_25_Regular_Season": "https://nbsleague.wordpress.com/2025-regular-season-schedule/"
}

STANDINGS_PAGES = {
    "2026_Regular_Season": "https://nbsleague.wordpress.com/2026-standings/",
    "2024_25_Regular_Season": "https://nbsleague.wordpress.com/2025-standings/"
}

def clean_text(text):
    return " ".join(text.split()).strip()

def scrape_data():
    # --- SCRAPE SCHEDULE ---
    all_games = {}
    for season, url in SCHEDULE_PAGES.items():
        print(f"Scraping Schedule: {season}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table: continue

        games_list = []
        for row in table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) < 4: continue

            # 1. Date & Time (replacing <br> with space)
            date = cols[0].get_text(separator=" ").strip()
            time = cols[1].get_text(separator=" ").strip()

            # 2. Teams & Logos
            team_cell = cols[2]
            logos = [img['src'] for img in team_cell.find_all('img')]
            # Splitting text like "BOS TOR" into ["BOS", "TOR"]
            team_names = team_cell.get_text(separator=" ").split()
            
            # 3. Scores & Link
            score_cell = cols[3]
            score_link = score_cell.find('a')['href'] if score_cell.find('a') else ""
            scores = score_cell.get_text(separator=" ").split()

            games_list.append({
                "date": date,
                "time": time,
                "away_team": team_names[0] if len(team_names) > 0 else "???",
                "home_team": team_names[1] if len(team_names) > 1 else "???",
                "away_logo": logos[0] if len(logos) > 0 else "",
                "home_logo": logos[1] if len(logos) > 1 else "",
                "away_score": scores[0] if len(scores) > 0 else "0",
                "home_score": scores[1] if len(scores) > 1 else "0",
                "post_url": score_link,
                "status": cols[4].text.strip() if len(cols) > 4 else "Final"
            })
        all_games[season] = games_list

    with open('nbs_data.json', 'w') as f:
        json.dump(all_games, f, indent=2)

    # --- SCRAPE STANDINGS ---
    all_standings = {}
    for season, url in STANDINGS_PAGES.items():
        print(f"Scraping Standings: {season}")
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        table = soup.find('table')
        if not table: continue

        standings_list = []
        rows = table.find_all('tr')
        # Map headers manually since the HTML uses specific icons/abbr
        for row in rows[1:]:
            cols = row.find_all('td')
            if len(cols) < 4: continue
            
            # Extract logo and team name
            team_td = cols[1]
            logo = team_td.find('img')['src'] if team_td.find('img') else ""
            team_name = team_td.text.strip()

            standings_list.append({
                "rank": cols[0].text.strip(),
                "team": team_name,
                "logo": logo,
                "games": cols[2].text.strip(),
                "record": cols[3].text.strip(),
                "pct": cols[4].text.strip(),
                "gb": cols[5].text.strip(),
                "mov": cols[8].text.strip() if len(cols) > 8 else "0"
            })
        all_standings[season] = standings_list

    with open('nbs_standings.json', 'w') as f:
        json.dump(all_standings, f, indent=2)

if __name__ == "__main__":
    scrape_data()
