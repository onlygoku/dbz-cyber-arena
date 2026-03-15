-- Docker Compose local development bootstrap
-- Creates the database and user if they don't exist.
-- In production (Render.com) the DATABASE_URL env var is used directly.

CREATE USER ctf WITH PASSWORD 'ctf';
CREATE DATABASE ctfdb OWNER ctf;
GRANT ALL PRIVILEGES ON DATABASE ctfdb TO ctf;
