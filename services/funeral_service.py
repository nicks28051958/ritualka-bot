from typing import Dict, List, Optional

class FuneralService:
    def __init__(self):
        self.packages = self._init_packages()
    
    def _init_packages(self) -> Dict[str, Dict]:
        """Инициализация пакетов услуг"""
        return {
            "basic_traditional": {
                "name": "Базовый пакет (Традиционные похороны)",
                "description": "Включает: транспортировку, оформление документов, гроб стандартный, венок, зал прощания",
                "price": 25000,
                "services": ["transport", "documents", "coffin", "wreaths", "hall"],
                "funeral_type": "traditional",
                "budget": "less_30k"
            },
            "premium_traditional": {
                "name": "Премиум пакет (Традиционные похороны)",
                "description": "Включает: транспортировку, оформление документов, гроб премиум, венки, зал прощания, отпевание, музыка",
                "price": 45000,
                "services": ["transport", "documents", "coffin", "wreaths", "hall", "service", "music"],
                "funeral_type": "traditional",
                "budget": "30k_60k"
            },
            "luxury_traditional": {
                "name": "Люкс пакет (Традиционные похороны)",
                "description": "Включает: все услуги + премиум гроб, цветы, расширенное отпевание",
                "price": 75000,
                "services": ["transport", "documents", "coffin", "wreaths", "hall", "service", "music", "flowers"],
                "funeral_type": "traditional",
                "budget": "more_60k"
            },
            "basic_cremation": {
                "name": "Базовый пакет (Кремация)",
                "description": "Включает: транспортировку, оформление документов, урну стандартную",
                "price": 20000,
                "services": ["transport", "documents"],
                "funeral_type": "cremation",
                "budget": "less_30k"
            },
            "premium_cremation": {
                "name": "Премиум пакет (Кремация)",
                "description": "Включает: транспортировку, оформление документов, урну премиум, зал прощания",
                "price": 35000,
                "services": ["transport", "documents", "hall"],
                "funeral_type": "cremation",
                "budget": "30k_60k"
            },
            "luxury_cremation": {
                "name": "Люкс пакет (Кремация)",
                "description": "Включает: все услуги + премиум урна, отпевание, музыка",
                "price": 55000,
                "services": ["transport", "documents", "hall", "service", "music"],
                "funeral_type": "cremation",
                "budget": "more_60k"
            }
        }
    
    def select_package(self, funeral_type: str, services: List[str], budget: str) -> Optional[Dict]:
        """Подбор пакета услуг на основе анкеты"""
        
        # Фильтруем пакеты по типу похорон
        suitable_packages = [
            pkg for pkg_id, pkg in self.packages.items()
            if pkg["funeral_type"] == funeral_type
        ]
        
        if not suitable_packages:
            return None
        
        # Оцениваем соответствие услуг
        best_package = None
        best_score = 0
        
        for package in suitable_packages:
            score = 0
            
            # Проверяем соответствие бюджета
            if package["budget"] == budget:
                score += 3
            elif (budget == "less_30k" and package["budget"] == "30k_60k") or \
                 (budget == "more_60k" and package["budget"] == "30k_60k"):
                score += 1
            
            # Проверяем соответствие услуг
            package_services = set(package["services"])
            user_services = set(services)
            
            # За каждую совпадающую услугу +1 балл
            score += len(package_services.intersection(user_services))
            
            # За каждую лишнюю услугу в пакете +0.5 балла
            score += len(package_services - user_services) * 0.5
            
            if score > best_score:
                best_score = score
                best_package = package
        
        return best_package
    
    def get_package_details(self, package_id: str) -> Optional[Dict]:
        """Получение деталей пакета по ID"""
        return self.packages.get(package_id)
    
    def get_all_packages(self) -> Dict[str, Dict]:
        """Получение всех пакетов"""
        return self.packages
    
    def format_package_message(self, package: Dict) -> str:
        """Форматирование сообщения с пакетом"""
        services_map = {
            "transport": "🚚 Транспортировка",
            "documents": "📋 Оформление документов",
            "service": "⛪ Отпевание",
            "coffin": "⚰️ Гроб",
            "wreaths": "💐 Венки",
            "music": "🎵 Музыка",
            "hall": "🏛️ Зал прощания",
            "flowers": "🌹 Цветы"
        }
        
        services_text = "\n".join([f"• {services_map.get(service, service)}" for service in package["services"]])
        
        return f"""
📦 **{package['name']}**

{package['description']}

💰 **Стоимость:** {package['price']:,} ₽

📋 **Включенные услуги:**
{services_text}

Для оформления заказа нажмите кнопку ниже.
        """.strip() 