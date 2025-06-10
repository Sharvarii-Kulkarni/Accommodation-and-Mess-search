document.addEventListener("DOMContentLoaded", function () {
    const userId = localStorage.getItem("user_id");
    const userInfo = document.querySelector("#user-info");
    const logoutBtn = document.querySelector("#logout-btn");

    // Fetch user details if logged in
    if (userInfo) {
        if (!userId) {
            userInfo.textContent = "Not logged in";
        } else {
            fetch(`http://127.0.0.1:5000/get_user/${userId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        userInfo.textContent = "Error fetching user";
                    } else {
                        userInfo.innerHTML = `<strong>${data.name}</strong><br>${data.email}`;
                    }
                })
                .catch(error => {
                    console.error("Error fetching user:", error);
                    userInfo.textContent = "Error loading user";
                });
        }
    }

    // Handle Login
    const loginForm = document.querySelector("#login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const email = document.querySelector("#email").value;
            const password = document.querySelector("#password").value;

            fetch("http://127.0.0.1:5000/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.user_id) {
                        alert("Login successful!");
                        localStorage.setItem("user_id", data.user_id);
                        window.location.href = "home.html";
                    } else {
                        alert("Invalid credentials!");
                    }
                })
                .catch(error => console.error("Error:", error));
        });
    }

    // Logout functionality
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (event) {
            event.preventDefault();
            localStorage.removeItem("user_id");
            alert("Logged out successfully!");
            window.location.href = "login.html";
        });
    }
});

// Global map variables
let map;
let markers = [];
const defaultLocation = { lat: 18.5204, lng: 73.8567 }; // Pune default center
let userLocationMarker = null;
let locationButton = null;
let directionsService = null;
let directionsRenderer = null;
let activeInfoWindow = null;

// Initialize Google Map
function initMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        center: defaultLocation,
        zoom: 12,
        styles: [{ featureType: "poi", elementType: "labels", stylers: [{ visibility: "off" }] }]
    });

    directionsService = new google.maps.DirectionsService();
    directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
        polylineOptions: { strokeColor: "#4285F4", strokeWeight: 5, strokeOpacity: 0.7 }
    });
    directionsRenderer.setMap(map);

    locationButton = document.createElement("button");
    locationButton.innerHTML = '<i class="fas fa-location-arrow"></i> You Are Here';
    locationButton.classList.add("custom-map-control");
    locationButton.addEventListener("click", getUserLocation);
    map.controls[google.maps.ControlPosition.TOP_RIGHT].push(locationButton);

    // Load initial data based on page
    if (document.querySelector("#accommodation-search-form")) {
        fetchAllAccommodations();
    } else if (document.querySelector("#mess-search-form")) {
        fetchAllMessServices();
    }
}

// Get user's current location
function getUserLocation() {
    if (navigator.geolocation) {
        locationButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Locating...';
        locationButton.disabled = true;

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };

                map.setCenter(userLocation);
                map.setZoom(15);

                if (userLocationMarker) {
                    userLocationMarker.setPosition(userLocation);
                } else {
                    userLocationMarker = new google.maps.Marker({
                        position: userLocation,
                        map: map,
                        title: "You Are Here",
                        icon: {
                            path: google.maps.SymbolPath.CIRCLE,
                            scale: 10,
                            fillColor: "#4285F4",
                            fillOpacity: 1,
                            strokeColor: "#FFFFFF",
                            strokeWeight: 2
                        },
                        zIndex: 1000
                    });
                    animateMarker(userLocationMarker);

                    const infoWindow = new google.maps.InfoWindow({
                        content: '<div style="font-weight: bold;">You Are Here</div>'
                    });
                    userLocationMarker.addListener("click", () => {
                        infoWindow.open(map, userLocationMarker);
                    });
                }

                calculateDistances(userLocation);
                locationButton.innerHTML = '<i class="fas fa-location-arrow"></i> You Are Here';
                locationButton.disabled = false;
            },
            (error) => {
                console.error("Error getting user location:", error);
                alert("Could not get your location. Please check your device settings and try again.");
                locationButton.innerHTML = '<i class="fas fa-location-arrow"></i> You Are Here';
                locationButton.disabled = false;
            },
            { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
        );
    } else {
        alert("Geolocation is not supported by this browser.");
    }
}

// Animate the user location marker
function animateMarker(marker) {
    let scale = 10;
    let growing = false;
    setInterval(() => {
        if (growing) {
            scale += 0.2;
            if (scale >= 12) growing = false;
        } else {
            scale -= 0.2;
            if (scale <= 8) growing = true;
        }
        marker.setIcon({
            path: google.maps.SymbolPath.CIRCLE,
            scale: scale,
            fillColor: "#4285F4",
            fillOpacity: 1,
            strokeColor: "#FFFFFF",
            strokeWeight: 2
        });
    }, 100);
}

// Calculate distances from user to markers
function calculateDistances(userLocation) {
    markers.forEach(marker => {
        const distance = google.maps.geometry.spherical.computeDistanceBetween(
            new google.maps.LatLng(userLocation),
            marker.getPosition()
        );
        const distanceKm = (distance / 1000).toFixed(1);
        const existingContent = marker.infoWindow.getContent();
        const newContent = existingContent.replace(
            '</div>',
            `<p><strong>Distance:</strong> ${distanceKm} km from you</p></div>`
        );
        marker.infoWindow.setContent(newContent);
    });
}

// Fetch all accommodations
function fetchAllAccommodations() {
    fetch("http://127.0.0.1:5000/search_accommodations?location=&type=all&budget=30000")
        .then(response => response.json())
        .then(data => displayAccommodationsOnMap(data))
        .catch(error => console.error("Error fetching initial accommodations:", error));
}

// Display accommodations on map
function displayAccommodationsOnMap(accommodations) {
    clearMarkers();
    if (directionsRenderer) directionsRenderer.setDirections({ routes: [] });
    if (!accommodations.length || !map) return;

    const bounds = new google.maps.LatLngBounds();

    accommodations.forEach(acc => {
        geocodeAddress(acc.location, (position) => {
            if (!position) return;

            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: acc.name,
                animation: google.maps.Animation.DROP
            });

            marker.propertyPosition = position;

            const infoContent = `
                <div class="info-window">
                    <h3>${acc.name}</h3>
                    <p><strong>Type:</strong> ${acc.type}</p>
                    <p><strong>Price:</strong> ₹${acc.rent_price}</p>
                    <p><strong>Location:</strong> ${acc.location}</p>
                    <div class="info-window-buttons">
                        <a href="view_accommodation.html?id=${acc.id}" class="map-link">View Details</a>
                        <button class="route-button" onclick="calculateRoute('${acc.location}')">
                            <i class="fas fa-route"></i> Route to Here
                        </button>
                    </div>
                </div>
            `;

            const infoWindow = new google.maps.InfoWindow({ content: infoContent });

            marker.addListener("click", () => {
                if (activeInfoWindow) activeInfoWindow.close();
                infoWindow.open(map, marker);
                activeInfoWindow = infoWindow;
            });

            marker.infoWindow = infoWindow;
            markers.push(marker);
            bounds.extend(position);

            if (markers.length > 1) {
                map.fitBounds(bounds);
            } else if (markers.length === 1) {
                map.setCenter(position);
                map.setZoom(15);
            }

            if (userLocationMarker) calculateDistances(userLocationMarker.getPosition());
        });
    });
}

// Fetch all mess services
function fetchAllMessServices() {
    fetch("http://127.0.0.1:5000/search_mess?location=&meal_type=both")
        .then(response => response.json())
        .then(data => {
            console.log("Fetched mess services:", data); // Debugging
            displayMessServicesOnMap(data);
        })
        .catch(error => console.error("Error fetching initial mess services:", error));
}

// Display mess services on map
function displayMessServicesOnMap(messServices) {
    clearMarkers();
    if (directionsRenderer) directionsRenderer.setDirections({ routes: [] });
    if (!messServices.length || !map) return;

    const bounds = new google.maps.LatLngBounds();

    messServices.forEach(mess => {
        geocodeAddress(mess.location, (position) => {
            if (!position) return;

            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: mess.name,
                animation: google.maps.Animation.DROP
            });

            marker.propertyPosition = position;

            const infoContent = `
                <div class="info-window mess-info-window">
                    <h3>${mess.name}</h3>
                    <p><strong>Meal Type:</strong> ${mess.meal_type}</p>
                    <p><strong>Price:</strong> ₹${mess.price}</p>
                    <p><strong>Location:</strong> ${mess.location}</p>
                    <div class="info-window-buttons">
                        <a href="view_mess.html?id=${mess.id}" class="map-link">View Details</a>
                        <button class="route-button" onclick="calculateRoute('${mess.location}')">
                            <i class="fas fa-route"></i> Route to Here
                        </button>
                    </div>
                </div>
            `;

            const infoWindow = new google.maps.InfoWindow({ content: infoContent });

            marker.addListener("click", () => {
                if (activeInfoWindow) activeInfoWindow.close();
                infoWindow.open(map, marker);
                activeInfoWindow = infoWindow;
            });

            marker.infoWindow = infoWindow;
            markers.push(marker);
            bounds.extend(position);

            if (markers.length > 1) {
                map.fitBounds(bounds);
            } else if (markers.length === 1) {
                map.setCenter(position);
                map.setZoom(15);
            }

            if (userLocationMarker) calculateDistances(userLocationMarker.getPosition());
        });
    });
}

// Calculate and display route
function calculateRoute(destination) {
    if (!userLocationMarker) {
        alert("Please click 'You Are Here' button first to get your location.");
        return;
    }

    const loadingDiv = document.createElement('div');
    loadingDiv.id = 'route-loading';
    loadingDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Calculating route...';
    document.body.appendChild(loadingDiv);

    const origin = userLocationMarker.getPosition();
    const routeTimeout = setTimeout(() => {
        const loadingElement = document.getElementById('route-loading');
        if (loadingElement) loadingElement.remove();
        alert("Route calculation timed out. Please try again later.");
    }, 10000);

    directionsService.route(
        {
            origin: origin,
            destination: destination,
            travelMode: google.maps.TravelMode.DRIVING,
            alternatives: true
        },
        (response, status) => {
            clearTimeout(routeTimeout);
            const loadingElement = document.getElementById('route-loading');
            if (loadingElement) loadingElement.remove();

            if (status === "OK") {
                directionsRenderer.setDirections(response);
                const route = response.routes[0];
                const duration = route.legs[0].duration.text;
                const distance = route.legs[0].distance.text;

                const routeInfoDiv = document.createElement('div');
                routeInfoDiv.id = 'route-info';
                routeInfoDiv.innerHTML = `
                    <div class="route-info-header">
                        <h3>Route Information</h3>
                        <button id="close-route-info"><i class="fas fa-times"></i></button>
                    </div>
                    <div class="route-info-content">
                        <p><i class="fas fa-clock"></i> <strong>Duration:</strong> ${duration}</p>
                        <p><i class="fas fa-road"></i> <strong>Distance:</strong> ${distance}</p>
                        <div class="travel-mode-selector">
                            <button class="travel-mode-btn active" data-mode="DRIVING">
                                <i class="fas fa-car"></i> Driving
                            </button>
                            <button class="travel-mode-btn" data-mode="WALKING">
                                <i class="fas fa-walking"></i> Walking
                            </button>
                            <button class="travel-mode-btn" data-mode="BICYCLING">
                                <i class="fas fa-bicycle"></i> Cycling
                            </button>
                            <button class="travel-mode-btn" data-mode="TRANSIT">
                                <i class="fas fa-bus"></i> Transit
                            </button>
                        </div>
                    </div>
                `;
                document.body.appendChild(routeInfoDiv);

                document.querySelectorAll('.travel-mode-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.travel-mode-btn').forEach(b => b.classList.remove('active'));
                        e.target.closest('.travel-mode-btn').classList.add('active');
                        const mode = e.target.closest('.travel-mode-btn').dataset.mode;
                        updateRoute(origin, destination, mode);
                    });
                });

                document.getElementById('close-route-info').addEventListener('click', () => {
                    document.getElementById('route-info').remove();
                    directionsRenderer.setDirections({ routes: [] });
                });
            } else {
                let errorMessage = "Could not calculate route";
                switch (status) {
                    case "ZERO_RESULTS": errorMessage = "No route found."; break;
                    case "OVER_QUERY_LIMIT": errorMessage = "Too many requests."; break;
                    case "REQUEST_DENIED": errorMessage = "Route calculation denied."; break;
                    case "INVALID_REQUEST": errorMessage = "Invalid request."; break;
                }

                const errorDiv = document.createElement('div');
                errorDiv.id = 'route-error';
                errorDiv.innerHTML = `
                    <div class="route-error-content">
                        <p><i class="fas fa-exclamation-triangle"></i> ${errorMessage}</p>
                        <button id="dismiss-error" class="btn">Dismiss</button>
                        <a href="https://www.google.com/maps/dir/?api=1&origin=${origin.lat()},${origin.lng()}&destination=${encodeURIComponent(destination)}" 
                           target="_blank" class="btn">Open in Google Maps</a>
                    </div>
                `;
                document.body.appendChild(errorDiv);

                document.getElementById('dismiss-error').addEventListener('click', () => {
                    document.getElementById('route-error').remove();
                });
                setTimeout(() => {
                    const errorElement = document.getElementById('route-error');
                    if (errorElement) errorElement.remove();
                }, 10000);
            }
        }
    );
}

// Update route with new travel mode
function updateRoute(origin, destination, travelMode) {
    document.querySelector('.route-info-content').innerHTML = '<p><i class="fas fa-spinner fa-spin"></i> Updating route...</p>';

    const updateTimeout = setTimeout(() => {
        document.querySelector('.route-info-content').innerHTML = `
            <p><i class="fas fa-exclamation-triangle"></i> Route update timed out.</p>
            <button id="try-again-btn" class="btn">Try Again</button>
        `;
        document.getElementById('try-again-btn').addEventListener('click', () => updateRoute(origin, destination, travelMode));
    }, 10000);

    directionsService.route(
        { origin, destination, travelMode: google.maps.TravelMode[travelMode] },
        (response, status) => {
            clearTimeout(updateTimeout);
            if (status === "OK") {
                directionsRenderer.setDirections(response);
                const route = response.routes[0];
                const duration = route.legs[0].duration.text;
                const distance = route.legs[0].distance.text;

                document.querySelector('.route-info-content').innerHTML = `
                    <p><i class="fas fa-clock"></i> <strong>Duration:</strong> ${duration}</p>
                    <p><i class="fas fa-road"></i> <strong>Distance:</strong> ${distance}</p>
                    <div class="travel-mode-selector">
                        <button class="travel-mode-btn ${travelMode === 'DRIVING' ? 'active' : ''}" data-mode="DRIVING">
                            <i class="fas fa-car"></i> Driving
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'WALKING' ? 'active' : ''}" data-mode="WALKING">
                            <i class="fas fa-walking"></i> Walking
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'BICYCLING' ? 'active' : ''}" data-mode="BICYCLING">
                            <i class="fas fa-bicycle"></i> Cycling
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'TRANSIT' ? 'active' : ''}" data-mode="TRANSIT">
                            <i class="fas fa-bus"></i> Transit
                        </button>
                    </div>
                `;

                document.querySelectorAll('.travel-mode-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.travel-mode-btn').forEach(b => b.classList.remove('active'));
                        e.target.closest('.travel-mode-btn').classList.add('active');
                        const mode = e.target.closest('.travel-mode-btn').dataset.mode;
                        updateRoute(origin, destination, mode);
                    });
                });
            } else {
                document.querySelector('.route-info-content').innerHTML = `
                    <p><i class="fas fa-exclamation-triangle"></i> Could not update route.</p>
                    <div class="travel-mode-selector">
                        <button class="travel-mode-btn ${travelMode === 'DRIVING' ? 'active' : ''}" data-mode="DRIVING">
                            <i class="fas fa-car"></i> Driving
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'WALKING' ? 'active' : ''}" data-mode="WALKING">
                            <i class="fas fa-walking"></i> Walking
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'BICYCLING' ? 'active' : ''}" data-mode="BICYCLING">
                            <i class="fas fa-bicycle"></i> Cycling
                        </button>
                        <button class="travel-mode-btn ${travelMode === 'TRANSIT' ? 'active' : ''}" data-mode="TRANSIT">
                            <i class="fas fa-bus"></i> Transit
                        </button>
                    </div>
                `;
                document.querySelectorAll('.travel-mode-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        document.querySelectorAll('.travel-mode-btn').forEach(b => b.classList.remove('active'));
                        e.target.closest('.travel-mode-btn').classList.add('active');
                        const mode = e.target.closest('.travel-mode-btn').dataset.mode;
                        updateRoute(origin, destination, mode);
                    });
                });
            }
        }
    );
}

// Geocode address to coordinates
function geocodeAddress(address, callback) {
    if (!address) {
        callback(null);
        return;
    }
    const geocoder = new google.maps.Geocoder();
    if (!address.toLowerCase().includes("pune")) {
        address += ", Pune, Maharashtra";
    }
    geocoder.geocode({ address }, (results, status) => {
        if (status === "OK" && results[0]) {
            callback(results[0].geometry.location);
        } else {
            console.warn(`Geocoding failed for address: ${address}. Status: ${status}`);
            callback(null);
        }
    });
}

// Clear all markers
function clearMarkers() {
    markers.forEach(marker => marker.setMap(null));
    markers = [];
}

// CSS for map and route features
document.addEventListener("DOMContentLoaded", function () {
    const style = document.createElement('style');
    style.textContent = `
        .custom-map-control {
            background-color: #fff;
            border: none;
            border-radius: 2px;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
            margin: 10px;
            padding: 8px 16px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: background-color 0.3s;
        }
        .custom-map-control:hover { background-color: #f1f1f1; }
        .custom-map-control i { margin-right: 8px; color: #4285F4; }
        .custom-map-control:disabled { cursor: not-allowed; opacity: 0.7; }
        .info-window-buttons { display: flex; gap: 8px; margin-top: 8px; }
        .route-button {
            background-color: #34A853;
            color: white;
            border: none;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            display: flex;
            align-items: center;
            gap: 4px;
        }
        .route-button:hover { background-color: #2E8B57; }
        #route-loading {
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #route-info {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            width: 300px;
            z-index: 100;
        }
        .route-info-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 15px;
            border-bottom: 1px solid #eee;
        }
        .route-info-header h3 { margin: 0; font-size: 16px; color: #333; }
        #close-route-info { background: none; border: none; font-size: 16px; cursor: pointer; color: #777; }
        #close-route-info:hover { color: #333; }
        .route-info-content { padding: 15px; }
        .route-info-content p { margin: 8px 0; display: flex; align-items: center; gap: 8px; }
        .travel-mode-selector { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 15px; }
        .travel-mode-btn {
            background-color: #f1f1f1;
            border: none;
            padding: 8px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            transition: all 0.2s ease;
        }
        .travel-mode-btn:hover { background-color: #e0e0e0; }
        .travel-mode-btn.active { background-color: #4285F4; color: white; }
        #route-error {
            position: fixed;
            bottom: 20px;
            left: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
            width: 300px;
            z-index: 100;
            padding: 15px;
        }
        .route-error-content { display: flex; flex-direction: column; gap: 10px; }
        .route-error-content p { margin: 0; color: #d32f2f; display: flex; align-items: center; gap: 8px; }
    `;
    document.head.appendChild(style);
});

// Handle Accommodation Search
document.addEventListener("DOMContentLoaded", function () {
    const accommodationSearchForm = document.querySelector("#accommodation-search-form");
    const accommodationResultsSection = document.querySelector("#search-results");

    if (accommodationSearchForm) {
        accommodationSearchForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const locationKeyword = document.querySelector("#location").value.trim();
            let propertyType = document.querySelector("#property-type").value;
            const maxBudget = document.querySelector("#max-budget").value;

            if (propertyType === "") propertyType = "all";

            fetch(`http://127.0.0.1:5000/search_accommodations?location=${locationKeyword}&type=${propertyType}&budget=${maxBudget}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    displayAccommodationsOnMap(data);
                    accommodationResultsSection.innerHTML = "";

                    if (data.length === 0) {
                        accommodationResultsSection.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(acc => {
                            let imageUrl = acc.image_url.startsWith("http") ? acc.image_url : `http://127.0.0.1:5000${acc.image_url}`;
                            const listing = `
                                <div class="box fade-in">
                                    <div class="thumb">
                                        <img src="${imageUrl}" alt="${acc.name}" style="width:250px; height:auto; border-radius:5px;">
                                    </div>
                                    <h3 class="name">${acc.name}</h3>
                                    <p class="location"><i class="fas fa-map-marker-alt"></i> ${acc.location}</p>
                                    <p class="type">Type: ${acc.type}</p>

                                    <a href="view_accommodation.html?id=${acc.id}" class="btn">View Details</a>
                                </div>
                            `;
                            accommodationResultsSection.innerHTML += listing;
                        });
                    }
                    accommodationResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                })
                .catch(error => {
                    console.error("Error fetching accommodation search results:", error);
                    accommodationResultsSection.innerHTML = "<p>Something went wrong. Please try again.</p>";
                });
        });
    }
});

// Handle Mess Service Search
document.addEventListener("DOMContentLoaded", function () {
    const messSearchForm = document.querySelector("#mess-search-form");
    const messResultsSection = document.querySelector("#mess-search-results");

    if (messSearchForm) {
        messSearchForm.addEventListener("submit", function (event) {
            event.preventDefault();
            const locationKeyword = document.querySelector("#mess-location").value.trim();
            const mealType = document.querySelector("#meal-type").value;
            const maxBudget = document.querySelector("#mess-budget").value;

            fetch(`http://127.0.0.1:5000/search_mess?location=${locationKeyword}&meal_type=${mealType}&budget=${maxBudget}`)
                .then(response => {
                    if (!response.ok) throw new Error("Network response was not ok");
                    return response.json();
                })
                .then(data => {
                    displayMessServicesOnMap(data);
                    messResultsSection.innerHTML = "";

                    if (data.length === 0) {
                        messResultsSection.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(mess => {
                            const listing = `
                                <div class="box fade-in">
                                    <div class="thumb">
                                        <img src="http://127.0.0.1:5000/${mess.image_url}" alt="${mess.name}">
                                    </div>
                                    <h3 class="name">${mess.name}</h3>
                                    <p class="location"><i class="fas fa-map-marker-alt"></i> ${mess.location}</p>
                                    <p class="meal-type">Meal Type: ${mess.meal_type}</p>
                                    <p class="price">Price: ₹${mess.price}</p>
                                    <p class="description">${mess.description}</p>
                                    <a href="view_mess.html?id=${mess.id}" class="btn">View Details</a>
                                </div>
                            `;
                            messResultsSection.innerHTML += listing;
                        });
                    }
                    messResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                })
                .catch(error => {
                    console.error("Error fetching mess search results:", error);
                    messResultsSection.innerHTML = "<p>Something went wrong. Please try again.</p>";
                });
        });
    }
});
// Handle mobile menu toggle
document.addEventListener("DOMContentLoaded", function () {
    const menuBtn = document.getElementById("menu-btn");
    const navList = document.querySelector(".header .navbar .flex > ul");
 
    if (menuBtn && navList) {
       menuBtn.addEventListener("click", () => {
          navList.classList.toggle("active");
       });
    }
 });
 