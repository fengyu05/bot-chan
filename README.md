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
 <tr>
    <td>Looking math with LLM</td>
    <td>Checing Arxiv</td>
    <td>Doing google search</td>
 </tr>
    <td><img width="768" alt="Screenshot 2023-09-15 at 12 02 42 PM" src="https://github.com/fengyu05/bot-chan/assets/7340368/2447d5b4-c674-45b5-977d-b282470b4047">
</td>
    <td><img width="755" alt="Screenshot 2023-09-15 at 11 59 44 AM" src="https://github.com/fengyu05/bot-chan/assets/7340368/596f8464-fc52-4742-9b10-834233ffd8da">
</td>
    <td><img width="769" alt="Screenshot 2023-09-15 at 11 58 59 AM" src="https://github.com/fengyu05/bot-chan/assets/7340368/c27a6ca3-da3b-4ba2-bc19-4610d65d7e25">
</td> 
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

## Deployment

Botchan is fully functional and running on your local dev machine or laptop.
If you are looking at optional to turn it into a 24/7 online bot here are some suggestions.

  - Deploying the application in a cloud Kubernetes environment is recommended since it is already containerized.
  - Deploy on serverless env like Heroku.

## Customization

Want to customize your chatbot? Bot-chan offers the flexibility to tailor it to your specific needs.

### Intention
Botchan uses an intention module to decide whether and how to reply to a certain message. The framework just applies the chat intention
to all messages. If you want to extend it, add your code in [message_intent.py](./botchan/message_intent.py) and [agent.py](./botchan/agent.py) message handler registration.

### Chain of Thought mode

Botchan can use a chain of thought mode to break down the thinking process and show it in its chat. To engage Chain-ot-thought mode, start a message with prefix `:thought:`. You may upload a customized slack emoji for it.

### Using tools
Botchan uses some preconfig lang-chain tools in the chain of thought mode. If you want to add more tools or customize then, edit them [here](https://github.com/fengyu05/bot-chan/blob/master/botchan/agents/mrkl.py#L8).  Some tools may require API keys to be set in the env. 



### Bot personality
You may configure the name and the personality via prompting in [here](https://github.com/fengyu05/bot-chan/blob/main/botchan/prompt.py#L15). 
The mapping is by intent. So you can create different bot prompting for different use cases or even have multiple bots. 

### Slack event handling

Botchat only subscribes to Slack message events. If you want to subscribe to other events and do sth cool. Make your change in the [app.py](https://github.com/fengyu05/bot-chan/blob/main/botchan/app.py#L39). 

## Security and privacy reminder.

- Botchan does not store any information from Slack but instead uses the Slack History API to read messages.
- It is essential to be aware that if you need to log chat messages, the author suggests only doing so when the debug flag is on. 
- The repository is not designed to be secure for production use, so use it at your own risk.








