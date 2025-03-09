CREATE TABLE accommodations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    rent_price INTEGER NOT NULL,
    deposit_amount INTEGER NOT NULL,
    description TEXT,
    image_url TEXT,
    owner_name VARCHAR(100),
    phone_number VARCHAR(20),
    bedrooms INTEGER,
    bathrooms INTEGER,
    balconies INTEGER,
    furnished_status VARCHAR(50),
    carpet_area INTEGER,
    amenities TEXT,
    listing_date DATE DEFAULT CURRENT_DATE,
    availability_status BOOLEAN DEFAULT TRUE,
    property_age INTEGER,
    parking_available BOOLEAN DEFAULT FALSE
);


CREATE TABLE mess_service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL,  -- Monthly Price
    description TEXT,
    image_url TEXT,
    owner_name VARCHAR(100),
    phone_number VARCHAR(20),
    timings VARCHAR(100),
    menu TEXT,
    amenities TEXT,
    listing_date DATE DEFAULT CURRENT_DATE
);


CREATE TABLE saved_listing (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    accommodation_id INTEGER REFERENCES accommodations(id) ON DELETE CASCADE,
    mess_id INTEGER REFERENCES mess_service(id) ON DELETE CASCADE
);


