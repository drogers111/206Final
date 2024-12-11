import sqlite3
import requests
import matplotlib.pyplot as plt

# Connect to SQLite database
db_name = "pokemon.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Create the Pokemon table with the correct structure
cursor.execute("""
CREATE TABLE IF NOT EXISTS Pokemon (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    base_attack INTEGER,
    base_defense INTEGER,
    base_stamina INTEGER
)
""")
conn.commit()

def fetch_and_store_pokemon_stats(api_url):
    """
    Fetch Pokémon stats from the given API and store them in the database.
    """
    try:
        response = requests.get(api_url)
        response.raise_for_status() 
        data = response.json()

        for pokemon in data:
            # Extract data fields
            pokemon_id = int(pokemon['pokemon_id'])
            name = pokemon['pokemon_name']
            base_attack = int(pokemon['base_attack'])
            base_defense = int(pokemon['base_defense'])
            base_stamina = int(pokemon['base_stamina'])

            # #Debug information
            # print(f"Storing Pokémon: {name} (ID: {pokemon_id}, Attack: {base_attack})") 

            # Insert or replace into the database
            cursor.execute("""
            INSERT OR REPLACE INTO Pokemon (id, name, base_attack, base_defense, base_stamina)
            VALUES (?, ?, ?, ?, ?)
            """, (pokemon_id, name, base_attack, base_defense, base_stamina))

        conn.commit()
        print("Pokémon stats successfully stored in the database.")
    except Exception as e:
        print(f"Unexpected error: {e}")

def plot_attack_comparison(pokemon_ids):
    """
    Plot a bar chart comparing the base attack stats of the specified Pokémon.
    """
    pokemon_names = []
    attack_values = []

    for pokemon_id in pokemon_ids:
        cursor.execute("SELECT name, base_attack FROM Pokemon WHERE id = ?", (pokemon_id,))
        result = cursor.fetchone()
        if result:
            pokemon_names.append(result[0])
            attack_values.append(result[1])
        else:
            print(f"Pokémon ID {pokemon_id} not found in the database.")

    if pokemon_names and attack_values:
        # Plot the bar chart
        plt.bar(pokemon_names, attack_values, color='skyblue')
        plt.title("Comparison of Base Attack Stats")
        plt.xlabel("Pokémon")
        plt.ylabel("Base Attack")
        plt.tight_layout() 
        plt.show()
    else:
        print("No Pokémon data available for plotting.")

# Fetch and store Pokémon data from the API
api_url = "https://pogoapi.net/api/v1/pokemon_stats.json"
fetch_and_store_pokemon_stats(api_url)

# Plot comparison for specific Pokémon IDs
pokemon_ids = [1, 2]  
plot_attack_comparison(pokemon_ids)

# Close the database connection
conn.close()
