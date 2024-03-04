# Introduction
Welcome to Bot-chan! This is a minimal but fully functional framework for a Slack AI Chatbot that is easy setup and customize.

We made Botchan open source to help those who want to create their own chatbot application but don't know where to start. You can use Botchan as a personal chatbot on your Slack workspace, or develop it into a product or something even bigger.

## Spotlights

As a Slack Chatbot application, Botchan has the following features.

- Reposonse to IM(direct message) or `@` mentioned in public channels.
- Engage in interactive conversions.
- Retrieval-augmented Generation.
- Index knowledge from text messages, web base url and uploaded PDF.
- Capable of using tools: like proactive invlove Google search and Wiki lookup.

<code><table>
  <tr>
    <td>Learn knowledge from PDF</td>
    <td>Learn from WEB url</td>
    <td>Learn from pinned messages</td>
  </tr>
  <tr>
    <td><img width="330" alt="Screenshot 2024-03-04 at 2 37 58 PM" src="https://github.com/fengyu05/bot-chan/assets/7340368/e6ea9635-a512-4257-8ef3-73e2a0f903a2">
</td>
    <td><div>
      <p><img width="715" alt="Screenshot 2024-03-04 at 9 38 54 AM" src="https://github.com/fengyu05/bot-chan/assets/7340368/ac1021b6-f26b-42df-91ad-64dcacc91842">
</p>
      <p><img width="752" alt="Screenshot 2024-03-04 at 9 39 02 AM" src="https://github.com/fengyu05/bot-chan/assets/7340368/e48efdfb-6c52-494c-8b0d-4582fb9ede33">
</p>
    </div></td>
    <td>
      <div>
        <p><img width="721" alt="rag1" src="https://github.com/fengyu05/bot-chan/assets/7340368/e80c2677-508a-4882-8292-55c5a6563b3e">
</p>
        <p><img width="378" alt="rag2" src="https://github.com/fengyu05/bot-chan/assets/7340368/51705f64-fee7-4f08-b78a-342b1765c3aa">
</p>
        <p><img width="337" alt="rag3" src="https://github.com/fengyu05/bot-chan/assets/7340368/f3b47444-9dba-4cc7-8771-33316ae40570">
</p>
      </div>
    </td>
 </tr>
 <tr>
    <td>Context awareness</td>
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



## Developer guide

### Tooling

Run make to see help tips
```
===== All tasks =====
build                build image
server               start prod server
server-dev           start dev server
bash                 Connect to a bash within the docker image
ci-bash              Connect to a bash within the tool image(faster), for running task like `poetry lock`
lint                 Lint the code folder
fmt                  Apply python formater(will edit the code)
```

### Updating dependencies

Method 1. With local poetry install:

edit `pyproject.toml` and run `poetry lock`

Method 2. Run `make ci-bash` to get a ci bash shell; then same with above.
 
### Customization
Want to customize your chatbot? Bot-chan offers the flexibility to tailor it to your specific needs. See [settings.py](./botchan/settings.py)
You can use a env file if you are deploying it with docker or kube.

### Intention
Botchan uses an intention module to decide whether and how to reply to a certain message. The framework just applies the chat intention
to all messages. If you want to extend it, add your code in [message_intent.py](./botchan/message_intent.py) and [agent.py](./botchan/agent.py) message handler registration.

### Slack event handling
Botchat only subscribes to Slack message events. If you want to subscribe to other events and do sth cool. Make your change in the [app.py](https://github.com/fengyu05/bot-chan/blob/main/botchan/app.py#L39).

## Security and privacy reminder.
- It is essential to be aware that if you need to log chat messages, the author suggests only doing so when the debug flag is on. 
- The repository is not designed to be secure for production use, so use it at your own risk.
