document.addEventListener('DOMContentLoaded', () => {
    // Initialize the map
    const map = L.map('map').setView([0, 0], 2);

    // Add the OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Function to fetch landmarks
    const fetchLandmarks = async () => {
        try {
            const response = await fetch('/get_landmarks');
            const landmarks = await response.json();
            displayLandmarks(landmarks);
        } catch (error) {
            console.error('Error fetching landmarks:', error);
        }
    };

    // Function to display landmarks on the map
    const displayLandmarks = (landmarks) => {
        landmarks.forEach(landmark => {
            const marker = L.marker([landmark.lat, landmark.lon]).addTo(map);
            marker.bindPopup(`<b>${landmark.title}</b><br>${landmark.summary}`);
        });
    };

    // Fetch landmarks when the map is moved
    map.on('moveend', fetchLandmarks);

    // Initial fetch of landmarks
    fetchLandmarks();
});
