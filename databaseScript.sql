CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password TEXT NOT NULL
);

-- Create Admin table
CREATE TABLE admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

-- Create Accommodations table
CREATE TABLE accommodations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    rent_price INTEGER NOT NULL,
    deposit_amount INTEGER,
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
    listing_date DATE,
    availability_status BOOLEAN,
    property_age INTEGER,
    parking_available BOOLEAN
);

-- Create Mess Service table
CREATE TABLE mess_service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    meal_type VARCHAR(50) NOT NULL,
    price INTEGER NOT NULL,
    description TEXT,
    image_url TEXT,
    owner_name VARCHAR(100),
    phone_number VARCHAR(20),
    timings VARCHAR(100),
    menu TEXT,
    amenities TEXT,
    listing_date DATE
);

-- Create Saved Listing table with foreign key constraints
CREATE TABLE saved_listing (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    accommodation_id INTEGER,
    mess_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (accommodation_id) REFERENCES accommodations(id) ON DELETE CASCADE,
    FOREIGN KEY (mess_id) REFERENCES mess_service(id) ON DELETE CASCADE
);

