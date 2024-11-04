from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from botchan.core.bot_proxy import BotProxy
from botchan.logger import get_logger
from botchan.utt.singleton import Singleton

logger = get_logger(__name__)


class SlackBotClient(App, Singleton):
    proxies: list[BotProxy] = []

    def add_proxy(self, proxy: BotProxy) -> None:
        self.proxies.append(proxy)

    def run(self, token: str) -> None:
        handler = SocketModeHandler(
            app_token=token,
            app=self,
            logger=logger,
        )
        handler.start()
