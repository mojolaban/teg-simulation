-- SQLite doesn’t support CREATE DATABASE; the database file is created implicitly when tables are made
-- Remove MySQL-specific comments and settings

-- Table: compensation
DROP TABLE IF EXISTS compensation;
CREATE TABLE compensation (
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    comp_amt INTEGER DEFAULT NULL,
    comp_rgainfinal INTEGER DEFAULT NULL,
    comp_round INTEGER DEFAULT NULL,
    num INTEGER PRIMARY KEY AUTOINCREMENT,
    id VARCHAR(2) DEFAULT NULL,
    gr VARCHAR(1) DEFAULT NULL,
    lang TINYINT DEFAULT NULL
);

-- Table: demog
DROP TABLE IF EXISTS demog;
CREATE TABLE demog (
    ts TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    id VARCHAR(2) DEFAULT NULL,
    gender VARCHAR(20) DEFAULT NULL,
    age SMALLINT DEFAULT NULL,
    education_level VARCHAR(20) DEFAULT NULL,
    current_education VARCHAR(20) DEFAULT NULL,
    country_residence VARCHAR(10) DEFAULT NULL,
    citizenship VARCHAR(10) DEFAULT NULL,
    asset_experience VARCHAR(40) DEFAULT NULL,
    tax_experience VARCHAR(20) DEFAULT NULL,
    description VARCHAR(10) DEFAULT NULL,
    PRIMARY KEY (ts)
);

-- Table: log
DROP TABLE IF EXISTS log;
CREATE TABLE log (
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    counter TINYINT DEFAULT NULL,
    num INTEGER PRIMARY KEY AUTOINCREMENT,
    id VARCHAR(2) DEFAULT NULL,
    gr VARCHAR(1) DEFAULT NULL,
    lang TINYINT DEFAULT NULL,
    au TINYINT DEFAULT NULL
);

-- Table: responses
DROP TABLE IF EXISTS responses;
CREATE TABLE responses (
    gr VARCHAR(1) DEFAULT NULL,
    id VARCHAR(2) DEFAULT NULL,
    lang TINYINT DEFAULT NULL,
    ts DATETIME DEFAULT CURRENT_TIMESTAMP,
    round INTEGER DEFAULT NULL,
    trx INTEGER DEFAULT NULL,
    sec INTEGER DEFAULT NULL,
    pos VARCHAR(1) DEFAULT NULL,
    activity TEXT GENERATED ALWAYS AS (
        CASE pos
            WHEN 's' THEN 'buying'
            WHEN 'b' THEN 'selling'
        END
    ) STORED,
    price INTEGER DEFAULT NULL,
    crypto DECIMAL(5,2) DEFAULT NULL,
    fiat INTEGER DEFAULT NULL,
    crypto_prev DECIMAL(5,2) DEFAULT NULL,
    fiat_prev INTEGER DEFAULT NULL,
    sell INTEGER DEFAULT NULL,
    buy INTEGER DEFAULT NULL,
    buy_prev INTEGER DEFAULT NULL,
    t_gain INTEGER DEFAULT NULL,
    t_tax INTEGER DEFAULT NULL,
    t_gain_net INTEGER DEFAULT NULL,
    r_gain INTEGER DEFAULT NULL,
    r_gain_prev INTEGER DEFAULT NULL,
    r_tax INTEGER DEFAULT NULL,
    r_tax_prev INTEGER DEFAULT NULL,
    r_gain_net INTEGER DEFAULT NULL,
    tax_disclos INTEGER DEFAULT NULL,
    tax_discre INTEGER GENERATED ALWAYS AS (COALESCE(r_tax, 0) - COALESCE(tax_disclos, 0)) STORED,
    audit INTEGER DEFAULT NULL,
    penalty INTEGER GENERATED ALWAYS AS (
        CASE WHEN (audit = 1 AND tax_discre >= 0) THEN COALESCE(tax_discre, 0) * 2 ELSE 0 END
    ) STORED,
    r_gain_final INTEGER GENERATED ALWAYS AS (
        CASE WHEN audit = 1
            THEN (COALESCE(r_gain, 0) - COALESCE(tax_disclos, 0) - COALESCE(tax_discre, 0) - COALESCE(penalty, 0))
            ELSE (COALESCE(r_gain, 0) - COALESCE(tax_disclos, 0))
        END
    ) STORED,
    num INTEGER PRIMARY KEY AUTOINCREMENT
);

-- Table: survey
DROP TABLE IF EXISTS survey;
CREATE TABLE survey (
    ts DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    question0 INTEGER DEFAULT NULL,
    question1 INTEGER DEFAULT NULL,
    question2 INTEGER DEFAULT NULL,
    question3 INTEGER DEFAULT NULL,
    question4 INTEGER DEFAULT NULL,
    question5 INTEGER DEFAULT NULL,
    question6 INTEGER DEFAULT NULL,
    question7 INTEGER DEFAULT NULL,
    question8 INTEGER DEFAULT NULL,
    question9 INTEGER DEFAULT NULL,
    question10 INTEGER DEFAULT NULL,
    question11 INTEGER DEFAULT NULL,
    question12 INTEGER DEFAULT NULL,
    question13 INTEGER DEFAULT NULL,
    question14 INTEGER DEFAULT NULL,
    question15 INTEGER DEFAULT NULL,
    question16 INTEGER DEFAULT NULL,
    question17 INTEGER DEFAULT NULL,
    question18 INTEGER DEFAULT NULL,
    question19 INTEGER DEFAULT NULL,
    question20 INTEGER DEFAULT NULL,
    question21 INTEGER DEFAULT NULL,
    question22 INTEGER DEFAULT NULL,
    question23 INTEGER DEFAULT NULL,
    question24 INTEGER DEFAULT NULL,
    question25 INTEGER DEFAULT NULL,
    question26 INTEGER DEFAULT NULL,
    question27 INTEGER DEFAULT NULL,
    question28 INTEGER DEFAULT NULL,
    question29 INTEGER DEFAULT NULL,
    question30 INTEGER DEFAULT NULL,
    question31 INTEGER DEFAULT NULL,
    question32 INTEGER DEFAULT NULL,
    question33 INTEGER DEFAULT NULL,
    question34 INTEGER DEFAULT NULL,
    question35 INTEGER DEFAULT NULL,
    question36 INTEGER DEFAULT NULL,
    email VARCHAR(100) DEFAULT NULL,
    gr INTEGER DEFAULT NULL,
    id VARCHAR(2) DEFAULT NULL,
    comments VARCHAR(10000) DEFAULT NULL,
    followup TEXT CHECK(followup IN ('Yes', 'No')) NOT NULL,
    lang TINYINT DEFAULT NULL,
    veteran TEXT CHECK(veteran IN ('Yes', 'No')) DEFAULT NULL,
    cryptorisk TEXT,
    trustpower TEXT,
    comments_a TEXT,
    comments_b TEXT,
    PRIMARY KEY (ts)
);