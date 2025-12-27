import asyncio
import logging
from typing import Optional, Dict, Any
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram import F
import yaml
import os
import time
from datetime import datetime

from ..core.database import DatabaseManager
from ..core.config import ConfigManager
from ..utils.helpers import format_uptime


class ForelkaInlineBot:
    def __init__(self):
        self.config = ConfigManager()
        self.inline_config = self.config.get_inline_bot_config()
        
        if not self.inline_config.get('enabled', True):
            return
        
        self.token = self.inline_config.get('token', '')
        self.owner_id = self.inline_config.get('owner_id', 0)
        
        if not self.token:
            return
        
        self.bot = Bot(token=self.token)
        self.dp = Dispatcher()
        self.db = DatabaseManager(self.config.get("database_path", "forelka.db"))
        
        self.START_TIME = time.time()
        self.CACHE = {}
        self.CACHE_TTL = 30
        
        self._setup_handlers()
        self._load_strings()
    
    def _load_strings(self):
        strings_path = "strings/ru.yml"
        if os.path.exists(strings_path):
            with open(strings_path, 'r', encoding='utf-8') as f:
                self.strings = yaml.safe_load(f)
        else:
            self.strings = {
                'inline': {
                    'not_owner': "❌ Доступ запрещен",
                    'last_logs': "📄 Последние 20 строк лога",
                    'status': "ℹ️ Статус Forelka",
                    'search': "🔍 Поиск в логах",
                    'help': "❓ Помощь по командам",
                    'log_file_missing': "Лог-файл отсутствует.",
                    'log_empty': "Лог пуст.",
                    'search_no_results': "По запросу '{keyword}' ничего не найдено.",
                    'status_text': "🟢 Статус Forelka\n\n🕒 Аптайм: {uptime}\n📄 Лог-файл: {log_status}"
                }
            }
    
    def _setup_handlers(self):
        self.dp.message.register(self._start_handler, CommandStart())
        self.dp.message.register(self._help_handler, Command("help"))
        self.dp.inline_query.register(self._inline_query_handler)
    
    async def _start_handler(self, message: types.Message):
        if message.from_user.id != self.owner_id:
            await message.answer(self.strings['inline']['not_owner'])
            return
        
        await message.answer("🤖 Inline bot готов к работе!")
    
    async def _help_handler(self, message: types.Message):
        if message.from_user.id != self.owner_id:
            await message.answer(self.strings['inline']['not_owner'])
            return
        
        help_text = (
            "Используйте:\n"
            "- Пустой запрос — последние строки лога\n"
            "- status — статус юзербота\n"
            "- search <слово> — поиск по логам"
        )
        await message.answer(help_text)
    
    async def _inline_query_handler(self, inline_query: InlineQuery):
        if inline_query.from_user.id != self.owner_id:
            await self.bot.answer_inline_query(inline_query.id, results=[], cache_time=1)
            return
        
        query = inline_query.query.strip()
        results = await self._get_inline_results(query)
        await self.bot.answer_inline_query(inline_query.id, results, cache_time=1)
    
    async def _get_inline_results(self, query: str):
        if query in self.CACHE:
            cached_time, results = self.CACHE[query]
            if time.time() - cached_time < self.CACHE_TTL:
                return results
        
        results = []
        
        if query == "":
            text = await self._get_recent_logs(20)
            results.append(InlineQueryResultArticle(
                id="last_logs",
                title=self.strings['inline']['last_logs'],
                input_message_content=InputTextMessageContent(message_text=text),
                description="Показать последние 20 строк лога"
            ))
        
        elif query.lower() == "status":
            text = await self._get_status_text()
            results.append(InlineQueryResultArticle(
                id="status",
                title=self.strings['inline']['status'],
                input_message_content=InputTextMessageContent(message_text=text, parse_mode="HTML"),
                description="Показать статус и аптайм"
            ))
        
        elif query.lower().startswith("search "):
            keyword = query[7:].strip()
            if keyword:
                text = await self._search_logs(keyword, 15)
            else:
                text = "Введите ключевое слово после команды 'search'"
            
            results.append(InlineQueryResultArticle(
                id="search",
                title=f"🔍 Поиск: {keyword}" if keyword else self.strings['inline']['search'],
                input_message_content=InputTextMessageContent(message_text=text),
                description=f"Результаты поиска по '{keyword}'" if keyword else "Поиск в логах"
            ))
        
        else:
            text = (
                "Используйте:\n"
                "- Пустой запрос — последние строки лога\n"
                "- status — статус юзербота\n"
                "- search <слово> — поиск по логам"
            )
            results.append(InlineQueryResultArticle(
                id="help",
                title=self.strings['inline']['help'],
                input_message_content=InputTextMessageContent(message_text=text),
                description="Помощь"
            ))
        
        self.CACHE[query] = (time.time(), results)
        return results
    
    async def _get_recent_logs(self, num_lines: int = 20) -> str:
        log_file = 'forelka.log'
        if not os.path.exists(log_file):
            return self.strings['inline']['log_file_missing']
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return "".join(lines[-num_lines:]).strip() or self.strings['inline']['log_empty']
        except Exception as e:
            return f"Ошибка чтения логов: {e}"
    
    async def _search_logs(self, keyword: str, max_results: int = 10) -> str:
        log_file = 'forelka.log'
        if not os.path.exists(log_file):
            return self.strings['inline']['log_file_missing']
        
        keyword = keyword.lower()
        found = []
        
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    if keyword in line.lower():
                        found.append(line.strip())
                        if len(found) >= max_results:
                            break
            
            if not found:
                return self.strings['inline']['search_no_results'].format(keyword=keyword)
            
            return "\n".join(found)
        except Exception as e:
            return f"Ошибка поиска: {e}"
    
    async def _get_status_text(self) -> str:
        uptime = format_uptime(time.time() - self.START_TIME)
        log_exists = os.path.exists('forelka.log')
        
        return self.strings['inline']['status_text'].format(
            uptime=uptime,
            log_status="есть" if log_exists else "отсутствует"
        )
    
    async def run(self):
        if not self.token:
            return
        
        logging.info("🌐 Starting inline bot...")
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        if hasattr(self, 'bot'):
            await self.bot.session.close()