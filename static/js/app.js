document.addEventListener('DOMContentLoaded', () => {
    const map = L.map('map').setView([59.2753, 15.2134], 13);  // Updated to Örebro, Sweden

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let markers = [];
    let fetchTimer = null;

    const loadingIndicator = document.getElementById('loading');
    const errorMessage = document.getElementById('error-message');
    const errorText = document.getElementById('error-text');

    const showLoading = () => {
        loadingIndicator.style.display = 'block';
    };

    const hideLoading = () => {
        loadingIndicator.style.display = 'none';
    };

    const showError = (message) => {
        errorText.textContent = message;
        errorMessage.style.display = 'block';
    };

    const hideError = () => {
        errorMessage.style.display = 'none';
    };

    const categoryIcons = {
        "Historical": { icon: "fa-landmark", color: "#FF0000" },
        "Cultural": { icon: "fa-palette", color: "#00FF00" },
        "Natural": { icon: "fa-leaf", color: "#0000FF" },
        "Educational": { icon: "fa-graduation-cap", color: "#8B4513" },
        "Religious": { icon: "fa-place-of-worship", color: "#FF00FF" },
        "Commercial": { icon: "fa-store", color: "#00FFFF" },
        "Other": { icon: "fa-map-marker-alt", color: "#808080" }
    };

    const createCustomIcon = (category) => {
        const { icon, color } = categoryIcons[category] || categoryIcons["Other"];
        return L.divIcon({
            html: `<i class="fas ${icon} fa-2x" style="color: ${color};"></i>`,
            iconSize: [24, 24],
            className: 'custom-icon'
        });
    };

    const fetchLandmarks = async (searchQuery = '') => {
        const bounds = map.getBounds();
        const params = new URLSearchParams({
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest(),
            search: searchQuery
        });

        showLoading();
        hideError();

        try {
            const response = await fetch(`/get_landmarks?${params}`);
            console.log('Response from server:', response);
            if (!response.ok) {
                throw new Error('Failed to fetch landmarks');
            }
            const landmarks = await response.json();
            console.log('Parsed landmarks:', landmarks);
            displayLandmarks(landmarks);
        } catch (error) {
            console.error('Error fetching landmarks:', error);
            showError('Failed to fetch landmarks. Please try again later.');
        } finally {
            hideLoading();
        }
    };

    const displayLandmarks = (landmarks) => {
        console.log('Displaying landmarks:', landmarks);
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];

        landmarks.forEach(landmark => {
            console.log(`Creating marker for ${landmark.title}: lat ${landmark.lat}, lon ${landmark.lon}, category ${landmark.category}`);
            const marker = L.marker([landmark.lat, landmark.lon], {
                icon: createCustomIcon(landmark.category),
                category: landmark.category
            }).addTo(map);
            marker.bindPopup(`
                <b>${landmark.title}</b><br>
                ${landmark.summary}<br>
                <i class="fas ${categoryIcons[landmark.category].icon}" style="color: ${categoryIcons[landmark.category].color};"></i> ${landmark.category}
            `);
            markers.push(marker);
        });
    };

    const debounceFetchLandmarks = () => {
        clearTimeout(fetchTimer);
        fetchTimer = setTimeout(fetchLandmarks, 300);
    };

    map.on('moveend', debounceFetchLandmarks);

    const createLegend = () => {
        const legend = L.control({position: 'bottomright'});
        legend.onAdd = function(map) {
            const div = L.DomUtil.create('div', 'info legend');
            div.innerHTML = '<h4>Landmark Categories</h4>';
            for (const [category, { icon, color }] of Object.entries(categoryIcons)) {
                div.innerHTML += `
                    <div class="legend-item" data-category="${category}">
                        <input type="checkbox" id="${category}" checked>
                        <label for="${category}">
                            <i class="fas ${icon}" style="color: ${color};"></i> ${category}
                        </label>
                    </div>`;
            }
            return div;
        };
        legend.addTo(map);
        
        // Add change event listeners to checkboxes
        document.querySelectorAll('.legend-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                filterLandmarks();
            });
        });
    };

    const filterLandmarks = () => {
        const enabledCategories = Array.from(document.querySelectorAll('.legend-item input[type="checkbox"]:checked'))
            .map(checkbox => checkbox.id);
        
        console.log('Filtering landmarks. Enabled categories:', enabledCategories);
        
        markers.forEach(marker => {
            const category = marker.options.category;
            if (enabledCategories.includes(category)) {
                map.addLayer(marker);
            } else {
                map.removeLayer(marker);
            }
        });
    };

    createLegend();
    fetchLandmarks(); // Call this immediately after creating the map

    // New function to calculate midpoint
    const calculateMidpoint = (userLat, userLon, landmarksLat, landmarksLon) => {
        return [(userLat + landmarksLat) / 2, (userLon + landmarksLon) / 2];
    };

    // Updated user location tracking
    const locateUser = () => {
        if ("geolocation" in navigator) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const { latitude, longitude } = position.coords;
                    const initialLandmarksLat = 59.2753; // Örebro, Sweden
                    const initialLandmarksLon = 15.2134;
                    const midpoint = calculateMidpoint(latitude, longitude, initialLandmarksLat, initialLandmarksLon);
                    map.setView(midpoint, 13); // Increased zoom level from 10 to 13
                    L.marker([latitude, longitude], {
                        icon: L.divIcon({
                            html: '<i class="fas fa-user fa-2x" style="color: #4a69bd;"></i>',
                            iconSize: [24, 24],
                            className: 'custom-icon'
                        })
                    }).addTo(map).bindPopup("You are here!").openPopup();
                    fetchLandmarks(); // Fetch landmarks for the new view
                },
                (error) => {
                    console.error("Error getting user location:", error);
                    showError("Unable to retrieve your location. Please check your browser settings.");
                }
            );
        } else {
            showError("Geolocation is not supported by your browser.");
        }
    };

    // Create locate button with combined search functionality
    const locateControl = L.control({ position: 'topleft' });
    locateControl.onAdd = function (map) {
        const div = L.DomUtil.create('div', 'leaflet-control-locate-container leaflet-bar leaflet-control');
        div.innerHTML = `
          <button id="locate-search-btn" class="leaflet-control-locate" title="Locate Me / Search">
            <i class="fas fa-location-arrow"></i>
          </button>
          <div id="search-box" class="hidden">
            <input type="text" id="search-input" placeholder="Search landmarks...">
            <button id="search-submit"><i class="fas fa-search"></i></button>
          </div>
        `;
        return div;
    };
    locateControl.addTo(map);

    // Add event listeners for the new combined functionality
    const locateSearchBtn = document.getElementById('locate-search-btn');
    const searchBox = document.getElementById('search-box');
    const searchInput = document.getElementById('search-input');
    const searchSubmit = document.getElementById('search-submit');

    locateSearchBtn.addEventListener('click', () => {
        searchBox.classList.toggle('hidden');
        if (!searchBox.classList.contains('hidden')) {
            searchInput.focus();
        } else {
            locateUser();
        }
    });

    const performSearch = () => {
        const searchQuery = searchInput.value.trim();
        if (searchQuery) {
            fetchLandmarks(searchQuery);
            searchBox.classList.add('hidden');
        }
    };

    searchSubmit.addEventListener('click', performSearch);
    searchInput.addEventListener('keyup', (event) => {
        if (event.key === 'Enter') {
            performSearch();
        }
    });

    // Initial location request
    locateUser();
});
