document.addEventListener("DOMContentLoaded", function () {
    const userId = localStorage.getItem("user_id");
    const userInfo = document.querySelector("#user-info"); 
    const logoutBtn = document.querySelector("#logout-btn");

    // ✅ Fetch user details if logged in
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

    // ✅ Handle Login
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

    // ✅ Logout functionality (should work on all pages)
    if (logoutBtn) {
        logoutBtn.addEventListener("click", function (event) {
            event.preventDefault();
            localStorage.removeItem("user_id"); // Clear session
            alert("Logged out successfully!");
            window.location.href = "login.html"; // Redirect to login
        });
    }
});

document.addEventListener("DOMContentLoaded", function () {
    const accommodationSearchForm = document.querySelector("#accommodation-search-form");
    const accommodationResultsSection = document.querySelector("#search-results");

    if (accommodationSearchForm) {
        accommodationSearchForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const locationKeyword = document.querySelector("#location").value.trim();
            let propertyType = document.querySelector("#property-type").value;
            const maxBudget = document.querySelector("#max-budget").value;

            // ✅ Set "all" if user selects "Any Type"
            if (propertyType === "") {
                propertyType = "all";
            }

            fetch(`http://127.0.0.1:5000/search_accommodations?location=${locationKeyword}&type=${propertyType}&budget=${maxBudget}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error("Network response was not ok");
                    }
                    return response.json();
                })
                .then(data => {
                    accommodationResultsSection.innerHTML = ""; 

                    if (data.length === 0) {
                        accommodationResultsSection.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(acc => {
                            const listing = `
                                <div class="box fade-in">
                                    <div class="thumb">
                                        <img src="${acc.image_url}" alt="${acc.name}">
                                    </div>
                                    <h3 class="name">${acc.name}</h3>
                                    <p class="location"><i class="fas fa-map-marker-alt"></i> ${acc.location}</p>  
                                    <p class="type">Type: ${acc.type}</p>
                                    <p class="price">Price: ₹${acc.price}</p>
                                    <p class="description">${acc.description}</p>
                                    <a href="view_property.html" class="btn">View Details</a>
                                </div>
                            `;
                            accommodationResultsSection.innerHTML += listing;
                        });
                    }

                    // ✅ Auto-scroll to search results
                    accommodationResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                })
                .catch(error => {
                    console.error("Error fetching accommodation search results:", error);
                    accommodationResultsSection.innerHTML = "<p>Something went wrong. Please try again.</p>";
                });
        });
    }
});


document.addEventListener("DOMContentLoaded", function () {
    const messSearchForm = document.querySelector("#mess-search-form");
    const messResultsSection = document.querySelector("#mess-search-results");

    if (messSearchForm) {
        messSearchForm.addEventListener("submit", function (event) {
            event.preventDefault();

            const locationKeyword = document.querySelector("#mess-location").value.trim();  // ✅ Allows keyword search
            const mealType = document.querySelector("#meal-type").value; 
            const maxBudget = document.querySelector("#mess-budget").value;

            fetch(`http://127.0.0.1:5000/search_mess?location=${locationKeyword}&meal_type=${mealType}&budget=${maxBudget}`)
                .then(response => response.json())
                .then(data => {
                    messResultsSection.innerHTML = ""; 

                    if (data.length === 0) {
                        messResultsSection.innerHTML = "<p>No results found.</p>";
                    } else {
                        data.forEach(mess => {
                            const listing = `
                                <div class="box fade-in">
                                    <div class="thumb">
                                        <img src="${mess.image_url}" alt="${mess.name}">
                                    </div>
                                    <h3 class="name">${mess.name}</h3>
                                    <p class="location"><i class="fas fa-map-marker-alt"></i> ${mess.location}</p>  <!-- ✅ Shows full address -->
                                    <p class="meal-type">Meal Type: ${mess.meal_type}</p>
                                    <p class="price">Price: ₹${mess.price}</p>
                                    <p class="description">${mess.description}</p>
                                    <a href="view_property.html" class="btn">View Details</a>
                                </div>
                            `;
                            messResultsSection.innerHTML += listing;
                        });
                    }

                    // ✅ Auto-scroll to search results
                    messResultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
                })
                .catch(error => console.error("Error fetching mess search results:", error));
        });
    }
});




