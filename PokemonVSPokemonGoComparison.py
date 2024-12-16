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

# Retrieve and process data
def process_data(conn):
    try:
        query = """
        SELECT 
            p.id AS Pokemon_ID,
            p.name AS Pokemon,
            (p.attack + p.special_attack) AS Pokemon_Attack,
            g.base_attack AS PokemonGo_Base_Attack
        FROM pokemon p
        INNER JOIN pokemongostats g ON p.id = g.id
        """
        df = pd.read_sql_query(query, conn)

        # Calculate averages
        avg_pokemon_attack = df['Pokemon_Attack'].mean()
        avg_pokemongo_attack = df['PokemonGo_Base_Attack'].mean()

        # Prepare comparison data
        comparison = pd.DataFrame({
            'Source': ['Pokemon (Attack + Special Attack)', 'Pokemon Go (Base Attack)'],
            'Average_Attack': [avg_pokemon_attack, avg_pokemongo_attack]
        })

        return df, comparison
    except Exception as e:
        print(f"Error processing data: {e}")
        return None, None

# Visualize data
def visualize_data(df, comparison):
    try:
        # Visualization 1: Distribution of Attack Values (Pokemon vs PokemonGoStats)
        plt.figure(figsize=(10, 6))
        df[['Pokemon_Attack', 'PokemonGo_Base_Attack']].plot(kind='box')
        plt.title('Distribution of Attack Values')
        plt.ylabel('Attack Values')
        plt.xticks([1, 2], ['Pokemon (Attack + Special Attack)', 'Pokemon Go (Base Attack)'])
        plt.savefig('attack_distribution.png')
        plt.close()
        print("Attack distribution plot saved as 'attack_distribution.png'.")

        # Visualization 2: Average Attack Comparison
        plt.figure(figsize=(8, 6))
        plt.bar(comparison['Source'], comparison['Average_Attack'], color=['blue', 'orange'])
        plt.title('Average Attack Value (Pokemon vs PokemonGO)')
        plt.xlabel('Game')
        plt.ylabel('Average Attack')
        plt.savefig('average_attack_comparison.png')
        plt.close()
        print("Average Attack Comparison plot saved as 'average_attack_comparison.png'.")
    except Exception as e:
        print(f"Error visualizing data: {e}")

def main():
    db_path = 'pokemon.db' 
    conn = connect_db(db_path)
    if conn:
        df, comparison = process_data(conn)
        if df is not None and comparison is not None:
            visualize_data(df, comparison)
        conn.close()

if __name__ == "__main__":
    main()
