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
    base_attack INTEGER,
    base_defense INTEGER,
    base_stamina INTEGER
)
""")
conn.commit()


def fetch_pokemon_go_data():
    """Fetch Pokémon stats from the Pokémon GO API with row and count limits."""
    api_url = "https://pogoapi.net/api/v1/pokemon_stats.json"

    # Check current count of Pokémon in the database
    cursor.execute("SELECT COUNT(*) FROM PokemonGoStats")
    current_count = cursor.fetchone()[0]

    rows_added = 0

    try:
        # Fetch the full dataset from the API
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()

        for pokemon_data in data:
            pokemon_id = int(pokemon_data['pokemon_id'])

            # Stop processing based on defined limits (25 stored per time ran up until program has been ran 4 times and stored 100 items)
            if rows_added >= 25 and current_count < 76:
                print("25 PokemonGo Pokemon added to table PokemonGoStats.")
                break
            if rows_added >= 100:
                print("100 PokemonGo Pokemon added to table PokemonGoStats, run again for the next batch.")
                break

            #Ensuring unique constraint met
            cursor.execute("SELECT id FROM PokemonGoStats WHERE id = ?", (pokemon_id,))
            if cursor.fetchone():
                continue

            # Prepare data for insertion
            pokemon = (
                pokemon_id,
                int(pokemon_data['base_attack']),
                int(pokemon_data['base_defense']),
                int(pokemon_data['base_stamina']),
            )

            # Insert data into the database
            cursor.execute("""
            INSERT INTO PokemonGoStats (id, base_attack, base_defense, base_stamina)
            VALUES (?, ?, ?, ?)
            """, pokemon)
            conn.commit()

            rows_added += 1

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
    except (sqlite3.Error, KeyError, ValueError) as e:
        print(f"Error processing or storing data: {e}")


# Run the script
fetch_pokemon_go_data()

# Close the database connection
conn.close()