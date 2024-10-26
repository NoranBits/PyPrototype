-- Table to store basic details about each bill
CREATE TABLE bills (
    id SERIAL PRIMARY KEY,
    bill_number VARCHAR(10) NOT NULL, 
    parliament_number INTEGER NOT NULL, 
    session_number INTEGER NOT NULL, 
    title VARCHAR(255) NOT NULL, 
    bill_type VARCHAR(255), 
    status VARCHAR(100),
    introduced_date DATE,
    royal_assent_date DATE,
    full_text_link TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Automatically records the last update timestamp
);
-- Table to store detailed sections of each bill (e.g., clauses, articles)
CREATE TABLE bill_text (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id),
    section_number VARCHAR(50),
    section_title VARCHAR(255),
    section_text TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Table to store sponsor details for each bill
CREATE TABLE sponsors (
    id SERIAL PRIMARY KEY,
    title VARCHAR(50),                        
    first_name VARCHAR(100),                  
    last_name VARCHAR(100),                   
    honorifics VARCHAR(50),                  
    province VARCHAR(100),                    
    affiliation VARCHAR(100),                
    telephone VARCHAR(50),                    
    email VARCHAR(255),                       
    staff TEXT,                               
    personal_website TEXT,                    
    biography TEXT,                          
    bill_id INTEGER REFERENCES bills(id),     
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP 

-- Table to store voting details for each bill
CREATE TABLE voting (
    id SERIAL PRIMARY KEY,
    bill_id INTEGER REFERENCES bills(id), 
    total_yeas INTEGER, 
    total_nays INTEGER, 
    total_abstain INTEGER, 
    total_paired INTEGER, 
    vote_date DATE,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Relationship table linking bills to sponsors
CREATE TABLE bill_sponsors (
    bill_id INTEGER REFERENCES bills(id),
    sponsor_id INTEGER REFERENCES sponsors(id),
    PRIMARY KEY (bill_id, sponsor_id),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);