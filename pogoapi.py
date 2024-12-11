import sqlite3
import requests
import matplotlib.pyplot as plt

DB_NAME = "pokemon.db"  # Constant for database name
API_URL = "https://pogoapi.net/api/v1/pokemon_stats.json" # Constant for API URL


def create_pokemon_table(cursor):
    """Creates the Pokemon table if it doesn't exist."""
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Pokemon (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE, 
        base_attack INTEGER,
        base_defense INTEGER,
        base_stamina INTEGER
    )
    """)

def fetch_and_store_pokemon_stats(cursor, api_url):
    """Fetches Pokémon stats and stores them in the database."""
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        # Efficiently insert/update using executemany
        pokemon_data = [(int(p['pokemon_id']), p['pokemon_name'], int(p['base_attack']), int(p['base_defense']), int(p['base_stamina'])) for p in data]
        cursor.executemany("""
            INSERT OR REPLACE INTO Pokemon (id, name, base_attack, base_defense, base_stamina)
            VALUES (?, ?, ?, ?, ?)
        """, pokemon_data)

        return True # Indicate success
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return False
    except (sqlite3.Error, KeyError, ValueError) as e:  # Catch specific DB and data errors
        print(f"Error processing or storing data: {e}")
        return False


def plot_attack_comparison(cursor, pokemon_ids):
    """Plots a bar chart comparing base attack stats."""
    pokemon_names, attack_values = [], []
    try:
      cursor.execute("SELECT name, base_attack FROM Pokemon WHERE id IN ({})".format(",".join(["?"] * len(pokemon_ids))), pokemon_ids) #More efficient query for multiple pokemon ids.
      results = cursor.fetchall()
      if results:
          pokemon_names = [row[0] for row in results]
          attack_values = [row[1] for row in results]
      else:
          print("Pokémon IDs not found in the database.")

      if pokemon_names and attack_values:
          plt.bar(pokemon_names, attack_values, color='skyblue')
          plt.title("Comparison of Base Attack Stats")
          plt.xlabel("Pokémon")
          plt.ylabel("Base Attack")
          plt.tight_layout()
          plt.show()
    except sqlite3.Error as e:
        print(f"Database error during plotting: {e}")



def main():
    """Main function to manage database and plotting."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    create_pokemon_table(cursor)

    if fetch_and_store_pokemon_stats(cursor, API_URL):
        print("Data successfully fetched and stored (or updated).")
        pokemon_ids = [1, 25, 150] 
        plot_attack_comparison(cursor, pokemon_ids)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    main()