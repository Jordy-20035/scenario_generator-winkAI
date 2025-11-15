import pandas as pd
import re
from typing import Dict, List, Optional

class TableGenerator:
    """Generate pre-production tables from processed scenes."""
    
    # Column presets - matching updated template structure
    PRESETS = {
        'basic': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект',
            'Подобъект',
            'Синопсис',
            'Персонажи',
            'Реквизит'
        ],
        'extended': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект',
            'Подобъект',
            'Синопсис',
            'Время года',
            'Персонажи',
            'Массовка',
            'Грим',
            'Костюм',
            'Реквизит',
            'Игровой транспорт',
            'Трюк',
            'Животные'
        ],
        'full': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект',
            'Подобъект',
            'Синопсис',
            'Время года',
            'Персонажи',
            'Массовка',
            'Грим',
            'Костюм',
            'Реквизит',
            'Игровой транспорт',
            'Трюк',
            'Животные'
        ]
    }
    
    def __init__(self):
        pass
    
    def map_element_to_column(self, column: str, scene_data: Dict) -> str:
        """Map extracted elements to table columns."""
        
        # Safely handle None values
        def safe_str(value):
            if value is None:
                return ''
            return str(value).strip() if value else ''
        
        # Basic fields
        series_num = safe_str(scene_data.get('series_number'))
        scene_num = safe_str(scene_data.get('scene_number'))
        time_of_day = safe_str(scene_data.get('time_of_day'))
        int_nat = safe_str(scene_data.get('interior_exterior'))
        
        # Location columns (now separate)
        obj_val = scene_data.get('location_object')
        obj = safe_str(obj_val)
        sub_obj_val = scene_data.get('location_sub_object')
        sub_obj = safe_str(sub_obj_val)
        
        # Synopsis (now separate column)
        text_val = scene_data.get('text')
        synopsis_text = safe_str(text_val)
        if synopsis_text:
            # Clean up synopsis - remove scene headers and formatting
            synopsis_text = re.sub(r'^[0-9\-А-ЯЁa-zA-Z]+[\.\)]\s*', '', synopsis_text)
            synopsis_text = re.sub(r'^[А-ЯЁ\s\-\.]+[–\-]\s*[А-ЯЁ]+\.?\s*', '', synopsis_text)
            synopsis_text = synopsis_text[:300].strip()
            synopsis_text = re.sub(r'\s+', ' ', synopsis_text)
        
        # Characters
        characters = scene_data.get('characters', '')
        if characters is None:
            characters = ''
        elif isinstance(characters, list):
            characters = ', '.join([str(c) for c in characters if c])
        else:
            characters = str(characters) if characters else ''
        
        # Extras/Massovka (extract from extras field, remove prefix if present)
        extras = scene_data.get('extras') or ''
        if extras.startswith('Массовка:'):
            extras = extras.replace('Массовка:', '').strip()
        elif extras.startswith('Массовка'):
            extras = extras.replace('Массовка', '').strip()
        
        # Props, vehicles (now separate columns)
        props = safe_str(scene_data.get('props'))
        vehicles = safe_str(scene_data.get('vehicles'))
        
        # Animals - use extracted animals field
        animals = safe_str(scene_data.get('animals'))
        
        # Stunt/Trick - use extracted stunt field
        stunt = safe_str(scene_data.get('stunt'))
        
        # Makeup and Costume (will need special extraction later)
        makeup = ''
        costume = ''
        
        # Time of year (new column - will need special extraction)
        time_of_year = ''
        
        column_mapping = {
            'Серия': series_num,
            'Сцена': scene_num,
            'Режим': time_of_day,
            'Инт / нат': int_nat,
            'Объект': obj,
            'Подобъект': sub_obj,
            'Синопсис': synopsis_text,
            'Время года': time_of_year,
            'Персонажи': characters,
            'Массовка': extras,
            'Грим': makeup,
            'Костюм': costume,
            'Реквизит': props,
            'Игровой транспорт': vehicles,
            'Трюк': stunt,
            'Животные': animals,
        }
        
        return column_mapping.get(column, '')
    
    def generate(self, scenes_data: List[Dict], preset: str = 'basic', custom_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Generate pre-production table."""
        # Get columns based on preset
        if preset == 'custom' and custom_columns:
            columns = custom_columns.copy()
            # Always ensure Серия column is included first
            if 'Серия' not in columns:
                columns.insert(0, 'Серия')
        elif preset in self.PRESETS:
            columns = self.PRESETS[preset]
        else:
            columns = self.PRESETS['basic']
        
        # Create rows for each scene
        rows = []
        for scene_data in scenes_data:
            row = {}
            for column in columns:
                row[column] = self.map_element_to_column(column, scene_data)
            rows.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=columns)
        return df
    
    def export_csv(self, df: pd.DataFrame, file_path: str, encoding: str = 'utf-8-sig'):
        """Export table to CSV."""
        df.to_csv(file_path, index=False, encoding=encoding)
    
    def export_xlsx(self, df: pd.DataFrame, file_path: str):
        """Export table to XLSX."""
        df.to_excel(file_path, index=False, engine='openpyxl')
