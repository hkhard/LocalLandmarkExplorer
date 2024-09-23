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
        "Educational": { icon: "fa-graduation-cap", color: "#FFFF00" },
        "Religious": { icon: "fa-place-of-worship", color: "#FF00FF" },
        "Commercial": { icon: "fa-store", color: "#00FFFF" },
        "Other": { icon: "fa-map-marker-alt", color: "#FFFFFF" }
    };

    const createCustomIcon = (category) => {
        const { color } = categoryIcons[category] || categoryIcons["Other"];
        return L.divIcon({
            html: `<div class="pin" style="background-color: ${color};"></div>`,
            iconSize: [30, 30],
            iconAnchor: [15, 30],
            popupAnchor: [0, -30],
            className: 'custom-icon'
        });
    };

    const fetchLandmarks = async () => {
        const bounds = map.getBounds();
        const params = new URLSearchParams({
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        });

        showLoading();
        hideError();

        try {
            const response = await fetch(`/get_landmarks?${params}`);
            if (!response.ok) {
                throw new Error('Failed to fetch landmarks');
            }
            const landmarks = await response.json();
            console.log('Fetched landmarks:', landmarks);
            displayLandmarks(landmarks);
        } catch (error) {
            console.error('Error fetching landmarks:', error);
            showError('Failed to fetch landmarks. Please try again later.');
        } finally {
            hideLoading();
        }
    };

    const displayLandmarks = (landmarks) => {
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];

        landmarks.forEach(landmark => {
            console.log(`Creating marker for ${landmark.title}: lat ${landmark.lat}, lon ${landmark.lon}, category ${landmark.category}`);
            const marker = L.marker([landmark.lat, landmark.lon], {icon: createCustomIcon(landmark.category)}).addTo(map);
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
                div.innerHTML += `<div><i class="fas ${icon}" style="color: ${color};"></i> ${category}</div>`;
            }
            return div;
        };
        legend.addTo(map);
    };

    createLegend();
    fetchLandmarks();
});
