const pokemonGrid = document.getElementById('pokemon-grid');
const searchBar = document.getElementById('search-bar');
const typeFilter = document.getElementById('type-filter');
const abilityFilter = document.getElementById('ability-filter');
let allPokemonData = [];
const maxPokemonId = 1025;

function fetchRandomPokemon(numPokemon) {
    const uniqueIds = Array.from({ length: numPokemon }, function() {
        return Math.floor(Math.random() * maxPokemonId) + 1;
    });

    const pokemonPromises = uniqueIds.map(function(id) {
        return fetch('https://pokeapi.co/api/v2/pokemon/' + id)
            .then(function(response) {
                return response.ok ? response.json() : null;
            })
            .catch(function() {
                return null;
            });
    });

    Promise.all(pokemonPromises).then(function(pokemonData) {
        allPokemonData = pokemonData.filter(Boolean);
        displayPokemon(allPokemonData);
    });
}

function displayPokemon(pokemonData) {
    pokemonGrid.innerHTML = '';

    pokemonData.forEach(function(pokemon) {
        const card = document.createElement('div');
        card.classList.add('pokemon-card');

        // Image
        const img = document.createElement('img');
        img.src = pokemon.sprites.front_default || 'placeholder.png';
        img.alt = pokemon.name;
        card.appendChild(img);

        // Name
        const nameElement = document.createElement('h3');
        nameElement.textContent = pokemon.name;
        card.appendChild(nameElement);

        // Stats container
        const statsContainer = document.createElement('div');
        statsContainer.classList.add('pokemon-stats');

        // Stats
        pokemon.stats.forEach(function(stat) {
            const statParagraph = document.createElement('p');
            statParagraph.textContent = stat.stat.name.toUpperCase() + ': ' + stat.base_stat;
            statsContainer.appendChild(statParagraph);
        });

        // Total Stats
        const total = pokemon.stats.reduce(function(sum, stat) {
            return sum + stat.base_stat;
        }, 0);
        const totalParagraph = document.createElement('p');
        totalParagraph.textContent = 'Total: ' + total;
        statsContainer.appendChild(totalParagraph);
        card.appendChild(statsContainer);

        // Types
        const typesContainer = document.createElement('div');
        pokemon.types.forEach(function(type) {
            const typeSpan = document.createElement('span');
            typeSpan.className = 'type-icon ' + type.type.name; // Use CSS for styling
            typeSpan.textContent = type.type.name;
            typesContainer.appendChild(typeSpan);
        });
        card.appendChild(typesContainer);

        // Append card to grid
        pokemonGrid.appendChild(card);
    });
}

function searchPokemon() {
    const query = searchBar.value.toLowerCase();
    const filteredPokemon = allPokemonData.filter(function(pokemon) {
        return pokemon.name.toLowerCase().includes(query) || pokemon.id.toString().includes(query);
    });
    displayPokemon(filteredPokemon);
}

function populateTypes() {
    fetch('https://pokeapi.co/api/v2/type')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            data.results.forEach(function(type) {
                const option = document.createElement('option');
                option.value = type.name;
                option.textContent = type.name;
                typeFilter.appendChild(option);
            });
        });
}

function populateAbilities() {
    fetch('https://pokeapi.co/api/v2/ability')
        .then(function(response) {
            return response.json();
        })
        .then(function(data) {
            data.results.forEach(function(ability) {
                const option = document.createElement('option');
                option.value = ability.name;
                option.textContent = ability.name;
                abilityFilter.appendChild(option);
            });
        });
}

function filterByTypeAndAbility() {
    const selectedType = typeFilter.value;
    const selectedAbility = abilityFilter.value;

    const filteredData = allPokemonData.filter(function(pokemon) {
        const matchesType = selectedType === 'all' || pokemon.types.some(function(t) {
            return t.type.name === selectedType;
        });
        const matchesAbility = selectedAbility === 'all' || pokemon.abilities.some(function(a) {
            return a.ability.name === selectedAbility;
        });
        return matchesType && matchesAbility;
    });

    displayPokemon(filteredData);
}

// Event listeners for filtering and searching
typeFilter.addEventListener('change', filterByTypeAndAbility);
abilityFilter.addEventListener('change', filterByTypeAndAbility);
searchBar.addEventListener('input', searchPokemon);

// Initial population of types and abilities
populateTypes();
populateAbilities();
fetchRandomPokemon(151);
