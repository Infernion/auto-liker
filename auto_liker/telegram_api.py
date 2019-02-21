import telegram


class TelegramAPI:
    def __init__(self, token):
        self.api = telegram.Bot(token=token)

    def get_new_instagram_urls_from_chat(self, chat_id):
        for upd in self.api.get_updates():
            if upd.message.chat.id == chat_id:
                text = upd.message.text
                if text and "instagram.com/p/" in text:
                    yield text

    # def register_new_account(self):
    #     self.api.send_message
