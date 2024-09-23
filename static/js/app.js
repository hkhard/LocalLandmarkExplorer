document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([0, 0], 2);

    // Add the OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    let markers = [];

    // Function to fetch landmarks
    const fetchLandmarks = async () => {
        const bounds = map.getBounds();
        const params = new URLSearchParams({
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest()
        });

        try {
            const response = await fetch(`/get_landmarks?${params}`);
            const landmarks = await response.json();
            displayLandmarks(landmarks);
        } catch (error) {
            console.error('Error fetching landmarks:', error);
        }
    };

    // Function to display landmarks on the map
    const displayLandmarks = (landmarks) => {
        // Clear existing markers
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];

        landmarks.forEach(landmark => {
            const marker = L.marker([landmark.lat, landmark.lon]).addTo(map);
            marker.bindPopup(`<b>${landmark.title}</b><br>${landmark.summary}`);
            markers.push(marker);
        });
    };

    // Fetch landmarks when the map is moved or zoomed
    map.on('moveend', fetchLandmarks);

    // Initial fetch of landmarks
    fetchLandmarks();
});
