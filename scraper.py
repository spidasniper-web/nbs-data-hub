import requests
from bs4 import BeautifulSoup
import json

# --- CONFIGURATION ---
# All the schedule pages you provided
SCHEDULE_PAGES = {
    "2026_Regular_Season": "https://nbsleague.wordpress.com/2026-regular-season-schedule/",
    "2026_Preseason": "https://nbsleague.wordpress.com/2026-preseason-schedule/",
    "2025_Playoffs": "https://nbsleague.wordpress.com/2025-playoff-schedule/",
    "2024_25_Regular_Season": "https://nbsleague.wordpress.com/2025-regular-season-schedule/"
}

# The standings pages
STANDINGS_PAGES = {
    "2026_Regular_Season": "https://nbsleague.wordpress.com/2026-standings/",
    "2024_25_Regular_Season": "https://nbsleague.wordpress.com/2025-standings/"
}

def scrape_data(urls_dict, output_filename, mode="schedule"):
    all_data = {}

    for season_name, url in urls_dict.items():
        print(f"Scraping {mode} for {season_name}...")
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print(f"  [!] No table found at {url}")
                continue
            
            rows = table.find_all('tr')
            season_entries = []
            
            if mode == "schedule":
                # Schedule Logic (Assumes: Away, Home, AwayScore, HomeScore)
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) >= 4:
                        season_entries.append({
                            "away_team": cols[0].text.strip(),
                            "home_team": cols[1].text.strip(),
                            "away_score": cols[2].text.strip(),
                            "home_score": cols[3].text.strip(),
                            "status": "Final"
                        })
            else:
                # Standings Logic (Grabs headers automatically)
                headers = [th.text.strip() for th in rows[0].find_all(['th', 'td'])]
                for row in rows[1:]:
                    cols = row.find_all('td')
                    if len(cols) > 0:
                        entry = {headers[i]: col.text.strip() for i, col in enumerate(cols) if i < len(headers)}
                        season_entries.append(entry)
            
            all_data[season_name] = season_entries
        except Exception as e:
            print(f"  [!] Error scraping {url}: {e}")

    with open(output_filename, 'w') as f:
        json.dump(all_data, f, indent=2)
    print(f"Successfully saved to {output_filename}")

if __name__ == "__main__":
    # Run the schedule mission
    scrape_data(SCHEDULE_PAGES, 'nbs_data.json', mode="schedule")
    
    # Run the standings mission
    scrape_data(STANDINGS_PAGES, 'nbs_standings.json', mode="standings")
