-- Drop existing tables if they exist
DROP TABLE IF EXISTS bill_votes;
DROP TABLE IF EXISTS bill_details;
DROP TABLE IF EXISTS bills;

-- create the bills table
CREATE TABLE bills (
    bill_id SERIAL PRIMARY KEY,
    bill_number VARCHAR(50) NOT NULL,
    parliament_number INTEGER NOT NULL,
    session_number INTEGER NOT NULL,
    bill_stage VARCHAR(255),
    bill_stage_date TIMESTAMP,
    sponsor_id INTEGER,
    sponsor_name VARCHAR(255),
    sponsor_role VARCHAR(255),
    UNIQUE(bill_number, parliament_number, session_number)
);
-- create the bill_details table
CREATE TABLE bill_details (
    detail_id SERIAL PRIMARY KEY,
    bill_number VARCHAR(50) NOT NULL,
    parliament_number INTEGER NOT NULL,
    session_number INTEGER NOT NULL,
    title VARCHAR(255),
    short_title VARCHAR(255),
    sponsor VARCHAR(255),
    bill_ref_number VARCHAR(50),
    bill_history TEXT,
    introduction TEXT,
    body TEXT,
    FOREIGN KEY (bill_number, parliament_number, session_number) 
        REFERENCES bills (bill_number, parliament_number, session_number)
        ON DELETE CASCADE
);

-- create the bill_votes table
CREATE TABLE bill_votes (
    vote_id SERIAL PRIMARY KEY,
    parliament_number INTEGER NOT NULL,
    session_number INTEGER NOT NULL,
    description TEXT,
    decision VARCHAR(50),
    bill_number VARCHAR(50),
    total_yeas INTEGER,
    total_nays INTEGER,
    total_abstain INTEGER,
    vote_date DATE,
    division_number VARCHAR(50),
    FOREIGN KEY (bill_number, parliament_number, session_number) 
        REFERENCES bills (bill_number, parliament_number, session_number)
        ON DELETE CASCADE
);

-- Create indexes to optimize queries
CREATE INDEX idx_bill_number_parliament_session ON bills (bill_number, parliament_number, session_number);
CREATE INDEX idx_vote_parliament_session ON bill_votes (parliament_number, session_number);
