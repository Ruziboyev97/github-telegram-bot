import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters, 
    ContextTypes, ConversationHandler
)
from config import Config
from github_api import GitHubManager
from storage import token_storage

# Состояния для ConversationHandler
SETUP_BOT_TOKEN, SETUP_GITHUB_TOKEN = range(2)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleGitHubBot:
    def __init__(self):
        self.app = Application.builder().build()  # Пока без токена
        self.setup_handlers()
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        # Conversation для настройки
        setup_conv = ConversationHandler(
            entry_points=[CommandHandler("setup", self.setup_start)],
            states={
                SETUP_BOT_TOKEN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.setup_bot_token)
                ],
                SETUP_GITHUB_TOKEN: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.setup_github_token)
                ],
            },
            fallbacks=[CommandHandler("cancel", self.setup_cancel)],
        )
        
        # Основные команды
        self.app.add_handler(setup_conv)
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("repos", self.list_repos))
        self.app.add_handler(CommandHandler("create", self.create_repo))
        self.app.add_handler(CommandHandler("status", self.check_status))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user = update.effective_user
        user_id = user.id
        
        config = Config(user_id)
        has_tokens, message = config.validate()
        
        if has_tokens:
            await update.message.reply_text(
                f"👋 С возвращением, {user.first_name}!\n"
                f"{message}\n\n"
                "Используйте /help для списка команд"
            )
        else:
            await update.message.reply_text(
                f"👋 Привет, {user.first_name}!\n"
                f"{message}\n\n"
                "Для начала работы настройте токены:\n"
                "/setup - настройка токенов\n"
                "/help - помощь"
            )
    
    # === НАСТРОЙКА ТОКЕНОВ ===
    
    async def setup_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Начало настройки токенов"""
        user_id = update.effective_user.id
        
        await update.message.reply_text(
            "🔧 **Настройка токенов**\n\n"
            "1. 📱 **Telegram Bot Token**:\n"
            "   - Напишите @BotFather в Telegram\n"
            "   - Команда: /newbot\n"
            "   - Пришлите полученный токен\n\n"
            "Введите ваш Telegram Bot Token:",
            reply_markup=ReplyKeyboardRemove()
        )
        
        return SETUP_BOT_TOKEN
    
    async def setup_bot_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение Bot Token"""
        user_id = update.effective_user.id
        bot_token = update.message.text.strip()
        
        # Простая валидация токена
        if not bot_token or ":" not in bot_token:
            await update.message.reply_text(
                "❌ Неверный фортокен токена. Должен быть вида: 1234567890:ABCdef...\n"
                "Попробуйте снова:"
            )
            return SETUP_BOT_TOKEN
        
        # Сохраняем токен
        token_storage.set_token(user_id, 'bot_token', bot_token)
        context.user_data['bot_token'] = bot_token
        
        await update.message.reply_text(
            "✅ Telegram Bot Token сохранен!\n\n"
            "2. 🐙 **GitHub Personal Access Token**:\n"
            "   - Зайдите на https://github.com/settings/tokens\n"
            "   - Создайте новый token с правами: repo, user\n"
            "   - Пришлите полученный токен\n\n"
            "Введите ваш GitHub Token:"
        )
        
        return SETUP_GITHUB_TOKEN
    
    async def setup_github_token(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Сохранение GitHub Token"""
        user_id = update.effective_user.id
        github_token = update.message.text.strip()
        
        if not github_token or len(github_token) < 10:
            await update.message.reply_text(
                "❌ Неверный формат токена. Попробуйте снова:"
            )
            return SETUP_GITHUB_TOKEN
        
        # Сохраняем GitHub токен
        token_storage.set_token(user_id, 'github_token', github_token)
        
        # Тестируем подключение
        try:
            github_mgr = GitHubManager(user_id)
            user_info = github_mgr.test_connection()
            
            await update.message.reply_text(
                f"✅ **Настройка завершена!**\n\n"
                f"🔗 Подключено к GitHub аккаунту: {user_info}\n\n"
                f"Теперь используйте:\n"
                f"/repos - мои репозитории\n"
                f"/create - создать репозиторий\n"
                f"/status - статус настроек"
            )
        except Exception as e:
            await update.message.reply_text(
                f"⚠️ GitHub Token сохранен, но ошибка подключения: {e}\n"
                f"Проверьте правильность токена и права доступа."
            )
        
        return ConversationHandler.END
    
    async def setup_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Отмена настройки"""
        await update.message.reply_text(
            "❌ Настройка отменена.\n"
            "Используйте /setup чтобы начать заново.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    
    # === ОСНОВНЫЕ КОМАНДЫ ===
    
    async def check_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Проверка статуса настроек"""
        user_id = update.effective_user.id
        config = Config(user_id)
        has_tokens, message = config.validate()
        
        status_text = f"🔍 **Статус настроек**\n\n"
        status_text += f"Telegram Bot: {'✅' if config.BOT_TOKEN else '❌'}\n"
        status_text += f"GitHub Token: {'✅' if config.GITHUB_TOKEN else '❌'}\n\n"
        status_text += message
        
        await update.message.reply_text(status_text)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        help_text = """
🤖 **GitHub Bot - Помощь**

🔧 **Настройка:**
/setup - Настройка токенов (обязательно!)
/status - Проверка статуса

📂 **GitHub команды:**
/repos - Мои репозитории
/create <name> - Создать репозиторий

❓ **Общее:**
/help - Эта справка
/start - Перезапуск бота
        """
        await update.message.reply_text(help_text)
    
    async def list_repos(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /repos - список репозиториев"""
        user_id = update.effective_user.id
        config = Config(user_id)
        
        has_tokens, message = config.validate()
        if not has_tokens:
            await update.message.reply_text(message)
            return
        
        await update.message.reply_text("🔄 Получаю репозитории...")
        
        try:
            github_mgr = GitHubManager(user_id)
            repos = github_mgr.get_my_repos()
            
            if isinstance(repos, str):  # Ошибка
                await update.message.reply_text(repos)
            else:
                message = "📂 **Мои репозитории:**\n\n"
                for repo in repos[:5]:  # Покажем первые 5
                    desc = repo['description'] or "Без описания"
                    message += f"🔹 **{repo['name']}**\n"
                    message += f"   📝 {desc}\n"
                    message += f"   ⭐ {repo['stars']} stars\n"
                    message += f"   🔗 {repo['url']}\n\n"
                
                await update.message.reply_text(message)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    async def create_repo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /create - создать репозиторий"""
        user_id = update.effective_user.id
        config = Config(user_id)
        
        has_tokens, message = config.validate()
        if not has_tokens:
            await update.message.reply_text(message)
            return
        
        if not context.args:
            await update.message.reply_text("❌ Укажите название: /create my-project")
            return
        
        repo_name = " ".join(context.args)
        await update.message.reply_text(f"🔄 Создаю '{repo_name}'...")
        
        try:
            github_mgr = GitHubManager(user_id)
            result = github_mgr.create_repo(repo_name)
            await update.message.reply_text(result)
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка: {e}")
    
    def run(self):
        """Запуск бота"""
        logger.info("🤖 Запускаю бота...")
        self.app.run_polling()

if __name__ == "__main__":
    bot = SimpleGitHubBot()
    bot.run()