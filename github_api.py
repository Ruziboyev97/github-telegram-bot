from github import Github
from config import Config

class GitHubManager:
    def __init__(self, user_id):
        config = Config(user_id)
        self.g = Github(config.GITHUB_TOKEN)
        self.user = self.g.get_user()
    
    def test_connection(self):
        """Тест подключения к GitHub"""
        try:
            user = self.g.get_user()
            return user.login
        except Exception as e:
            raise Exception(f"GitHub connection failed: {e}")
    
    def get_my_repos(self):
        """Получить мои репозитории"""
        try:
            repos = []
            for repo in self.user.get_repos():
                repos.append({
                    'name': repo.name,
                    'description': repo.description or "No description",
                    'url': repo.html_url,
                    'stars': repo.stargazers_count
                })
            return repos
        except Exception as e:
            return f"❌ GitHub Error: {e}"
    
    def create_repo(self, name, description=""):
        """Создать новый репозиторий"""
        try:
            repo = self.user.create_repo(name, description=description, auto_init=True)
            return f"✅ Репозиторий создан!\n🔗 {repo.html_url}"
        except Exception as e:
            return f"❌ GitHub Error: {e}"