from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from services.user_service import UserService
from services.github_service import GitHubService

WAITING_TOKEN, BROWSING = range(2)

class StartHandler:
    """Обработчик команды /start"""
    
    def __init__(self, user_service: UserService, github_service: GitHubService):
        self.user_service = user_service
        self.github_service = github_service
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Команда /start"""
        user_name = update.effective_user.first_name
        user_id = update.effective_user.id

        self.user_service.ensure_user_exists(user_id)
        
        await update.message.reply_text(
            f"👋 Привет, {user_name}! Я бот для работы с GitHub.\n\n"
            "📝 Отправь мне свой GitHub Personal Access Token.\n\n"
            "🔑 Как получить токен:\n"
            "1. github.com/settings/tokens\n"
            "2. Generate new token (classic)\n"
            "3. Выбери права: repo, delete_repo\n"
            "4. Скопируй и отправь мне\n\n"
            "🔒 Твой токен будет зашифрован и безопасно сохранён в Supabase!"
        )
        return WAITING_TOKEN
    
    async def receive_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Получение и проверка токена"""
        token = update.message.text.strip()
        user_id = update.effective_user.id
        
        # Удаляем сообщение с токеном для безопасности
        try:
            await update.message.delete()
        except:
            pass
        
        # Проверяем токен
        if not self.github_service.validate_token(token):
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Неверный токен! Попробуй ещё раз или используй /start"
            )
            return WAITING_TOKEN
        
        # Получаем инфо пользователя GitHub
        github_user = self.github_service.get_user_info(token)
        github_username = github_user['login'] if github_user else "Unknown"
        
        # Сохраняем токен (зашифрованный)
        if self.user_service.save_token(user_id, token):
            self.user_service.log_action(user_id, 'token_saved')
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ Токен безопасно сохранён в Supabase!\n"
                     f"👤 GitHub: @{github_username}\n\n"
                     "Команды:\n"
                     "/repos - Репозитории\n"
                     "/stats - Статистика\n"
                     "/delete_data - Удалить мои данные\n"
                     "/help - Помощь"
            )
            return BROWSING
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="❌ Ошибка сохранения токена. Попробуй позже."
            )
            return WAITING_TOKEN