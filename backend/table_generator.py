import pandas as pd
import re
from typing import Dict, List, Optional

class TableGenerator:
    # Generate pre-production tables from processed scenes.
    
    PRESETS = {
        'basic': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект / Подобект / Синопсис',
            'Персонажи',
            'Реквизит / Игровой транспорт / Животное'
        ],
        'extended': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект / Подобект / Синопсис',
            'Персонажи',
            'Массовка / Групповка',
            'Примечание / Графика',
            'Грим / Костюм',
            'Реквизит / Игровой транспорт / Животное',
            'Декорация',
            'Спецэффект / Администрация'
        ],
        'full': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект / Подобект / Синопсис',
            'Персонажи',
            'Массовка / Групповка',
            'Примечание / Графика',
            'Грим / Костюм',
            'Реквизит / Игровой транспорт / Животное',
            'Декорация',
            'Каскадер / Трюк',
            'Администрация / Спецэффект',
            'Операторская техника / LED-экраны'
        ]
    }
    
    def __init__(self):
        pass
    
    def map_element_to_column(self, column: str, scene_data: Dict) -> str:
        # Combined column for Объект / Подобект / Синопсис
        if column == 'Объект / Подобект / Синопсис':
            parts = []
            obj_val = scene_data.get('location_object')
            obj = str(obj_val).strip() if obj_val is not None else ''
            sub_obj_val = scene_data.get('location_sub_object')
            sub_obj = str(sub_obj_val).strip() if sub_obj_val is not None else ''
            text_val = scene_data.get('text')
            synopsis_text = str(text_val).strip() if text_val else ''
            
            if synopsis_text:
                synopsis_text = re.sub(r'^[0-9\-А-ЯЁa-zA-Z]+[\.\)]\s*', '', synopsis_text)
                synopsis_text = re.sub(r'^[А-ЯЁ\s\-\.]+[–\-]\s*[А-ЯЁ]+\.?\s*', '', synopsis_text)
                synopsis_text = synopsis_text[:300].strip()
                synopsis_text = re.sub(r'\s+', ' ', synopsis_text)
            
            if obj:
                parts.append(f"Объект: {obj}")
            if sub_obj:
                parts.append(f"Подобъект: {sub_obj}")
            if synopsis_text:
                parts.append(f"Синопсис: {synopsis_text}")
            
            return '\n'.join(parts) if parts else ''
        
        # Combined column for Массовка / Групповка
        if column == 'Массовка / Групповка':
            parts = []
            extras = scene_data.get('extras') or ''
            if extras:
                parts.append(f"Массовка: {extras}")
            return '\n'.join(parts) if parts else ''
        
        # Combined column for Реквизит / Игровой транспорт / Животное
        if column == 'Реквизит / Игровой транспорт / Животное':
            parts = []
            props = scene_data.get('props') or ''
            vehicles = scene_data.get('vehicles') or ''
            
            if props:
                parts.append(f"Реквизит: {props}")
            if vehicles:
                parts.append(f"Игровой транспорт: {vehicles}")
            
            return '\n'.join(parts) if parts else ''
        
        # Individual column mappings
        series_num = scene_data.get('series_number') or ''
        scene_num = scene_data.get('scene_number') or ''
        time_of_day = scene_data.get('time_of_day') or ''
        int_nat = scene_data.get('interior_exterior') or ''
        
        characters = scene_data.get('characters', '')
        if characters is None:
            characters = ''
        elif isinstance(characters, list):
            characters = ', '.join([str(c) for c in characters if c])
        else:
            characters = str(characters) if characters else ''
        
        column_mapping = {
            'Серия': str(series_num) if series_num else '',
            'Сцена': str(scene_num) if scene_num else '',
            'Режим': str(time_of_day) if time_of_day else '',
            'Инт / нат': str(int_nat) if int_nat else '',
            'Персонажи': characters,
            'Декорация': '', 
            'Каскадер / Трюк': '', 
        }
        
        return column_mapping.get(column, '')
    
    def generate(self, scenes_data: List[Dict], preset: str = 'basic', custom_columns: Optional[List[str]] = None) -> pd.DataFrame:
        if preset == 'custom' and custom_columns:
            columns = custom_columns.copy()
            if 'Серия' not in columns:
                columns.insert(0, 'Серия')
        elif preset in self.PRESETS:
            columns = self.PRESETS[preset]
        else:
            columns = self.PRESETS['basic']
        
        rows = []
        for scene_data in scenes_data:
            row = {}
            for column in columns:
                row[column] = self.map_element_to_column(column, scene_data)
            rows.append(row)
        
        df = pd.DataFrame(rows, columns=columns)
        return df

    
    def export_csv(self, df: pd.DataFrame, file_path: str, encoding: str = 'utf-8-sig'):
        """
        Export table to CSV.
        
        Args:
            df: DataFrame to export
            file_path: Output file path
            encoding: File encoding (default: utf-8-sig for Excel compatibility)
        """
        df.to_csv(file_path, index=False, encoding=encoding)
    
    def export_xlsx(self, df: pd.DataFrame, file_path: str):
        """
        Export table to XLSX.
        
        Args:
            df: DataFrame to export
            file_path: Output file path
        """
        df.to_excel(file_path, index=False, engine='openpyxl')

