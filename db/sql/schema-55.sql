-- Store json values by key string, used for teslapy cache

CREATE TABLE keyvaluestores (
    kvstore VARCHAR(256) NOT NULL,
    scope VARCHAR(256) NOT NULL,
    key VARCHAR(256) NOT NULL,
    value JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    modified_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (kvstore, scope, key)
);
