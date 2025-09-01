CREATE TABLE authors (
    id UUID PRIMARY KEY,
    name VARCHAR NOT NULL
);

CREATE INDEX ix_authors_id ON authors (id);
CREATE UNIQUE INDEX ix_authors_name ON authors (name);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(150) NOT NULL,
    password_hash VARCHAR NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE UNIQUE INDEX ix_users_username ON users (username);

DO $$ BEGIN
    CREATE TYPE genreenum AS ENUM (
        'Fiction',
        'Non-Fiction',
        'Science',
        'History',
        'Biography',
        'Fantasy',
        'Mystery',
        'Thriller',
        'Romance',
        'Science Fiction'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

CREATE TABLE books (
    id UUID PRIMARY KEY,
    title VARCHAR NOT NULL,
    published_year INT NOT NULL,
    author_id UUID REFERENCES authors (id),
    genres genreenum[] NOT NULL
);

CREATE INDEX ix_books_id ON books (id);

CREATE TABLE refresh_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    token VARCHAR NOT NULL,
    expires_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX ix_refresh_tokens_token ON refresh_tokens (token);
CREATE INDEX ix_refresh_tokens_user_id ON refresh_tokens (user_id);
