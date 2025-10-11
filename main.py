from telegram.ext import Application, CommandHandler, CallbackQueryHandler, \
                         MessageHandler, filters, ConversationHandler

from config import config
from services.supabase_service import SupabaseService
from services.user_service import UserService
from services.github_service import GitHubService
from handlers.start_handler import StartHandler, WAITING_TOKEN, BROWSING
from handlers.repos_handler import ReposHandler
from handlers.callback_handler import CallbackHandler


def main():
    """Главная функция запуска бота"""
    
    print("=" * 60)
    print("🤖 Telegram GitHub Bot with Supabase")
    print("=" * 60)
    
    # Инициализация сервисов
    print("📦 Инициализация сервисов...")
    supabase_service = SupabaseService()
    user_service = UserService(supabase_service)
    github_service = GitHubService()
    
    # Инициализация обработчиков
    print("🔧 Инициализация обработчиков...")
    start_handler = StartHandler(user_service, github_service)
    repos_handler = ReposHandler(user_service, github_service)
    callback_handler = CallbackHandler(user_service, github_service)
    
    # Создание приложения
    print("🚀 Создание Telegram приложения...")
    app = Application.builder().token(config.BOT_TOKEN).build()
    
    # Conversation handler для /start
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_handler.start)],
        states={
            WAITING_TOKEN: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, start_handler.receive_token)
            ],
            BROWSING: [
                CommandHandler('repos', repos_handler.show_repos),
                CommandHandler('stats', repos_handler.show_stats),
                CommandHandler('delete_data', repos_handler.delete_user_data)
            ]
        },
        fallbacks=[CommandHandler('start', start_handler.start)]
    )
    
    # Регистрация обработчиков
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler('repos', repos_handler.show_repos))
    app.add_handler(CommandHandler('stats', repos_handler.show_stats))
    app.add_handler(CommandHandler('delete_data', repos_handler.delete_user_data))
    app.add_handler(CallbackQueryHandler(callback_handler.handle_callback))
    
    # Запуск бота
    print("=" * 60)
    print("✅ Бот успешно запущен!")
    print(f"🗄️  База данных: Supabase")
    print(f"🔒 Шифрование: Активно (Fernet)")
    print(f"📋 Макс. репозиториев: {config.MAX_REPOS_DISPLAY}")
    print(f"👤 Всего пользователей: {user_service.get_users_count()}")
    print("=" * 60)
    print("⌨️  Нажми Ctrl+C для остановки")
    print("=" * 60)
    
    app.run_polling()


if __name__ == '__main__':
    main()