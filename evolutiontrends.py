import sqlite3
import matplotlib.pyplot as plt
import pandas as pd

# Connect to the database
def connect_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None

# Retrieve data for specific Pokémon evolution line (Bulbasaur, Ivysaur, Venusaur)
def fetch_evolution_data(conn):
    try:
        query = f"""
        SELECT 
            p.name, p.hp, p.attack, p.defense
        FROM pokemon p
        WHERE p.name IN ('bulbasaur', 'ivysaur', 'venusaur')
        """
        df = pd.read_sql_query(query, conn)
        return df
    except Exception as e:
        print(f"Error fetching evolution stats: {e}")
        return None

# Plotting the line chart for stat progression
def plot_stat_progression(df):
    try:
        stats = ['hp', 'attack', 'defense']
        
        # Create plot
        plt.figure(figsize=(10, 6))
        for stat in stats:
            plt.plot(df['name'], df[stat], label=stat.capitalize(), marker='o')
        
        plt.title('Stat Progression for Evolution Line: Bulbasaur → Ivysaur → Venusaur')
        plt.xlabel('Pokemon')
        plt.ylabel('Base Stat Value')
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()
        
        plt.savefig('evolution_stat_progression.png')
        print("Line chart saved as 'evolution_stat_progression.png'.")
    except Exception as e:
        print(f"Error plotting evolution data: {e}")

def main():
    db_path = 'pokemon.db'
    conn = connect_db(db_path)
    if conn:
        evolution_df = fetch_evolution_data(conn)
        if evolution_df is not None:
            plot_stat_progression(evolution_df)
        conn.close()

if __name__ == "__main__":
    main()