from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.user_service import UserService
from services.github_service import GitHubService
from config import config

class ReposHandler:
    """Обработчик команды /repos"""
    
    def __init__(self, user_service: UserService, github_service: GitHubService):
        self.user_service = user_service
        self.github_service = github_service
    
    async def show_repos(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать список репозиториев"""
        user_id = update.effective_user.id
        token = self.user_service.get_token(user_id)
        
        if not token:
            await update.message.reply_text("❌ Сначала отправь токен через /start")
            return
        
        await update.message.reply_text("🔄 Загружаю репозитории...")
        
        repos = self.github_service.get_repositories(token)
        
        if not repos:
            await update.message.reply_text("❌ Не удалось получить репозитории")
            return
        
        self.user_service.log_action(user_id, 'view_repos')
        
        keyboard = []
        for repo in repos[:config.MAX_REPOS_DISPLAY]:
            button_text = f"📁 {repo['name']}"
            if repo['private']:
                button_text += " 🔒"
            
            keyboard.append([InlineKeyboardButton(
                button_text,
                callback_data=f"repo:{repo['full_name']}"
            )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"📦 Твои репозитории ({len(repos)}):",
            reply_markup=reply_markup
        )
    
    async def show_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать статистику пользователя"""
        user_id = update.effective_user.id
        stats = self.user_service.get_stats(user_id)
        
        text = "📊 Твоя статистика:\n\n"
        text += f"Всего действий: {stats['total_actions']}\n\n"
        
        if stats['actions_by_type']:
            text += "📈 По типам:\n"
            for action_type, count in stats['actions_by_type'].items():
                emoji = self._get_action_emoji(action_type)
                text += f"{emoji} {action_type}: {count}\n"
        
        if stats['recent_actions']:
            text += f"\n🕐 Последние действия:\n"
            for action in stats['recent_actions'][:5]:
                text += f"• {action['action_type']}"
                if action.get('repo_name'):
                    text += f" ({action['repo_name']})"
                text += "\n"
        
        # Общая статистика бота
        total_users = self.user_service.get_users_count()
        text += f"\n👥 Всего пользователей бота: {total_users}"
        
        await update.message.reply_text(text)
    
    def _get_action_emoji(self, action_type: str) -> str:
        """Получить эмодзи для типа действия"""
        emojis = {
            'token_saved': '🔑',
            'view_repos': '📦',
            'open_repo': '📁',
            'open_folder': '📂',
            'view_file': '📄',
            'delete_file': '🗑',
            'create_file': '➕'
        }
        return emojis.get(action_type, '•')
    
    async def delete_user_data(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Удалить данные пользователя"""
        user_id = update.effective_user.id
        
        if self.user_service.delete_user(user_id):
            await update.message.reply_text(
                "✅ Все твои данные удалены из Supabase.\n"
                "Используй /start чтобы начать заново."
            )
        else:
            await update.message.reply_text(
                "❌ Ошибка при удалении данных. Попробуй позже."
            )