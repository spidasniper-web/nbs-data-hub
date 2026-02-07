import requests
from bs4 import BeautifulSoup
import json
import time

# --- CONFIG ---
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
        # Create a clean season name from the URL
        season_name = url.split('/')[-2].replace('-', '_')
        print(f"Scraping Schedule: {season_name}...")
        
        try:
            res = requests.get(url, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            tables = soup.find_all('table')
            season_games = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 4: continue
                    
                    # --- LOGO EXTRACTION ---
                    # Look for all images in the team name cell (cols[2])
                    imgs = cols[2].find_all('img')
                    away_logo = imgs[0]['src'] if len(imgs) > 0 else ""
                    home_logo = imgs[1]['src'] if len(imgs) > 1 else ""

                    # --- POST URL EXTRACTION ---
                    # The link to the gameday post is usually in the score cell (cols[3])
                    link_tag = cols[3].find('a', href=True)
                    post_url = link_tag['href'] if link_tag else ""

                    # --- TEAM & SCORE CLEANING ---
                    # Using separator=" " ensures "BOS<br>TOR" becomes "BOS TOR"
                    teams = cols[2].get_text(separator=" ").split()
                    scores = cols[3].get_text(separator=" ").split()

                    game = {
                        "date": cols[0].get_text(separator=" ").strip(),
                        "time": cols[1].get_text(separator=" ").strip(),
                        "away_team": teams[0] if len(teams) > 0 else "???",
                        "home_team": teams[1] if len(teams) > 1 else "???",
                        "away_logo": away_logo,
                        "home_logo": home_logo,
                        "away_score": scores[0] if len(scores) > 0 else "0",
                        "home_score": scores[1] if len(scores) > 1 else "0",
                        "post_url": post_url,
                        "status": cols[4].get_text().strip() if len(cols) > 4 else "Final"
                    }
                    season_games.append(game)
            
            all_data[season_name] = season_games
            time.sleep(1) 
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    # Save Schedule
    with open('nbs_data.json', 'w') as f:
        json.dump(all_data, f, indent=2)
    print("Schedule saved to nbs_data.json")

    # 2. SCRAPE STANDINGS
    standings_data = {}
    for url in STANDINGS_URLS:
        season_name = url.split('/')[-2].replace('-', '_')
        print(f"Scraping Standings: {season_name}...")
        
        try:
            res = requests.get(url, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Find ALL tables on the page (East, West, or Classic, Legacy)
            tables = soup.find_all('table')
            all_conferences = []
            
            for table in tables:
                rows = table.find_all('tr')[1:] # Skip header
                conference_teams = []
                
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) < 4: continue
                    
                    team_logo = cols[1].find('img')['src'] if cols[1].find('img') else ""
                    
                    conference_teams.append({
                        "rank": cols[0].get_text().strip(),
                        "team": cols[1].get_text().strip(),
                        "logo": team_logo,
                        "record": cols[3].get_text().strip(),
                        "pct": cols[4].get_text().strip(),
                        "gb": cols[5].get_text().strip() if len(cols) > 5 else "0"
                    })
                
                if conference_teams:
                    all_conferences.append(conference_teams)
            
            standings_data[season_name] = all_conferences
            
        except Exception as e:
            print(f"Error scraping standings {url}: {e}")

    with open('nbs_standings.json', 'w') as f:
        json.dump(standings_data, f, indent=2)
    print("Standings saved to nbs_standings.json")

if __name__ == "__main__":
    scrape_all()
