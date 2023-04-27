# Introduction
Welcome to Bot-chan! This is a minimal but fully functional framework for a Slack AI Chatbot that is easy setup and customize.

We made Botchan open source to help those who want to create their own chatbot application but don't know where to start. You can use Botchan as a personal chatbot on your Slack workspace, or develop it into a product or something even bigger.

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

## Productionize

Botchan is fully functional running on your local dev machine or laptop.
If you are looking at optional to turn it into a 24/7 online bot here are some suggetions.

  - Deploying the application in a cloud Kubenetes environment is recommended since it is already containerized.
  - Deploy on serverless env like Heroku.

## Customization

Want to customize your chatbot? Bot-chan offers flexibility to tailor it to your specific needs.

### Intention
Botchan use intention module to decide whether and how to reply to a certain message. The framework just apply the chat intetion
to all messages. If you want to extended it, add your code in [message_intent.py](./botchat/message_intent.py) and [agent.py](./botchat/agent.py) message handler registration.

### Bot personality
You may config the name and the personality via prompting in [here](https://github.com/fengyu05/bot-chan/blob/main/botchan/prompt.py#L15). 
The mapping is by intent. So you can create different bot prompting for different usecase or even have mutiply bots. 

### Slack event handling

Botchat only subcribe to Slack message events. If you want to subcribe to other event and do sth cool. Make your change in the [app.py](https://github.com/fengyu05/bot-chan/blob/main/botchan/app.py#L39). 

## Security and privicay reminder.

- Botchan does not store any information from Slack, but instead uses the Slack History API to read messages.
- It is important to be aware that if you need to log any chat messages, the author suggests only doing so when the debug flag is on. 
- The repository is not designed to be secure for production use, so use it at your own risk.








