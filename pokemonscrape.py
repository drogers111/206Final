import sqlite3
import requests
from bs4 import BeautifulSoup

# Database setup
db_name = "pokemon.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Ensure the PokemonImages table exists correctly
cursor.execute("""
CREATE TABLE PokemonImages (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    image BLOB NOT NULL,
    FOREIGN KEY (id) REFERENCES Pokemon(id)
)
""")
conn.commit()

def fetch_and_store_images(start_id, end_id):
    url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the webpage.")
        return
    
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("td", style="font-family:monospace,monospace")

    for row in rows:
        # Extract Pokémon ID (e.g., "#0001")
        pokemon_id_text = row.text.strip()
        if not pokemon_id_text.startswith("#"):
            continue
        
        # Convert to numeric ID
        pokemon_id = int(pokemon_id_text.strip("#"))
        
        if not (start_id <= pokemon_id <= end_id):
            continue

        # Find the next sibling containing the image
        image_td = row.find_next_sibling("td")
        img_tag = image_td.find("img") if image_td else None
        if not img_tag or "src" not in img_tag.attrs:
            print(f"No image found for Pokémon ID {pokemon_id}.")
            continue

        # Extract the image URL and download it
        image_url = img_tag['src']
        if not image_url.startswith("http"):
            image_url = f"https:{image_url}"  

        img_response = requests.get(image_url)
        if img_response.status_code != 200:
            print(f"Failed to download image for Pokémon ID {pokemon_id}.")
            continue

        # Convert image content to binary
        image_data = img_response.content

        # Get Pokémon name from the database
        cursor.execute("SELECT name FROM pokemon WHERE id = ?", (pokemon_id,))
        result = cursor.fetchone()
        if not result:
            print(f"No Pokémon found for ID {pokemon_id}, skipping.")
            continue
        pokemon_name = result[0]

        # Insert into database
        cursor.execute("""
        INSERT INTO PokemonImages (id, name, image)
        VALUES (?, ?, ?)
        """, (pokemon_id, pokemon_name, image_data))
        conn.commit()
        print(f"Stored image for Pokémon: {pokemon_name} (ID: {pokemon_id})")

# Prompt user for a range of Pokémon IDs
start_id = int(input("Enter the starting Pokémon ID: "))
end_id = int(input("Enter the ending Pokémon ID: "))
fetch_and_store_images(start_id, end_id)

# Close the database connection
conn.close()