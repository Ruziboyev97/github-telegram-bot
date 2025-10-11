from typing import Optional, Dict, Any
from services.supabase_service import SupabaseService

class UserService:
    """Управление пользователями через Supabase"""
    
    def __init__(self, supabase_service: SupabaseService):
        self.db = supabase_service
    
    def save_token(self, user_id: int, token: str) -> bool:
        """Сохранить токен пользователя"""
        return self.db.save_user_token(user_id, token)
    
    def get_token(self, user_id: int) -> Optional[str]:
        """Получить токен пользователя"""
        return self.db.get_user_token(user_id)
    
    def set_current_repo(self, user_id: int, repo_name: str) -> bool:
        """Установить текущий репозиторий"""
        return self.db.set_current_repo(user_id, repo_name)
    
    def get_current_repo(self, user_id: int) -> Optional[str]:
        """Получить текущий репозиторий"""
        return self.db.get_current_repo(user_id)
    
    def set_current_path(self, user_id: int, path: str) -> bool:
        """Установить текущий путь"""
        return self.db.set_current_path(user_id, path)
    
    def get_current_path(self, user_id: int) -> str:
        """Получить текущий путь"""
        return self.db.get_current_path(user_id)
    
    def log_action(self, user_id: int, action_type: str, 
                   repo_name: str = None, file_path: str = None) -> bool:
        """Логировать действие"""
        return self.db.log_action(user_id, action_type, repo_name, file_path)
    
    def get_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику"""
        return self.db.get_user_stats(user_id)
    
    def delete_user(self, user_id: int) -> bool:
        """Удалить пользователя"""
        return self.db.delete_user_data(user_id)
    
    def get_users_count(self) -> int:
        """Получить общее количество пользователей"""
        return self.db.get_all_users_count()