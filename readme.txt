!!! Make sure you have Docker Desktop running first !!!


--- Input these into CMD ---
docker build -t music-bot .
docker run -d --name musicbot -e DISCORD_BOT_TOKEN="PUT_BOT_KEY_HERE" music-bot