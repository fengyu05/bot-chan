# Introduction
Welcome to Bot-chan! This is a minimal framework for a Slack AI Chatbot that provides easy setup instructions and customization options.

## Spotlights

## Setup

Bot-chan requires three tokens to function properly, which can be added to the `env.dev` file.
Please rename the `env.dev.template` file as `env.dev` and insert the required tokens.

To obtain the necessary Slack tokens, please follow the instructions provided in the [setup_slack_app.md](./setup_slack_app.md) guide.
For OpenAI API Token, simply generate a token on their developer page.

### Requirements env.
We use [Docker](https://www.docker.com) to run the application.

But if you prefer, you may choose to install requirements without Docker. Bot-chan utilizes `python3.9` and `poetry 1.2+`. You can install these dependencies using any preferred method, but we recommend the virtual env management tool [ASDF](https://asdf-vm.com/).

## Development

To start developing with Bot-chan, run the command `docker-compose up -d`. Logs can be reviewed with `docker-compose logs`.

## Customization

Want to customize your chatbot? Bot-chan offers flexibility to tailor it to your specific needs.

Thank you.







