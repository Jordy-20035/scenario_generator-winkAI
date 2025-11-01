"""
NLP-based extraction module for production elements.
Extracts: locations, time of day, characters, extras, props, vehicles,
makeup, costumes, special effects, stunts, pyrotechnics, special equipment.
"""
import re
import spacy
from typing import Dict, List, Optional
from natasha import (
    Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger,
    NewsNERTagger, Doc
)
import razdel


class ElementExtractor:
    """Extract production elements from scene text using NLP."""
    
    def __init__(self):
        # Load spaCy Russian model
        try:
            self.nlp = spacy.load("ru_core_news_sm")
        except OSError:
            print("Warning: ru_core_news_sm not found. Install with: python -m spacy download ru_core_news_sm")
            self.nlp = None
        
        # Initialize Natasha components for better Russian NLP
        self.segmenter = Segmenter()
        self.morph_vocab = MorphVocab()
        emb = NewsEmbedding()
        self.morph_tagger = NewsMorphTagger(emb)
        self.ner_tagger = NewsNERTagger(emb)
        
        # Keywords and patterns for extraction
        self._init_keywords()
    
    def _init_keywords(self):
        """Initialize keyword dictionaries for extraction."""
        # Time of day keywords
        self.time_keywords = {
            'день': 'День',
            'дневное': 'День',
            'утро': 'Утро',
            'утреннее': 'Утро',
            'вечер': 'Вечер',
            'вечернее': 'Вечер',
            'ночь': 'Ночь',
            'ночное': 'Ночь',
            'ночью': 'Ночь',
            'рассвет': 'Утро',
            'закат': 'Вечер'
        }
        
        # Location indicators
        self.location_indicators = [
            'в', 'на', 'у', 'около', 'возле', 'около',
            'кабинет', 'офис', 'комната', 'дом', 'квартира',
            'улица', 'площадь', 'парк', 'кафе', 'ресторан',
            'машина', 'автомобиль', 'метро', 'поезд'
        ]
        
        # Character name patterns (capitalized words, typically at sentence start)
        self.character_pattern = re.compile(r'\b([А-ЯЁ][а-яё]+)\s+(?:говорит|сказал|смотрит|идет|делает)')
        
        # Props keywords
        self.props_keywords = [
            'телефон', 'ноутбук', 'компьютер', 'деньги', 'кошелек',
            'ключи', 'документы', 'книга', 'газета', 'листы',
            'ручка', 'карандаш', 'бумага', 'папка', 'портфель',
            'сумка', 'шаурма', 'чипсы', 'напиток', 'вино',
            'животное', 'собака', 'кошка'
        ]
        
        # Vehicle keywords
        self.vehicle_keywords = [
            'автомобиль', 'машина', 'авто', 'такси', 'автобус',
            'трамвай', 'метро', 'поезд', 'мотоцикл', 'велосипед'
        ]
        
        # Special effects keywords
        self.sfx_keywords = [
            'спецэффект', 'эффект', 'дым', 'огонь', 'взрыв',
            'свет', 'молния', 'дождь', 'снег', 'ветер'
        ]
        
        # Equipment keywords
        self.equipment_keywords = [
            'коптер', 'дрон', 'камера', 'объектив', 'микрофон',
            'освещение', 'подъемник', 'кран'
        ]
        
        # Extras/crowd indicators
        self.extras_indicators = [
            'массовка', 'толпа', 'люди', 'студенты', 'прохожие',
            'официанты', 'гости', 'зрители', 'толпа людей'
        ]
    
    def extract_time_of_day(self, text: str) -> Optional[str]:
        """Extract time of day from scene text."""
        text_lower = text.lower()
        
        for keyword, time in self.time_keywords.items():
            if keyword in text_lower:
                return time
        
        return None
    
    def extract_location(self, text: str) -> Dict[str, Optional[str]]:
        """Extract location (object and sub-object) from scene text."""
        # Use Natasha for NER to find location names
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.tag_ner(self.ner_tagger)
        
        locations = []
        for span in doc.spans:
            if span.type == 'LOC':  # Location entity
                locations.append(span.text)
        
        # Also look for location keywords
        text_lower = text.lower()
        location_parts = []
        
        # Common location patterns
        location_patterns = [
            r'([А-ЯЁ][а-яё]+(?:\s+[А-ЯЁ][а-яё]+)*)\s*[\.:]',  # City names followed by punctuation
            r'(кабинет|офис|комната|дом|квартира|клуб|кафе|ресторан)',
            r'(улица|площадь|парк|сквер)',
            r'([А-ЯЁ][а-яё]+\s+ул\.)',  # Street names
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            location_parts.extend(matches)
        
        object_location = None
        sub_object = None
        
        if locations:
            object_location = locations[0] if len(locations) > 0 else None
            sub_object = locations[1] if len(locations) > 1 else None
        
        if location_parts and not object_location:
            object_location = location_parts[0]
            if len(location_parts) > 1:
                sub_object = location_parts[1]
        
        return {
            'object': object_location,
            'sub_object': sub_object
        }
    
    def extract_characters(self, text: str) -> List[str]:
        """Extract character names from scene text."""
        characters = set()
        
        # Use NER to find person names
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PER":  # Person entity
                    characters.add(ent.text)
        
        # Also use Natasha NER
        doc = Doc(text)
        doc.segment(self.segmenter)
        doc.tag_morph(self.morph_tagger)
        doc.tag_ner(self.ner_tagger)
        
        for span in doc.spans:
            if span.type == 'PER':  # Person entity
                characters.add(span.text)
        
        # Pattern-based extraction (capitalized names at sentence start)
        matches = self.character_pattern.findall(text)
        characters.update(matches)
        
        return sorted(list(characters))
    
    def extract_extras(self, text: str) -> Optional[str]:
        """Extract extras/crowd information."""
        text_lower = text.lower()
        extras_list = []
        
        for indicator in self.extras_indicators:
            if indicator in text_lower:
                # Try to extract count
                pattern = rf'{indicator}.*?\((\d+)\)'
                match = re.search(pattern, text, re.IGNORECASE)
                count = match.group(1) if match else "?"
                
                extras_list.append(f"{indicator.capitalize()} ({count})")
        
        if extras_list:
            return ", ".join(extras_list)
        
        return None
    
    def extract_props(self, text: str) -> Optional[str]:
        """Extract props from scene text."""
        text_lower = text.lower()
        props_list = []
        
        for keyword in self.props_keywords:
            pattern = rf'\b{re.escape(keyword)}\w*'
            if re.search(pattern, text_lower):
                # Get full word/phrase
                match = re.search(rf'\b{keyword}\w*(?:\s+\w+)*', text, re.IGNORECASE)
                if match:
                    props_list.append(match.group(0))
        
        if props_list:
            return ", ".join(props_list)
        
        return None
    
    def extract_vehicles(self, text: str) -> Optional[str]:
        """Extract vehicles/transport."""
        text_lower = text.lower()
        vehicles_list = []
        
        for keyword in self.vehicle_keywords:
            pattern = rf'\b{re.escape(keyword)}\w*'
            if re.search(pattern, text_lower):
                match = re.search(rf'\b{keyword}\w*(?:\s+\w+)*', text, re.IGNORECASE)
                if match:
                    vehicles_list.append(match.group(0))
        
        if vehicles_list:
            return ", ".join(vehicles_list)
        
        return None
    
    def extract_special_effects(self, text: str) -> Optional[str]:
        """Extract special effects."""
        text_lower = text.lower()
        sfx_list = []
        
        for keyword in self.sfx_keywords:
            if keyword in text_lower:
                sfx_list.append(keyword.capitalize())
        
        if sfx_list:
            return ", ".join(sfx_list)
        
        return None
    
    def extract_equipment(self, text: str) -> Optional[str]:
        """Extract special equipment."""
        text_lower = text.lower()
        equipment_list = []
        
        for keyword in self.equipment_keywords:
            pattern = rf'\b{re.escape(keyword)}\w*'
            if re.search(pattern, text_lower):
                # Try to extract with count
                pattern_count = rf'{keyword}.*?\((\d+)\)'
                match = re.search(pattern_count, text, re.IGNORECASE)
                if match:
                    equipment_list.append(f"{keyword} ({match.group(1)})")
                else:
                    equipment_list.append(keyword)
        
        if equipment_list:
            return ", ".join(equipment_list)
        
        return None
    
    def extract_interior_exterior(self, text: str) -> Optional[str]:
        """Determine if scene is interior or exterior."""
        text_lower = text.lower()
        
        interior_keywords = ['кабинет', 'комната', 'дом', 'квартира', 'офис', 'клуб', 'кафе', 'ресторан']
        exterior_keywords = ['улица', 'площадь', 'парк', 'сквер', 'на улице', 'на площади']
        
        for keyword in interior_keywords:
            if keyword in text_lower:
                return 'Инт'
        
        for keyword in exterior_keywords:
            if keyword in text_lower:
                return 'Нат'
        
        return None
    
    def extract_all(self, text: str) -> Dict:
        """
        Extract all production elements from scene text.
        
        Args:
            text: Scene text
        
        Returns:
            Dictionary with all extracted elements
        """
        location = self.extract_location(text)
        
        return {
            'time_of_day': self.extract_time_of_day(text),
            'interior_exterior': self.extract_interior_exterior(text),
            'location_object': location['object'],
            'location_sub_object': location['sub_object'],
            'characters': self.extract_characters(text),
            'extras': self.extract_extras(text),
            'props': self.extract_props(text),
            'vehicles': self.extract_vehicles(text),
            'special_effects': self.extract_special_effects(text),
            'equipment': self.extract_equipment(text),
        }

