import requests
from bs4 import BeautifulSoup
import json

def scrape_nbs_league():
    pages_to_scrape = {
        "2026_Regular_Season": "https://nbsleague.wordpress.com/2026-regular-season-schedule/",
        "2026_Preseason": "https://nbsleague.wordpress.com/2026-preseason-schedule/",
        "2025_Playoffs": "https://nbsleague.wordpress.com/2025-playoff-schedule/",
        "2024_25_Regular_Season": "https://nbsleague.wordpress.com/2025-regular-season-schedule/"
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    all_league_data = {}

    for season_name, url in pages_to_scrape.items():
        print(f"Scouting {season_name}...")
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            season_games = []
            # Find all tables on the page
            tables = soup.find_all('table')
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cols = row.find_all('td')
                    # Based on your HTML, we need at least 4 columns
                    if len(cols) >= 4:
                        # Column 2 (index 2) has the Team names
                        # We use get_text with a separator to handle the <br> tags
                        teams_raw = cols[2].get_text(separator="|").split("|")
                        teams = [t.strip() for t in teams_raw if t.strip()]
                        
                        # Column 3 (index 3) has the Scores
                        scores_raw = cols[3].get_text(separator="|").split("|")
                        scores = [s.strip() for s in scores_raw if s.strip()]
                        
                        if len(teams) >= 2 and len(scores) >= 2:
                            season_games.append({
                                "away_team": teams[0],
                                "home_team": teams[1],
                                "away_score": scores[0],
                                "home_score": scores[1],
                                "status": cols[4].get_text().strip() if len(cols) > 4 else "N/A"
                            })
            
            all_league_data[season_name] = season_games
            print(f"  > Found {len(season_games)} games.")

        except Exception as e:
            print(f"  > Error scouting {season_name}: {e}")

    return all_league_data

if __name__ == "__main__":
    data = scrape_nbs_league()
    with open("nbs_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print("\nLeague Scouting Complete! Check nbs_data.json")