import sqlite3
import requests

# Create or connect to SQLite database
db_name = "pokemon.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS Pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    hp INTEGER,
    attack INTEGER,
    defense INTEGER,
    special_attack INTEGER,
    special_defense INTEGER,
    speed INTEGER
)
""")

conn.commit()

def fetch_pokemon_data():
    url_base = "https://pokeapi.co/api/v2/pokemon/"
    cursor.execute("SELECT COUNT(*) FROM Pokemon")
    current_count = cursor.fetchone()[0]

    rows_added = 0
    for pokemon_id in range(1, 1026):
        # Stop processing based on defined limits (25 stored per time ran up until program has been ran 4 times and stored 100 items)
        if (rows_added >= 25 and current_count < 76):
            print("Reached limit of 25 new Pokémon entries for this execution.")
            break
        if (rows_added >= 100):
            print("100 Pokemon Added, run again for the next 100")
            break
        
        #Check if pokemon in database. If so, skip to next
        cursor.execute("SELECT id FROM Pokemon WHERE id = ?", (pokemon_id,))
        if cursor.fetchone():
            continue

        try:
            response = requests.get(f"{url_base}{pokemon_id}")
            if response.status_code != 200:
                print(f"Failed to fetch data for Pokémon ID {pokemon_id}")
                continue

            data = response.json()

            # Insert into Pokemon table
            stats = {stat['stat']['name']: stat['base_stat'] for stat in data['stats']}
            pokemon = (
                data['id'],
                data['name'],
                stats.get('hp'),
                stats.get('attack'),
                stats.get('defense'),
                stats.get('special-attack'),
                stats.get('special-defense'),
                stats.get('speed'),
            )
            cursor.execute("""
            INSERT INTO Pokemon (id, name, hp, attack, defense, special_attack, special_defense, speed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, pokemon)
            conn.commit()

            rows_added += 1
            print(f"Stored data for Pokémon: {data['name']} (ID: {data['id']})")

        except Exception as e:
            print(f"Error processing Pokémon ID {pokemon_id}: {e}")

def main():
    fetch_pokemon_data()


if __name__ == "__main__":
    main()

conn.close()