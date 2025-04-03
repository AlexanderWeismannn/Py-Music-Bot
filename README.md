# 🎶 Discord Music Bot

A fully-featured Discord music bot written in Python, powered by `discord.py`, `yt-dlp`, and `FFmpeg`.  
Stream YouTube audio into voice channels, search songs, manage queues — and deploy it anywhere via Docker. 🐳

---

## ✨ Features

- 🎧 Join & leave voice channels
- 🔍 `!search` to find YouTube music via keywords or Spotify links (converted to YouTube)
- ▶️ `!play` to queue and stream songs
- ⏸ `!pause`, ⏯ `!resume`, `!skip`, `!prev` ❌ `!leave` commands
- 📄 `!queue` to show current and upcoming tracks
- ✅ Auto disconnect when alone
- 🐳 Easy deployment with Docker

| Command     | Aliases            | Description                                               |
|-------------|--------------------|-----------------------------------------------------------|
| `!join`     | `!j`, `!ahoy`       | Bot joins your voice channel                              |
| `!play`     | `!p`, `!Play`       | Plays a song from queue or resumes paused playback        |
| `!search`   | `!s`, `!sr`         | Search YouTube and select from a result dropdown          |
| `!pause`    | `!ps`, `!stop`      | Pause current playback                                    |
| `!resume`   | `!res`, `!r`        | Resume paused playback                                    |
| `!queue`    | `!q`, `!list`       | Show currently playing and queued songs                   |
| `!skip`     | `!next`, `!n`       | Skip the current song and play the next one in queue      |
| `!prev`     | `!back`, `!b`       | Go back to the previous song (if available)               |
| `!leave`    | `!l`, `!byebye`     | Disconnect the bot from the voice channel                 |

  

---

## 📦 Requirements

- Python 3.11+
- `ffmpeg`
- `PyNaCl`
- `yt-dlp`
- A Discord bot token from [Discord Developer Portal](https://discord.com/developers/applications)

---

## 🧰 Installation (Local Dev)

```bash
git clone https://github.com/AlexanderWeismannn/Py-Music-Bot.git
cd music-bot
pip install -r requirements.txt
```
---

## 🐳 Docker Deployment

You can run this music bot instantly using Docker — no Python or dependencies required.

1. **Download the Docker image**  
   - 📦 [Download `music-bot.tar`](https://drive.google.com/file/d/1jgF9hzq6ncgZ43pAz_eVbyAlk6SotngX/view?usp=sharing)
   - Invite Bot [Invite Link](https://discord.com/channels/277870655297552384/697482599081312366/1357240101675208876)
   - - A create Bot Token [Discord Developer Portal](https://discord.com/developers/applications)
   

3. **Load the image into Docker**:
   ```bash
   docker load -i music-bot.tar

4. ***Run the Bot with Discord Token*
  ```bash
  docker run -d --name musicbot -e DISCORD_BOT_TOKEN=your_token_here music-bot
```
