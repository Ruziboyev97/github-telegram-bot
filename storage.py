import json
import os

class TokenStorage:
    def __init__(self, filename="tokens.json"):
        self.filename = filename
        self.tokens = self._load_tokens()
    
    def _load_tokens(self):
        """Загружаем токены из файла"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_tokens(self):
        """Сохраняем токены в файл"""
        with open(self.filename, 'w') as f:
            json.dump(self.tokens, f, indent=2)
    
    def set_token(self, user_id, token_type, token_value):
        """Сохраняем токен пользователя"""
        if str(user_id) not in self.tokens:
            self.tokens[str(user_id)] = {}
        
        self.tokens[str(user_id)][token_type] = token_value
        self._save_tokens()
    
    def get_token(self, user_id, token_type):
        """Получаем токен пользователя"""
        return self.tokens.get(str(user_id), {}).get(token_type)
    
    def has_tokens(self, user_id):
        """Проверяем, есть ли у пользователя токены"""
        user_data = self.tokens.get(str(user_id), {})
        return 'bot_token' in user_data and 'github_token' in user_data

# Глобальное хранилище
token_storage = TokenStorage()