from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from services.user_service import UserService
from services.github_service import GitHubService

class CallbackHandler:
    """Обработчик нажатий на кнопки"""
    
    def __init__(self, user_service: UserService, github_service: GitHubService):
        self.user_service = user_service
        self.github_service = github_service
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Основной обработчик callback'ов"""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        token = self.user_service.get_token(user_id)
        
        if not token:
            await query.edit_message_text("❌ Токен не найден. Используй /start")
            return
        
        data = query.data
        
        if data.startswith("repo:"):
            await self._handle_repo(query, user_id, token, data)
        elif data.startswith("item:"):
            await self._handle_item(query, user_id, token, data)
        elif data.startswith("delete:"):
            await self._handle_delete(query, user_id, token, data)
        elif data == "back_repos":
            await self._handle_back_to_repos(query, user_id, token)
    
    async def _handle_repo(self, query, user_id: int, token: str, data: str) -> None:
        """Обработка открытия репозитория"""
        repo_name = data.split(":", 1)[1]
        self.user_service.set_current_repo(user_id, repo_name)
        self.user_service.set_current_path(user_id, '')
        self.user_service.log_action(user_id, 'open_repo', repo_name)
        
        contents = self.github_service.get_contents(token, repo_name)
        
        if contents:
            keyboard = self._build_contents_keyboard(contents, repo_name, is_root=True)
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"📦 Репозиторий: {repo_name}",
                reply_markup=reply_markup
            )
        else:
            await query.edit_message_text("❌ Не удалось загрузить содержимое репозитория")
    
    async def _handle_item(self, query, user_id: int, token: str, data: str) -> None:
        """Обработка открытия папки или файла"""
        parts = data.split(":", 2)
        item_type = parts[1]
        item_path = parts[2]
        repo_name = self.user_service.get_current_repo(user_id)
        
        if item_type == "dir":
            self.user_service.set_current_path(user_id, item_path)
            self.user_service.log_action(user_id, 'open_folder', repo_name, item_path)
            contents = self.github_service.get_contents(token, repo_name, item_path)
            
            if contents:
                keyboard = self._build_contents_keyboard(contents, repo_name, is_root=False)
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(f"📁 {item_path}", reply_markup=reply_markup)
        else:
            self.user_service.log_action(user_id, 'view_file', repo_name, item_path)
            contents = self.github_service.get_contents(token, repo_name, item_path)
            
            if contents:
                keyboard = [
                    [InlineKeyboardButton("🗑 Удалить файл", 
                                        callback_data=f"delete:{item_path}:{contents['sha']}")],
                    [InlineKeyboardButton("⬅️ Назад", callback_data=f"repo:{repo_name}")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                size_kb = contents['size'] / 1024
                await query.edit_message_text(
                    f"📄 Файл: {item_path}\n"
                    f"📊 Размер: {size_kb:.2f} KB",
                    reply_markup=reply_markup
                )
    
    async def _handle_delete(self, query, user_id: int, token: str, data: str) -> None:
        """Обработка удаления файла"""
        parts = data.split(":", 2)
        file_path = parts[1]
        sha = parts[2]
        repo_name = self.user_service.get_current_repo(user_id)
        
        success = self.github_service.delete_file(
            token, repo_name, file_path, sha, 
            f"Delete {file_path} via Telegram bot"
        )
        
        if success:
            self.user_service.log_action(user_id, 'delete_file', repo_name, file_path)
            await query.edit_message_text(f"✅ Файл {file_path} успешно удалён!")
        else:
            await query.edit_message_text(f"❌ Ошибка при удалении файла")
    
    async def _handle_back_to_repos(self, query, user_id: int, token: str) -> None:
        """Возврат к списку репозиториев"""
        repos = self.github_service.get_repositories(token)
        
        if repos:
            keyboard = []
            for repo in repos[:20]:
                button_text = f"📁 {repo['name']}"
                if repo['private']:
                    button_text += " 🔒"
                keyboard.append([InlineKeyboardButton(
                    button_text,
                    callback_data=f"repo:{repo['full_name']}"
                )])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("📦 Выбери репозиторий:", reply_markup=reply_markup)
    
    def _build_contents_keyboard(self, contents, repo_name: str, is_root: bool):
        """Построить клавиатуру с содержимым папки"""
        keyboard = []
        
        for item in contents:
            icon = "📁" if item['type'] == 'dir' else "📄"
            keyboard.append([InlineKeyboardButton(
                f"{icon} {item['name']}",
                callback_data=f"item:{item['type']}:{item['path']}"
            )])
        
        if is_root:
            keyboard.append([InlineKeyboardButton("⬅️ Назад к репозиториям", callback_data="back_repos")])
        else:
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data=f"repo:{repo_name}")])
        
        return keyboard