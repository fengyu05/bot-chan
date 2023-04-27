# Introduction
Welcome to Bot-chan! This is a minimal but fully functional framework for a Slack AI Chatbot that is easy setup and customize.
The author made Botchan open source in order to help those who are interested in creating their own chatbot application but don't know where to begin.

## Spotlights

As a Slack Chatbot application, Botchan has the following features.

- Reposonse to IM(direct message) or `@` mentioned in public channels.
- Engage in interactive conversions.
- Per thread(slack dicussion thread) memory.
- Customzied bot personality(via preconfig prompt).

<code><table>
  <tr>
    <td>Chat with the Botchan</td>
    <td>Help summary messages or posts in place</td>
    <td>Help writing code</td>
  </tr>
  <tr>
    <td><img width="300" alt="Screenshot 2023-04-27 at 11 46 44 AM" src="https://user-images.githubusercontent.com/7340368/234968563-9828a47e-6c06-4ce0-a33a-f02eb7405891.png"></td>
    <td><img width="300" alt="Screenshot 2023-04-27 at 11 51 34 AM" src="https://user-images.githubusercontent.com/7340368/234968587-f976e3ff-b208-4cc8-b121-fb1e584c5e32.png"></td>
    <td><img width="300" alt="Screenshot 2023-04-27 at 11 58 07 AM" src="https://user-images.githubusercontent.com/7340368/234968622-c4e8df1d-4c88-4ee4-b63b-a9411ea05cb1.png"></td>

 </tr>
</table></code>


## Setup

Bot-chan requires three tokens to function properly, which can be added to the `env.dev` file.
Please rename the `env.dev.template` file as `env.dev` and insert the required tokens.

To obtain the necessary Slack tokens, please follow the instructions provided in the [setup_slack_app.md](./setup_slack_app.md) guide.
For OpenAI API Token, simply generate a token on their developer page.

### Requirements env.
We use [Docker](https://www.docker.com) to run the application.

But if you prefer, you may choose to install requirements without Docker. Bot-chan utilizes `python3.9` and `poetry 1.2+`. You can install these dependencies using any preferred method, but we recommend the virtual env management tool [ASDF](https://asdf-vm.com/).

## Development

To start developing with Bot-chan, run the command `docker-compose up --build -d`. Logs can be reviewed with `docker-compose logs`.

## Customization

Want to customize your chatbot? Bot-chan offers flexibility to tailor it to your specific needs.

## Security and privicay reminder.

- Botchan does not store any information from Slack, but instead uses the Slack History API to read messages.
- It is important to be aware that if you need to log any chat messages, the author suggests only doing so when the debug flag is on. 
- The repository is not designed to be secure for production use, so use it at your own risk.








