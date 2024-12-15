import sqlite3
import requests
from bs4 import BeautifulSoup

# Database setup
db_name = "pokemon.db"
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Ensure the Pokemon table has an image column if it doesn't already exist
try:
    cursor.execute("""
    ALTER TABLE Pokemon
    ADD COLUMN image BLOB
    """)
    conn.commit()
except sqlite3.OperationalError:
    pass

# Function to fetch and store images
def fetch_and_store_images():
    url = "https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number"
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the webpage.")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all("tr")  # We'll loop through all the rows in the table

    # Check current count of Pokémon with images in the database
    cursor.execute("SELECT COUNT(*) FROM Pokemon WHERE image IS NOT NULL")
    current_count = cursor.fetchone()[0]

    rows_added = 0
    for row in rows:
        # Find the ID column (first <td>)
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # Extract Pokémon ID (e.g., "#0001")
        pokemon_id_text = cols[0].text.strip()
        if not pokemon_id_text.startswith("#"):
            continue

        # Convert to numeric ID
        pokemon_id = int(pokemon_id_text.strip("#"))

        # Stop processing based on defined limits (25 stored per time ran up until program has been ran 4 times and stored 100 items)
        if rows_added >= 25 and current_count < 76:
            print("Reached limit of 25 new Pokémon entries for this execution.")
            break
        if rows_added >= 100:
            print("100 Pokémon images added, run again for the next batch.")
            break

        # Check if the Pokémon ID already has an image in the database, if so, skip
        cursor.execute("SELECT image FROM Pokemon WHERE id = ?", (pokemon_id,))
        result = cursor.fetchone()
        if result and result[0] is not None:
            continue

        # Extract Pokémon name from the third <td>
        pokemon_name = cols[2].find("a").text.strip()

        # Find the image URL in the second <td> (contains <img>)
        img_tag = cols[1].find("img") if len(cols) > 1 else None
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

        # Update the image column in the Pokemon table
        cursor.execute("""
        UPDATE Pokemon
        SET image = ?
        WHERE id = ?
        """, (image_data, pokemon_id))
        conn.commit()

        rows_added += 1
        print(f"Stored image for Pokémon: {pokemon_name} (ID: {pokemon_id})")

# Run the script
fetch_and_store_images()

# Close the database connection
conn.close()