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

cursor.execute("""
CREATE TABLE IF NOT EXISTS Moves (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    base_power INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS PokemonMoves (
    pokemon_id INTEGER NOT NULL,
    move_id INTEGER NOT NULL,
    PRIMARY KEY (pokemon_id, move_id),
    FOREIGN KEY (pokemon_id) REFERENCES Pokemon(id),
    FOREIGN KEY (move_id) REFERENCES Moves(id)
)
""")
conn.commit()

def fetch_pokemon_data():
    url_base = "https://pokeapi.co/api/v2/pokemon/"
    cursor.execute("SELECT COUNT(*) FROM Pokemon")
    current_count = cursor.fetchone()[0]

    if current_count >= 100:
        print("Pokemon table already contains 100 or more rows. Skipping Pokémon fetch.")
        return

    rows_added = 0
    for pokemon_id in range(1, 1025):
        if rows_added >= 25:
            print("Reached limit of 25 new Pokémon entries for this execution.")
            break

        cursor.execute("SELECT id FROM Pokemon WHERE id = ?", (pokemon_id,))
        if cursor.fetchone():
            print(f"Pokémon ID {pokemon_id} already in database, skipping.")
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


def fetch_moves():
    url_base = "https://pokeapi.co/api/v2/move/"
    cursor.execute("SELECT COUNT(*) FROM Moves")
    current_move_count = cursor.fetchone()[0]

    if current_move_count >= 100:
        print("Moves table already contains 100 or more rows. Skipping move fetch.")
        return

    move_rows_added = 0
    move_id = 1

    # Get all existing move IDs in the database before fetching new ones
    cursor.execute("SELECT id FROM Moves")
    existing_move_ids = {row[0] for row in cursor.fetchall()}  # Set for fast lookup

    while move_rows_added < 25:
        try:
            # Skip if move is already in the database
            if move_id in existing_move_ids:
                print(f"Move ID {move_id} already exists, skipping API request.")
                move_id += 1
                continue

            # Fetch move data from the API if not already in the database
            response = requests.get(f"{url_base}{move_id}")
            if response.status_code == 404:  # End of available moves
                break
            if response.status_code != 200:
                print(f"Failed to fetch move ID {move_id}")
                move_id += 1
                continue

            data = response.json()

            # Insert move into Moves table
            move_name = data['name']
            move_type = data['type']['name']
            base_power = data.get('power') or 0
            cursor.execute("""
            INSERT INTO Moves (id, name, type, base_power)
            VALUES (?, ?, ?, ?)
            """, (data['id'], move_name, move_type, base_power))

            conn.commit()
            move_rows_added += 1
            print(f"Stored move: {move_name} (ID: {move_id})")

            # Add the new move ID to the set of existing IDs to avoid future API calls for it
            existing_move_ids.add(move_id)

            move_id += 1  # Increment move ID to fetch the next move

        except Exception as e:
            print(f"Error processing move ID {move_id}: {e}")
            move_id += 1


def fetch_pokemon_moves():
    cursor.execute("SELECT COUNT(*) FROM PokemonMoves")
    current_pokemon_moves_count = cursor.fetchone()[0]

    if current_pokemon_moves_count >= 100:
        print("PokemonMoves table already contains 100 or more rows. Skipping Pokémon-move relationships fetch.")
        return

    move_id = 1
    moves_fetched = 0  # Counter to track how many moves have been processed

    while moves_fetched < 25:  # Fetch and process only 25 moves
        try:
            url = f"https://pokeapi.co/api/v2/move/{move_id}"
            response = requests.get(url)
            if response.status_code == 404:  # No more moves available
                print("No more moves available. Stopping.")
                break
            if response.status_code != 200:
                print(f"Failed to fetch move ID {move_id}")
                move_id += 1
                continue

            data = response.json()

            # Insert Pokémon-move relationships
            for pokemon in data['learned_by_pokemon']:
                pokemon_name = pokemon['name']
                cursor.execute("SELECT id FROM Pokemon WHERE name = ?", (pokemon_name,))
                result = cursor.fetchone()

                if result:
                    pokemon_id = result[0]
                    cursor.execute("""
                    INSERT OR IGNORE INTO PokemonMoves (pokemon_id, move_id)
                    VALUES (?, ?)
                    """, (pokemon_id, data['id']))

            conn.commit()

            # Increment the number of moves processed
            moves_fetched += 1

            move_id += 1  

        except Exception as e:
            print(f"Error processing move ID {move_id}: {e}")
            move_id += 1  




def main():
    fetch_pokemon_data()
    fetch_moves()
    fetch_pokemon_moves()


if __name__ == "__main__":
    main()

conn.close()