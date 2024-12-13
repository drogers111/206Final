import sqlite3
import requests

# Database setup
db_name = "pokemon.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create the PokémonGoStats table if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS PokemonGoStats (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    base_attack INTEGER,
    base_defense INTEGER,
    base_stamina INTEGER
)
""")
conn.commit()


def fetch_pokemon_go_data(start_id, end_id):
    """Fetch Pokémon stats from the Pokémon GO API for a range of IDs."""
    api_url = "https://pogoapi.net/api/v1/pokemon_stats.json"

    try:
        # Fetch the full dataset from the API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        for pokemon_id in range(start_id, end_id + 1):
            cursor.execute("SELECT id FROM PokemonGoStats WHERE id = ?", (pokemon_id,))
            if cursor.fetchone():
                print(f"Pokémon ID {pokemon_id} already in database, skipping.")
                continue

            # Find the Pokémon in the API data
            pokemon_data = next((p for p in data if int(p['pokemon_id']) == pokemon_id), None)
            if not pokemon_data:
                print(f"Pokémon ID {pokemon_id} not found in the API data, skipping.")
                continue

            # Prepare data for insertion
            pokemon = (
                int(pokemon_data['pokemon_id']),
                pokemon_data['pokemon_name'],
                int(pokemon_data['base_attack']),
                int(pokemon_data['base_defense']),
                int(pokemon_data['base_stamina']),
            )

            # Insert data into the database
            cursor.execute("""
            INSERT INTO PokemonGoStats (id, name, base_attack, base_defense, base_stamina)
            VALUES (?, ?, ?, ?, ?)
            """, pokemon)
            conn.commit()

            print(f"Stored data for Pokémon: {pokemon_data['pokemon_name']} (ID: {pokemon_id})")

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except (sqlite3.Error, KeyError, ValueError) as e:
        print(f"Error processing or storing data: {e}")


# Prompt user for a range of Pokémon IDs
start_id = int(input("Enter the starting Pokémon ID: "))
end_id = int(input("Enter the ending Pokémon ID: "))
fetch_pokemon_go_data(start_id, end_id)

# Close the database connection
conn.close()
