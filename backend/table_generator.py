"""
Table generator module.
Creates structured pre-production tables with customizable column presets.
"""
import pandas as pd
from typing import List, Dict, Optional


class TableGenerator:
    """Generate pre-production tables from processed scenes."""
    
    # Column presets
    PRESETS = {
        'basic': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект',
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
            'Персонажи',
            'Массовка',
            'Реквизит',
            'Игровой транспорт',
            'Грим',
            'Костюм',
            'Спецэффект',
            'Спец. оборудование'
        ],
        'full': [
            'Серия',
            'Сцена',
            'Режим',
            'Инт / нат',
            'Объект',
            'Подобъект',
            'Синопсис',
            'Персонажи',
            'Массовка',
            'Групповка',
            'Грим',
            'Костюм',
            'Реквизит',
            'Игровой транспорт',
            'Декорация',
            'Пиротехника',
            'Каскадер / Трюк',
            'Музыка',
            'Спецэффект',
            'Спец. оборудование'
        ]
    }
    
    def __init__(self):
        pass
    
    def map_element_to_column(self, column: str, scene_data: Dict) -> str:
        """Map extracted elements to table columns."""
        column_mapping = {
            'Серия': '',  # Usually needs manual input or extraction from scene number
            'Сцена': scene_data.get('scene_number', ''),
            'Режим': scene_data.get('time_of_day', ''),
            'Инт / нат': scene_data.get('interior_exterior', ''),
            'Объект': scene_data.get('location_object', ''),
            'Подобъект': scene_data.get('location_sub_object', ''),
            'Синопсис': scene_data.get('text', '')[:200] if 'text' in scene_data else '',  # First 200 chars
            'Персонажи': ', '.join(scene_data.get('characters', [])) if isinstance(scene_data.get('characters'), list) else scene_data.get('characters', ''),
            'Массовка': scene_data.get('extras', ''),
            'Групповка': '',  # May need special extraction
            'Грим': '',  # Needs special extraction
            'Костюм': '',  # Needs special extraction
            'Реквизит': scene_data.get('props', ''),
            'Игровой транспорт': scene_data.get('vehicles', ''),
            'Декорация': '',  # May need special extraction
            'Пиротехника': '',  # May need special extraction
            'Каскадер / Трюк': '',  # May need special extraction
            'Музыка': '',  # May need special extraction
            'Спецэффект': scene_data.get('special_effects', ''),
            'Спец. оборудование': scene_data.get('equipment', ''),
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
            columns = custom_columns
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

