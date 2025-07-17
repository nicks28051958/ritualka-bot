import os
import aiofiles
from datetime import datetime
from config import MEMORY_PAGES_DIR, TEMPLATES_DIR
from services.openai_service import OpenAIService

class MemoryService:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.html_template = self._load_html_template()
    
    def _load_html_template(self) -> str:
        """Загрузка HTML-шаблона"""
        template_path = os.path.join(TEMPLATES_DIR, "memory_template.html")
        
        if not os.path.exists(template_path):
            # Создаем базовый шаблон
            template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Памяти {{name}}</title>
    <style>
        body {
            font-family: 'Georgia', serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            margin: 0;
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }
        .name {
            font-size: 2.5em;
            margin: 0;
            font-weight: 300;
        }
        .dates {
            font-size: 1.2em;
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .photo-section {
            padding: 30px;
            text-align: center;
        }
        .photo {
            max-width: 300px;
            max-height: 300px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .memory-text {
            padding: 30px;
            line-height: 1.8;
            font-size: 1.1em;
            color: #333;
            text-align: justify;
        }
        .candles {
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            border-top: 1px solid #e9ecef;
        }
        .candle-count {
            font-size: 1.3em;
            color: #6c757d;
        }
        .candle-icon {
            font-size: 1.5em;
            margin: 0 5px;
        }
        .footer {
            background: #343a40;
            color: white;
            padding: 20px 30px;
            text-align: center;
            font-size: 0.9em;
        }
        @media (max-width: 600px) {
            .name { font-size: 2em; }
            .photo { max-width: 250px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="name">{{name}}</h1>
            <p class="dates">{{birth_date}} — {{death_date}}</p>
        </div>
        
        {% if photo_path %}
        <div class="photo-section">
            <img src="{{photo_path}}" alt="Фото {{name}}" class="photo">
        </div>
        {% endif %}
        
        <div class="memory-text">
            {{memory_text}}
        </div>
        
        <div class="candles">
            <div class="candle-count">
                <span class="candle-icon">🕯️</span>
                Зажжено свечей памяти: {{candles_count}}
                <span class="candle-icon">🕯️</span>
            </div>
        </div>
        
        <div class="footer">
            <p>Страница создана в память о дорогом человеке</p>
            <p>{{created_at}}</p>
        </div>
    </div>
</body>
</html>
            """
            
            os.makedirs(TEMPLATES_DIR, exist_ok=True)
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(template)
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    async def create_memory_page(self, record_id: int, name: str, birth_date: str, death_date: str, 
                                memory_text: str, photo_path: str = None, candles_count: int = 0) -> str:
        """Создание HTML-страницы памяти"""
        
        # Генерируем улучшенный текст с помощью AI
        enhanced_text = await self.openai_service.generate_memory_page_content(
            name, birth_date, death_date, memory_text
        )
        
        # Подготавливаем данные для шаблона
        template_data = {
            'name': name,
            'birth_date': birth_date,
            'death_date': death_date,
            'memory_text': enhanced_text,
            'photo_path': photo_path,
            'candles_count': candles_count,
            'created_at': datetime.now().strftime("%d.%m.%Y %H:%M")
        }
        
        # Заменяем плейсхолдеры в шаблоне
        html_content = self.html_template
        for key, value in template_data.items():
            if value is not None:
                html_content = html_content.replace(f'{{{{{key}}}}}', str(value))
            else:
                html_content = html_content.replace(f'{{{{{key}}}}}', '')
        
        # Создаем файл
        filename = f"memory_{record_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(MEMORY_PAGES_DIR, filename)
        
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            await f.write(html_content)
        
        return filepath
    
    async def get_memory_page_url(self, filepath: str) -> str:
        """Получение URL для страницы памяти"""
        # В реальном проекте здесь будет загрузка на веб-сервер
        # Пока возвращаем локальный путь
        return f"file://{os.path.abspath(filepath)}" 