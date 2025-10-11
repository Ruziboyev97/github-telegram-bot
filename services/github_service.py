
import requests
import base64
from typing import Optional, List, Dict, Any
from config import config

class GitHubService:
    """Работа с GitHub API"""
    
    def __init__(self):
        self.api_url = config.GITHUB_API_URL
    
    def _get_headers(self, token: str) -> Dict[str, str]:
        """Получить заголовки для запроса"""
        return {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    
    def validate_token(self, token: str) -> bool:
        """Проверить валидность токена"""
        try:
            headers = self._get_headers(token)
            response = requests.get(f'{self.api_url}/user', headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка валидации токена: {e}")
            return False
    
    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе GitHub"""
        try:
            headers = self._get_headers(token)
            response = requests.get(f'{self.api_url}/user', headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Ошибка получения инфо пользователя: {e}")
            return None
    
    def get_repositories(self, token: str) -> Optional[List[Dict[str, Any]]]:
        """Получить список репозиториев"""
        try:
            headers = self._get_headers(token)
            response = requests.get(
                f'{self.api_url}/user/repos',
                headers=headers,
                params={'per_page': 100, 'sort': 'updated'},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Ошибка получения репозиториев: {e}")
            return None
    
    def get_contents(self, token: str, repo_full_name: str, path: str = '') -> Optional[Any]:
        """Получить содержимое репозитория/папки"""
        try:
            headers = self._get_headers(token)
            url = f'{self.api_url}/repos/{repo_full_name}/contents/{path}'
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ Ошибка получения содержимого: {e}")
            return None
    
    def create_file(self, token: str, repo_full_name: str, path: str, 
                   content: str, message: str) -> bool:
        """Создать файл в репозитории"""
        try:
            headers = self._get_headers(token)
            url = f'{self.api_url}/repos/{repo_full_name}/contents/{path}'
            
            encoded_content = base64.b64encode(content.encode()).decode()
            
            data = {
                'message': message,
                'content': encoded_content
            }
            
            response = requests.put(url, headers=headers, json=data, timeout=10)
            return response.status_code == 201
        except Exception as e:
            print(f"❌ Ошибка создания файла: {e}")
            return False
    
    def delete_file(self, token: str, repo_full_name: str, path: str, 
                   sha: str, message: str) -> bool:
        """Удалить файл из репозитория"""
        try:
            headers = self._get_headers(token)
            url = f'{self.api_url}/repos/{repo_full_name}/contents/{path}'
            
            data = {
                'message': message,
                'sha': sha
            }
            
            response = requests.delete(url, headers=headers, json=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"❌ Ошибка удаления файла: {e}")
            return False