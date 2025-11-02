"""
NLP-based extraction module for production elements.
Extracts: locations, time of day, characters, extras, props, vehicles,
makeup, costumes, special effects, stunts, pyrotechnics, special equipment.
"""
import re
import spacy
from typing import Dict, List, Optional

# Try to import natasha - make it optional
try:
    from natasha import (
        Segmenter, MorphVocab, NewsEmbedding, NewsMorphTagger,
        NewsNERTagger, Doc
    )
    NATASHA_AVAILABLE = True
except ImportError:
    NATASHA_AVAILABLE = False
    print("Warning: natasha not available. Some features may be limited.")

try:
    import razdel
    RAZDEL_AVAILABLE = True
except ImportError:
    RAZDEL_AVAILABLE = False
    print("Warning: razdel not available.")


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
        self.natasha_available = NATASHA_AVAILABLE
        if NATASHA_AVAILABLE:
            try:
                self.segmenter = Segmenter()
                self.morph_vocab = MorphVocab()
                emb = NewsEmbedding()
                self.morph_tagger = NewsMorphTagger(emb)
                self.ner_tagger = NewsNERTagger(emb)
            except Exception as e:
                print(f"Warning: Failed to initialize Natasha: {e}")
                self.natasha_available = False
                self.segmenter = None
                self.morph_vocab = None
                self.morph_tagger = None
                self.ner_tagger = None
        else:
            self.segmenter = None
            self.morph_vocab = None
            self.morph_tagger = None
            self.ner_tagger = None
        
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
        object_location = None
        sub_object = None
        
        # Script format patterns (e.g., "ЧЕЛЮСКИН. КАЮТ-КОМПАНИЯ – НОЧЬ")
        # Look for ALL CAPS location names followed by period and sub-location
        script_pattern = r'([А-ЯЁ][А-ЯЁ\s\-]+)\.\s*([А-ЯЁ][А-ЯЁ\s\-]+(?:\s*[–\-]\s*[А-ЯЁ\s]+)?)'
        script_match = re.search(script_pattern, text)
        if script_match:
            object_location = script_match.group(1).strip()
            sub_object = script_match.group(2).strip()
            # Remove time of day from sub_object if present
            sub_object = re.sub(r'\s*[–\-]\s*(ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР|ДЕНЬ|НОЧЬ|УТРО|ВЕЧЕР)', '', sub_object, flags=re.IGNORECASE)
            return {
                'object': object_location,
                'sub_object': sub_object if sub_object else None
            }
        
        # Pattern for "Объект: X. Подобъект: Y" format (sometimes appears in parsed text)
        explicit_pattern = r'Объект[:\s]+([^\.]+)\.?\s*(?:Подобъект[:\s]+([^\.]+))?'
        explicit_match = re.search(explicit_pattern, text, re.IGNORECASE)
        if explicit_match:
            object_location = explicit_match.group(1).strip()
            if explicit_match.group(2):
                sub_object = explicit_match.group(2).strip()
            return {
                'object': object_location,
                'sub_object': sub_object
            }
        
        # Look for location keywords (ship names, room types, etc.)
        text_upper = text.upper()
        
        # Ship/object names (common in scripts)
        ship_patterns = [
            r'\b(ЧЕЛЮСКИН|КОРАБЛЬ|СУДНО|ПАРОХОД)\b',
            r'\b([А-ЯЁ]+)\s+(?:КОРАБЛЬ|СУДНО|ПАРОХОД)\b',
        ]
        
        for pattern in ship_patterns:
            match = re.search(pattern, text_upper)
            if match:
                object_location = match.group(1) if match.lastindex else match.group(0)
                break
        
        # Room/location types (кают-компания, кабинет, палуба, etc.)
        room_patterns = [
            r'(кают-компания|каюткомпания|кабинет|палуба|радиорубка|машинное отделение)',
            r'(офис|комната|зал|коридор|кафе|ресторан)',
            r'(берег|лед|море|океан|пролив)',
        ]
        
        for pattern in room_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # If we have object, this is sub_object; otherwise it's object
                if not object_location:
                    object_location = matches[0].capitalize()
                else:
                    sub_object = matches[0].capitalize()
                    break
        
        # Geographic locations (cities, regions) - but only if no other location found
        if not object_location:
            # Use Natasha NER for locations only as fallback
            if self.natasha_available and self.segmenter and self.morph_tagger and self.ner_tagger:
                try:
                    doc = Doc(text)
                    doc.segment(self.segmenter)
                    doc.tag_morph(self.morph_tagger)
                    doc.tag_ner(self.ner_tagger)
                    
                    # Filter out common false positives
                    excluded = {'земли', 'земля', 'земле', 'землю', 'сома', 'сомову', 'сомова'}
                    for span in doc.spans:
                        if span.type == 'LOC' and span.text.lower() not in excluded:
                            object_location = span.text
                            break
                except Exception as e:
                    pass  # Silently fail if Natasha not available
        
        return {
            'object': object_location if object_location else None,
            'sub_object': sub_object if sub_object else None
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
        
        # Also use Natasha NER if available
        if self.natasha_available and self.segmenter and self.morph_tagger and self.ner_tagger:
            try:
                doc = Doc(text)
                doc.segment(self.segmenter)
                doc.tag_morph(self.morph_tagger)
                doc.tag_ner(self.ner_tagger)
                
                for span in doc.spans:
                    if span.type == 'PER':  # Person entity
                        characters.add(span.text)
            except Exception as e:
                print(f"Warning: Natasha NER failed: {e}")
        
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

