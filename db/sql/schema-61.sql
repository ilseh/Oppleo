-- Add UNIQUE constraint to username table
ALTER TABLE users ADD UNIQUE (username);

-- Add WebAuthN Credentials table
CREATE TABLE webauthn_credentials (

    credential_owner VARCHAR NOT NULL,
    credential_id VARCHAR(256) NOT NULL,
    credential_name VARCHAR(100),
    aaguid VARCHAR(100),
    credential_backed_up BOOLEAN,
    credential_device_type VARCHAR(100),
    credential_public_key VARCHAR(256),
    credential_type VARCHAR(100),
    fmt VARCHAR(100),
    sign_count INT,
    user_verified BOOLEAN DEFAULT false,

    created_at TIMESTAMP DEFAULT NOW(),
    modified_at TIMESTAMP DEFAULT NOW(),

    UNIQUE (credential_id, credential_public_key)
);

-- Add WebAuthN unique random user id to Users table
ALTER TABLE users ADD web_auth_user_id VARCHAR(100);