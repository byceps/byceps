#!/bin/sh -ex

# Create configuration file.
cp docker/byceps/config.toml.example docker/byceps/config.toml

# Create services.
docker compose up --no-start --quiet-pull

# Generate secret key.
docker compose run --rm byceps-apps uv run byceps generate-secret-key > ./secret_key.txt

# Insert secret key into configuration file.
sed -i '/secret_key = ""/s|^.*|secret_key = "fake-secret-key-for-testing"|' docker/byceps/config.toml

# Initialize database.
docker compose run --rm byceps-apps uv run byceps initialize-database
