"""
Table generator module.
Creates structured pre-production tables with customizable column presets.
"""
import pandas as pd
import re
from typing import Dict, List, Optional


class TableGenerator:
    """Generate pre-production tables from processed scenes."""
    
    # Column presets - matching exact template structure
    PRESETS = {
        'basic': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект / Подобъект / Синопсис',
            'Персонажи',
            'Реквизит / Игровой транспорт / Животное'
        ],
        'extended': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект / Подобъект / Синопсис',
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
            'Объект / Подобъект / Синопсис',
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
        """Map extracted elements to table columns."""
        
        # Combined column for Объект / Подобъект / Синопсис
        if column == 'Объект / Подобъект / Синопсис':
            parts = []
            obj = scene_data.get('location_object', '').strip()
            sub_obj = scene_data.get('location_sub_object', '').strip()
            synopsis_text = scene_data.get('text', '').strip() if 'text' in scene_data else ''
            
            # Clean up synopsis - remove scene headers and formatting
            if synopsis_text:
                # Remove scene number patterns at the start
                synopsis_text = re.sub(r'^[0-9\-А-ЯЁa-zA-Z]+[\.\)]\s*', '', synopsis_text)
                # Remove script format headers like "ЧЕЛЮСКИН. КАЮТ-КОМПАНИЯ – НОЧЬ"
                synopsis_text = re.sub(r'^[А-ЯЁ\s\-\.]+[–\-]\s*[А-ЯЁ]+\.?\s*', '', synopsis_text)
                # Limit to first 300 characters and clean up
                synopsis_text = synopsis_text[:300].strip()
                # Remove extra whitespace
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
            extras = scene_data.get('extras', '')
            if extras:
                parts.append(f"Массовка: {extras}")
            # Групповка would need special extraction - leaving empty for now
            return '\n'.join(parts) if parts else ''
        
        # Combined column for Примечание / Графика
        if column == 'Примечание / Графика':
            # These would need special extraction from text
            return ''
        
        # Combined column for Грим / Костюм
        if column == 'Грим / Костюм':
            # These would need special extraction from text
            return ''
        
        # Combined column for Реквизит / Игровой транспорт / Животное
        if column == 'Реквизит / Игровой транспорт / Животное':
            parts = []
            props = scene_data.get('props', '')
            vehicles = scene_data.get('vehicles', '')
            # Животное would need special extraction
            
            if props:
                parts.append(f"Реквизит: {props}")
            if vehicles:
                parts.append(f"Игровой транспорт: {vehicles}")
            
            return '\n'.join(parts) if parts else ''
        
        # Combined column for Администрация / Спецэффект
        if column == 'Администрация / Спецэффект' or column == 'Спецэффект / Администрация':
            parts = []
            sfx = scene_data.get('special_effects', '')
            # Администрация would need special extraction
            
            if sfx:
                parts.append(f"Спецэффект: {sfx}")
            
            return '\n'.join(parts) if parts else ''
        
        # Combined column for Операторская техника / LED-экраны
        if column == 'Операторская техника / LED-экраны':
            equipment = scene_data.get('equipment', '')
            if equipment:
                return f"Операторская техника: {equipment}"
            return ''
        
        # Individual column mappings
        column_mapping = {
            'Серия': scene_data.get('series_number', ''),
            'Сцена': scene_data.get('scene_number', ''),
            'Режим': scene_data.get('time_of_day', ''),
            'Инт / нат': scene_data.get('interior_exterior', ''),
            'Персонажи': ', '.join(scene_data.get('characters', [])) if isinstance(scene_data.get('characters'), list) else scene_data.get('characters', ''),
            'Декорация': '',  # Would need special extraction
            'Каскадер / Трюк': '',  # Would need special extraction
        }
        
        return column_mapping.get(column, '')
    
    def generate(
        self,
        scenes_data: List[Dict],
        preset: str = 'basic',
        custom_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Generate pre-production table.
        
        Args:
            scenes_data: List of processed scene dictionaries
            preset: Preset name ('basic', 'extended', 'full') or 'custom'
            custom_columns: List of column names for custom preset
        
        Returns:
            pandas DataFrame with the table
        """
        # Get columns based on preset
        if preset == 'custom' and custom_columns:
            columns = custom_columns.copy()
            # Always ensure Серия column is included if processing multiple files
            if 'Серия' not in columns:
                columns.insert(0, 'Серия')
        elif preset in self.PRESETS:
            columns = self.PRESETS[preset]
        else:
            # Default to basic if preset not found
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

