from storage import token_storage

class Config:
    def __init__(self, user_id):
        self.user_id = user_id
    
    @property
    def BOT_TOKEN(self):
        return token_storage.get_token(self.user_id, 'bot_token')
    
    @property
    def GITHUB_TOKEN(self):
        return token_storage.get_token(self.user_id, 'github_token')
    
    def validate(self):
        if not self.BOT_TOKEN:
            return False, "❌ Telegram Bot Token не настроен. Используйте /setup"
        if not self.GITHUB_TOKEN:
            return False, "❌ GitHub Token не настроен. Используйте /setup"
        return True, "✅ Все токены настроены!"