import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import json

# Connect to the database
def connect_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Retrieve data for specific Pokemon
def fetch_pokemon_stats(conn):
    try:
        query = """
        SELECT 
            p.name AS Pokemon,
            p.hp, p.attack, p.defense, p.special_attack, p.special_defense, p.speed
        FROM pokemon p
        WHERE p.name IN ('bulbasaur', 'ivysaur')
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching Pokemon stats: {e}")
        return None

# Calculate averages and differences
def calculate_averages_and_differences(df):
    try:
        stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']
        averages = df[stats].mean().astype(float)
        differences = (df[df['Pokemon'] == 'ivysaur'][stats].values[0] - 
                       df[df['Pokemon'] == 'bulbasaur'][stats].values[0]).astype(float)

        result = {
            'averages': averages.to_dict(),
            'differences': dict(zip(stats, differences))
        }

        # Save results to a text file
        try: 
            with open('calculatedValues.txt', 'a') as f:
                f.write("Base Stats Averages of Bulbasaur and Ivysaur:\n")
                json.dump(result['averages'], f, indent=4)
                f.write("\n\nBase Stats Differences (Ivysaur - Bulbasaur):\n")
                json.dump(result['differences'], f, indent=4)
        except Exception as e:
            print(f'Error writing to file: {e}')

        print("Calculations written to 'bulbasaur_ivysaur_stats.txt'.")
        return result
    except Exception as e:
        print(f"Error calculating averages and differences: {e}")
        return None

# Visualize data
def visualize_pokemon_stats(df):
    try:
        stats = ['hp', 'attack', 'defense', 'special_attack', 'special_defense', 'speed']

        # Create a dot plot
        plt.figure(figsize=(10, 6))
        for idx, row in df.iterrows():
            color = 'blue' if row['Pokemon'] == 'bulbasaur' else 'green'
            plt.scatter(stats, row[stats], label=row['Pokemon'], color=color, s=100)

        plt.title('Base Stats Comparison: Bulbasaur vs Ivysaur')
        plt.xlabel('Stats')
        plt.ylabel('Values')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        plt.savefig('bulbasaur_ivysaur_dot_plot.png')
        print("Dot plot saved as 'bulbasaur_ivysaur_dot_plot.png'.")
    except Exception as e:
        print(f"Error visualizing Pokemon stats: {e}")

def main():
    db_path = 'pokemon.db' 
    conn = connect_db(db_path)
    if conn:
        specific_pokemon_df = fetch_pokemon_stats(conn)
        if specific_pokemon_df is not None:
            calculate_averages_and_differences(specific_pokemon_df)
            visualize_pokemon_stats(specific_pokemon_df)
        conn.close()

if __name__ == "__main__":
    main()
