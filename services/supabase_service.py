from supabase import create_client, Client
from typing import Optional, List, Dict, Any
from datetime import datetime
from config import config
from services.encryption_service import EncryotionService

class SupabaseService:
    """Ma'lumotlar bazasi bilan ishlash"""

    def __init__(self) -> None:
        self.client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.encryption_service = EncryotionService()
        print("Supabasega ulanish")

    def save_user_token(self, user_id: int, token: str) -> bool:
        """foydalanuvchi tokenini saqlash"""
        try:
            encrypted_token = self.encryption_service.encrypt(token)

            existing = self.client.table('users').select('user_id').eq('user_id', user_id).execute()


            if existing.data:
                self.client.table('users').update({
                    'github_token_encrypted': encrypted_token,
                    'updated_at': datetime.now().isoformat()
                }).eq('user_id', user_id).execute()

            else:
                self.client.table('users').insert({
                    'user_id': user_id,
                    'github_token_encrypted': encrypted_token
                }).execute

            return True
        except Exception as e:
            print(f"token ma'lumotlarni saqlashda xatolik: {e}")
            return False
    
    def ensure_user_exists(self, user_id: int) -> bool:
        """Убедиться что пользователь существует в БД (создать если нет)"""
        try:
            # Проверяем существует ли
            existing = self.client.table('users').select('user_id').eq('user_id', user_id).execute()
        
            if not existing.data:
                # Создаём пользователя без токена
                self.client.table('users').insert({
                    'user_id': user_id
                }).execute()
                print(f"✅ Создан новый пользователь: {user_id}")
        
            return True
        except Exception as e:
            print(f"❌ Ошибка создания пользователя: {e}")
            return False

    def get_user_token(self, user_id: int) -> Optional[str]:
        """Получить токен пользователя (с расшифровкой)"""
        try:
            response = self.client.table('users').select('github_token_encrypted').eq('user_id', user_id).execute()
            
            if response.data and response.data[0]['github_token_encrypted']:
                encrypted_token = response.data[0]['github_token_encrypted']
                return self.encryption_service.decrypt(encrypted_token)
            return None
        except Exception as e:
            print(f"❌ Ошибка получения токена: {e}")
            return None
    
    def set_current_repo(self, user_id: int, repo_name: str) -> bool:
        """Установить текущий репозиторий"""
        try:
            self.client.table('users').update({
                'current_repo': repo_name,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка установки репозитория: {e}")
            return False
    
    def get_current_repo(self, user_id: int) -> Optional[str]:
        """Получить текущий репозиторий"""
        try:
            response = self.client.table('users').select('current_repo').eq('user_id', user_id).execute()
            
            if response.data and response.data[0].get('current_repo'):
                return response.data[0]['current_repo']
            return None
        except Exception as e:
            print(f"❌ Ошибка получения репозитория: {e}")
            return None
    
    def set_current_path(self, user_id: int, path: str) -> bool:
        """Установить текущий путь"""
        try:
            self.client.table('users').update({
                'current_path': path,
                'updated_at': datetime.now().isoformat()
            }).eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка установки пути: {e}")
            return False
    
    def get_current_path(self, user_id: int) -> str:
        """Получить текущий путь"""
        try:
            response = self.client.table('users').select('current_path').eq('user_id', user_id).execute()
            
            if response.data and response.data[0].get('current_path'):
                return response.data[0]['current_path']
            return ''
        except Exception as e:
            print(f"❌ Ошибка получения пути: {e}")
            return ''
    
    def log_action(self, user_id: int, action_type: str, 
                   repo_name: str = None, file_path: str = None) -> bool:
        """Логировать действие пользователя"""
        try:
            self.ensure_user_exists(user_id)
            self.client.table('action_history').insert({
                'user_id': user_id,
                'action_type': action_type,
                'repo_name': repo_name,
                'file_path': file_path
            }).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка логирования: {e}")
            return False
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Получить статистику пользователя"""
        try:
            # Общее количество действий
            total_response = self.client.table('action_history').select('id', count='exact').eq('user_id', user_id).execute()
            total_actions = total_response.count if total_response.count else 0
            
            # Действия по типам
            actions_response = self.client.table('action_history').select('action_type').eq('user_id', user_id).execute()
            
            actions_by_type = {}
            if actions_response.data:
                for action in actions_response.data:
                    action_type = action['action_type']
                    actions_by_type[action_type] = actions_by_type.get(action_type, 0) + 1
            
            # Последние 5 действий
            recent_response = self.client.table('action_history').select('*').eq('user_id', user_id).order('created_at', desc=True).limit(5).execute()
            recent_actions = recent_response.data if recent_response.data else []
            
            return {
                'total_actions': total_actions,
                'actions_by_type': actions_by_type,
                'recent_actions': recent_actions
            }
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {
                'total_actions': 0,
                'actions_by_type': {},
                'recent_actions': []
            }
    
    def delete_user_data(self, user_id: int) -> bool:
        """Удалить все данные пользователя (GDPR compliance)"""
        try:
            # Удаляем историю действий
            self.client.table('action_history').delete().eq('user_id', user_id).execute()
            # Удаляем пользователя
            self.client.table('users').delete().eq('user_id', user_id).execute()
            return True
        except Exception as e:
            print(f"❌ Ошибка удаления данных: {e}")
            return False
    
    def get_all_users_count(self) -> int:
        """Получить количество всех пользователей"""
        try:
            response = self.client.table('users').select('user_id', count='exact').execute()
            if response.count:
                return response.count
            else:
                return 0
        except Exception as e:
            print(f"❌ Ошибка подсчёта пользователей: {e}")
            return 0