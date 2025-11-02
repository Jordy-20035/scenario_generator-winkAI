"""
Improved element extraction module based on scaffold approach.
Uses keyword-based extraction with ALL CAPS character detection.
"""
import re
from typing import Dict, List, Optional, Any

# Regex for ALL CAPS detection (character names in scripts)
ALLCAP_RE = re.compile(r'^[A-ZА-ЯЁ\s\-]{2,}$')

# Keyword sets - extend these with larger gazetteers later
LOCATION_KEYWORDS = {
    "улица", "кабинет", "коридор", "зал", "кафе", "ресторан", "дом", 
    "площадь", "станция", "больница", "офис", "квартира", "комната",
    "парк", "сквер", "берег", "лед", "море", "океан", "пролив",
    "кают-компания", "каюткомпания", "палуба", "радиорубка", 
    "машинное отделение", "корабль", "судно", "пароход"
}

TIME_KEYWORDS = {
    "утро", "день", "вечер", "ночь", "рассвет", "сумерки", 
    "полдень", "ночью", "утром", "вечером", "дневное", "ночное"
}

MASS_KEYWORDS = {
    "толпа", "массовка", "зрители", "прохожие", "официанты", 
    "публика", "люди", "студенты", "экипаж", "челюскинцы"
}

PROP_KEYWORDS = {
    "автомобиль", "машина", "велосипед", "стол", "стул", "часы", 
    "пистолет", "телефон", "радио", "инструмент", "инструменты",
    "ноутбук", "компьютер", "деньги", "кошелек", "ключи", 
    "документы", "книга", "сигареты", "кольцо", "ружье"
}

VEHICLE_KEYWORDS = {
    "автомобиль", "машина", "авто", "такси", "автобус",
    "трамвай", "метро", "поезд", "мотоцикл"
}

SFX_KEYWORDS = {
    "взрыв", "пожар", "касание", "трюк", "каскадёр", 
    "пиротехника", "эффект", "CGI", "свет", "дым", "ветер",
    "снег", "молния", "дождь"
}

EQUIPMENT_KEYWORDS = {
    "коптер", "дрон", "камера", "объектив", "микрофон",
    "освещение", "подъемник", "кран", "хромакей", "хейзер"
}


class ElementExtractor:
    """Extract production elements using keyword-based approach."""
    
    def __init__(self):
        pass
    
    def normalize_word(self, word: str) -> str:
        """Normalize word for matching."""
        return word.strip().lower()
    
    def extract_characters(self, scene_text: str) -> List[str]:
        """
        Heuristic: lines in ALL CAPS often denote character names.
        Returns unique list in order of appearance.
        """
        names = []
        
        for line in scene_text.splitlines():
            s = line.strip()
            if not s or len(s) < 2:
                continue
            
            # Detect all-caps lines that are short (likely character headings)
            if ALLCAP_RE.match(s) and len(s.split()) <= 4:
                # Title case for readability
                names.append(s.title())
        
        # Remove duplicates while preserving order
        seen = set()
        out = []
        for n in names:
            if n.lower() not in seen:
                seen.add(n.lower())
                out.append(n)
        
        return out
    
    def extract_keywords_from_set(self, scene_text: str, keywords_set: set) -> List[str]:
        """Extract keywords from text by exact matching."""
        text_lower = scene_text.lower()
        found = []
        
        for kw in keywords_set:
            if kw in text_lower and kw not in found:
                found.append(kw)
        
        return found
    
    def extract_location(self, text: str) -> Dict[str, Optional[str]]:
        """Extract location (object and sub-object) from scene text."""
        object_location = None
        sub_object = None
        
        # Script format: "ЧЕЛЮСКИН. КАЮТ-КОМПАНИЯ – НОЧЬ"
        script_pattern = r'([А-ЯЁ][А-ЯЁ\s\-]+)\.\s*([А-ЯЁ][А-ЯЁ\s\-]+(?:\s*[–\-]\s*[А-ЯЁ\s]+)?)'
        script_match = re.search(script_pattern, text)
        if script_match:
            object_location = script_match.group(1).strip()
            sub_object = script_match.group(2).strip()
            # Remove time of day
            sub_object = re.sub(r'\s*[–\-]\s*(ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР)', '', sub_object, flags=re.IGNORECASE)
            return {
                'object': object_location,
                'sub_object': sub_object if sub_object else None
            }
        
        # Look for location keywords
        locs = self.extract_keywords_from_set(text, LOCATION_KEYWORDS)
        
        # Check for ship names (common in scripts)
        ship_match = re.search(r'\b(ЧЕЛЮСКИН|КОРАБЛЬ|СУДНО|ПАРОХОД)\b', text, re.IGNORECASE)
        if ship_match:
            object_location = ship_match.group(1)
        
        # Room types become sub_object if we have object, otherwise object
        for loc in locs:
            if not object_location:
                object_location = loc.capitalize()
            else:
                sub_object = loc.capitalize()
                break
        
        return {
            'object': object_location,
            'sub_object': sub_object
        }
    
    def extract_time_of_day(self, text: str) -> Optional[str]:
        """Extract time of day from scene text."""
        times = self.extract_keywords_from_set(text, TIME_KEYWORDS)
        
        # Priority mapping
        priority = {'ночь': 'Ночь', 'ночное': 'Ночь', 'ночью': 'Ночь',
                   'день': 'День', 'дневное': 'День',
                   'утро': 'Утро', 'утреннее': 'Утро', 'утром': 'Утро',
                   'вечер': 'Вечер', 'вечернее': 'Вечер', 'вечером': 'Вечер'}
        
        for time in times:
            if time in priority:
                return priority[time]
        
        # Return first found or None
        return times[0].capitalize() if times else None
    
    def extract_interior_exterior(self, text: str) -> Optional[str]:
        """Determine if scene is interior or exterior."""
        text_lower = text.lower()
        
        interior_keywords = ['кабинет', 'комната', 'дом', 'квартира', 'офис', 'клуб', 
                           'кафе', 'ресторан', 'кают-компания', 'радиорубка']
        exterior_keywords = ['улица', 'площадь', 'парк', 'сквер', 'на улице', 
                           'на площади', 'берег', 'море', 'лед']
        
        for kw in interior_keywords:
            if kw in text_lower:
                return 'Инт'
        
        for kw in exterior_keywords:
            if kw in text_lower:
                return 'Нат'
        
        return None
    
    def extract_all(self, text: str) -> Dict[str, Any]:
        """Extract all production elements from scene text."""
        location = self.extract_location(text)
        characters = self.extract_characters(text)
        
        # Main vs secondary (first 3 are main)
        main_chars = characters[:3]
        secondary_chars = characters[3:]
        
        props = self.extract_keywords_from_set(text, PROP_KEYWORDS)
        vehicles = self.extract_keywords_from_set(text, VEHICLE_KEYWORDS)
        sfx = self.extract_keywords_from_set(text, SFX_KEYWORDS)
        equipment = self.extract_keywords_from_set(text, EQUIPMENT_KEYWORDS)
        has_mass = bool(self.extract_keywords_from_set(text, MASS_KEYWORDS))
        
        return {
            'time_of_day': self.extract_time_of_day(text),
            'interior_exterior': self.extract_interior_exterior(text),
            'location_object': location['object'],
            'location_sub_object': location['sub_object'],
            'characters': main_chars + secondary_chars,  # Combined list
            'extras': f"Массовка: {', '.join(self.extract_keywords_from_set(text, MASS_KEYWORDS))}" if has_mass else None,
            'props': ', '.join(props) if props else None,
            'vehicles': ', '.join(vehicles) if vehicles else None,
            'special_effects': ', '.join(sfx) if sfx else None,
            'equipment': ', '.join(equipment) if equipment else None,
        }

