# Introduction
🎉 **Welcome to Fluctlight! Your Gateway to Intelligent Chat Agents** 🎉

Unleash the power of dynamic communication with Fluctlight, the ultimate framework designed for crafting task-based chat agents. Seamlessly configure and deploy your agents across leading platforms like Discord, Slack, and the web with ease.

🚀 **Why Choose Fluctlight?** 🚀

- 🌐 **Cross-Platform Deployment**: Effortlessly reach users on Discord, Slack, or any web interface.
- 🧠 **Advanced Capabilities**:
  - **RAG Retrieval**: Harness the potential of cutting-edge retrieval-augmented generation.
  - **Intent Detection**: Ensure every interaction is contextually relevant.
  - **Speech & Image Understanding**: Elevate your agent's capabilities by integrating speech recognition and image comprehension.

Transform your interaction experiences with Fluctlight, where innovation meets simplicity and versatility. Get started today and redefine what's possible!

## Spotlights



## Setup

Rename env.template to .env and fill in the required APIKEY there.

Make that, simple run command `docker compose up app`

### Requirements env.
We use [Docker](https://www.docker.com) to run the application.

We recommand asdf to manage your local dev env if you're on a MacOS.

## Development



## Deployment

Botchan is fully functional and running on your local dev machine or laptop.
If you are looking at optional to turn it into a 24/7 online bot here are some suggestions.

  - Deploying the application in a cloud Kubernetes environment is recommended since it is already containerized.
  - Deploy on serverless env like Heroku.



## Developer guide

### Tooling

Command make will list all the tasks.

```
===== All tasks =====
app                            start app server
app-debug                      start app server with debug mode
test                           Test.PHONY:
docker-compose-build           Build the app
docker-compose-up              Run app with rebuild
docker-compose-bash            Connect to a bash within the docker image
docker-test                    Run unit test
docker-test-int                Run intergation test
requirements.txt               Export requirements.txt from pyproject.toml
requirements-dev.txt           Export requirements-dev.txt from pyproject.toml
```

### Discord Bot Setup

[Discord Bot Setup Guide](https://discordpy.readthedocs.io/en/stable/discord.html)

### Slack Bot Setup

[Slack Bot Setup Tutorial](https://api.slack.com/tutorials/tracks/create-bot-to-welcome-users)

## Security and privacy reminder.
- It is essential to be aware that if you need to log chat messages, the author suggests only doing so when the debug flag is on. 
- The repository is not designed to be secure for production use, so use it at your own risk.
