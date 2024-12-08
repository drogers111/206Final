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
CREATE TABLE IF NOT EXISTS PokemonDetails (
    id INTEGER NOT NULL,
    type TEXT NOT NULL, -- 'move' or 'ability'
    name TEXT NOT NULL,
    detail TEXT,
    FOREIGN KEY (id) REFERENCES Pokemon(id)
)
""")
conn.commit()


def fetch_pokemon_data(start_id, end_id):
    url_base = "https://pokeapi.co/api/v2/pokemon/"
    for pokemon_id in range(start_id, end_id + 1):
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

            # Insert moves into PokemonDetails table
            for move in data['moves']:
                move_name = move['move']['name']
                learn_method = ", ".join(
                    method['move_learn_method']['name'] for method in move['version_group_details']
                )
                cursor.execute("""
                INSERT INTO PokemonDetails (id, type, name, detail)
                VALUES (?, ?, ?, ?)
                """, (data['id'], 'move', move_name, learn_method))

            # Insert abilities into PokemonDetails table
            for ability in data['abilities']:
                ability_name = ability['ability']['name']
                is_hidden = "hidden" if ability['is_hidden'] else "normal"
                cursor.execute("""
                INSERT INTO PokemonDetails (id, type, name, detail)
                VALUES (?, ?, ?, ?)
                """, (data['id'], 'ability', ability_name, is_hidden))

            conn.commit()
            print(f"Stored data for Pokémon: {data['name']} (ID: {data['id']})")

        except Exception as e:
            print(f"Error processing Pokémon ID {pokemon_id}: {e}")


# Prompt user for a range of Pokémon IDs
start_id = int(input("Enter the starting Pokémon ID: "))
end_id = int(input("Enter the ending Pokémon ID: "))
fetch_pokemon_data(start_id, end_id)

# Close the database connection
conn.close()
