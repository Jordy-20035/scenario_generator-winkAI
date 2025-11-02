"""
Streamlit frontend for Scenario Pre-Production Generator.
"""
import streamlit as st
import pandas as pd
import requests
import json
import os
from io import BytesIO
import time
import re

# Page config
st.set_page_config(
    page_title="Scenario Pre-Production Generator",
    page_icon="🎬",
    layout="wide"
)

# API endpoint
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Initialize session state
if 'processed_scenes' not in st.session_state:
    st.session_state.processed_scenes = None
if 'table_data' not in st.session_state:
    st.session_state.table_data = None
if 'selected_preset' not in st.session_state:
    st.session_state.selected_preset = 'basic'
if 'use_custom' not in st.session_state:
    st.session_state.use_custom = False
if 'selected_columns' not in st.session_state:
    st.session_state.selected_columns = None

# Available presets
PRESETS = {
    'basic': 'Базовый',
    'extended': 'Расширенный',
    'full': 'Полный'
}

# All available columns
ALL_COLUMNS = [
    'Серия', 'Сцена', 'Режим', 'Инт / нат', 'Объект', 'Подобъект',
    'Синопсис', 'Персонажи', 'Массовка', 'Групповка', 'Грим', 'Костюм',
    'Реквизит', 'Игровой транспорт', 'Декорация', 'Пиротехника',
    'Каскадер / Трюк', 'Музыка', 'Спецэффект', 'Спец. оборудование'
]


def extract_series_number(filename: str) -> str:
    """
    Extract series number from filename.
    Examples:
    - ЧЕЛЮСКИН_1c_15.08_ФИНАЛ -> "1"
    - ЧЕЛЮСКИН_2C_15.08_ФИНАЛ -> "2"
    - ЧЕЛЮСКИН_ЗС_05.09_ФИНАЛ -> "3" (Cyrillic З = 3)
    """
    # Try to find number after underscore (pattern: _Xc or _XC)
    patterns = [
        r'_(\d+)[cCсС]',  # _1c, _2C, _1с, _2С
        r'[_-](\d+)[._-]',  # _1., -1-, _1_
        r'серия[_\s]*(\d+)',  # серия_1, серия 1
        r'[Сс]ерия[_\s]*(\d+)',  # Серия_1, серия 1
    ]
    
    for pattern in patterns:
        match = re.search(pattern, filename, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Try Cyrillic number mapping (З = 3, Ч = 4, П = 5, Ш = 6, etc.)
    cyrillic_to_num = {
        'з': '3', 'З': '3',
        'ч': '4', 'Ч': '4',
        'п': '5', 'П': '5',
        'ш': '6', 'Ш': '6',
    }
    
    for cyr, num in cyrillic_to_num.items():
        if cyr in filename:
            return num
    
    # Default: try to extract first number from filename
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return numbers[0]
    
    # If nothing found, return "1" as default
    return "1"

st.title("🎬 Генератор препродакшн-таблиц для киносценариев")
st.markdown("---")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Настройки")
    
    use_custom = st.checkbox("Использовать кастомные столбцы", value=st.session_state.use_custom)
    st.session_state.use_custom = use_custom
    
    if not use_custom:
        preset_choice = st.selectbox(
            "Выберите пресет таблицы",
            options=list(PRESETS.keys()),
            format_func=lambda x: PRESETS[x],
            index=list(PRESETS.keys()).index(st.session_state.selected_preset) if st.session_state.selected_preset in PRESETS else 0
        )
        st.session_state.selected_preset = preset_choice
        st.session_state.selected_columns = None
        selected_columns = None
    else:
        st.subheader("Выберите столбцы")
        default_cols = st.session_state.selected_columns if st.session_state.selected_columns else ALL_COLUMNS[:7]
        selected_columns = st.multiselect(
            "Доступные столбцы",
            options=ALL_COLUMNS,
            default=default_cols
        )
        st.session_state.selected_columns = selected_columns

# Main content area
tab1, tab2 = st.tabs(["📤 Загрузка и обработка", "📊 Результаты"])

with tab1:
    st.header("Загрузите сценарии")
    st.markdown("Вы можете загрузить несколько файлов одновременно для обработки всех серий.")
    
    uploaded_files = st.file_uploader(
        "Выберите файлы сценариев (PDF или DOCX)",
        type=['pdf', 'docx'],
        accept_multiple_files=True,
        help="Поддерживаются файлы объемом до 120 страниц каждый. Можно загрузить несколько файлов для обработки всех серий."
    )
    
    if uploaded_files:
        # Show file info
        st.subheader("📋 Загруженные файлы:")
        file_info = []
        for idx, file in enumerate(uploaded_files, 1):
            file_size = len(file.read())
            file.seek(0)  # Reset file pointer
            file_info.append({
                'index': idx,
                'name': file.name,
                'size': file_size / 1024
            })
        
        # Display files in a nice format
        for info in file_info:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.text(f"{info['index']}. {info['name']}")
            with col2:
                st.text(f"{info['size']:.2f} KB")
        
        total_size = sum(info['size'] for info in file_info)
        st.info(f"📊 Всего файлов: {len(uploaded_files)} | Общий размер: {total_size:.2f} KB")
        
        # Process button
        if st.button("🔄 Обработать все сценарии", type="primary", use_container_width=True):
            with st.spinner(f"Обработка {len(uploaded_files)} сценариев... Это может занять до 5 минут на файл."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    all_processed_scenes = []
                    
                    # Process each file
                    for idx, uploaded_file in enumerate(uploaded_files):
                        status_text.text(f"Обработка файла {idx + 1} из {len(uploaded_files)}: {uploaded_file.name}...")
                        progress_bar.progress(idx / len(uploaded_files))
                        
                        # Upload file to backend
                        files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        response = requests.post(f"{API_URL}/upload", files=files, timeout=300)
                        
                        if response.status_code == 200:
                            data = response.json()
                            scenes = data['scenes']
                            
                            # Extract series number from filename
                            series_num = extract_series_number(uploaded_file.name)
                            
                            # Add series number to each scene
                            for scene in scenes:
                                scene['series_number'] = series_num
                                all_processed_scenes.append(scene)
                            
                            status_text.text(f"✅ Файл {idx + 1} обработан: {len(scenes)} сцен")
                        else:
                            st.warning(f"⚠️ Ошибка при обработке {uploaded_file.name}: {response.text}")
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Все файлы обработаны!")
                    
                    if all_processed_scenes:
                        st.session_state.processed_scenes = all_processed_scenes
                        st.success(f"✅ Успешно обработано {len(all_processed_scenes)} сцен из {len(uploaded_files)} файлов!")
                        
                        # Generate table
                        status_text.text("Генерация объединенной таблицы...")
                        table_preset = 'custom' if use_custom else st.session_state.selected_preset
                        table_response = requests.post(
                            f"{API_URL}/generate-table",
                            json={
                                "scenes_data": all_processed_scenes,
                                "preset": table_preset,
                                "custom_columns": selected_columns if use_custom else None
                            }
                        )
                        
                        if table_response.status_code == 200:
                            table_data = table_response.json()['table']
                            df = pd.DataFrame(table_data)
                            st.session_state.table_data = df
                            st.rerun()
                        else:
                            st.error(f"Ошибка генерации таблицы: {table_response.text}")
                    else:
                        st.error("Не удалось обработать ни один файл.")
                    
                    time.sleep(1)
                
                except requests.exceptions.RequestException as e:
                    st.error(f"Ошибка соединения с API: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()
                except Exception as e:
                    st.error(f"Неожиданная ошибка: {str(e)}")
                    progress_bar.empty()
                    status_text.empty()

with tab2:
    if st.session_state.table_data is not None:
        st.header("Препродакшн-таблица")
        
        df = st.session_state.table_data.copy()
        
        # Search and filter
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input("🔍 Поиск по таблице", placeholder="Введите текст для поиска...")
        with col2:
            if st.button("🔄 Обновить таблицу", use_container_width=True):
                # Regenerate table with current preset
                if st.session_state.processed_scenes:
                    try:
                        table_preset = 'custom' if use_custom else st.session_state.selected_preset
                        table_response = requests.post(
                            f"{API_URL}/generate-table",
                            json={
                                "scenes_data": st.session_state.processed_scenes,
                                "preset": table_preset,
                                "custom_columns": selected_columns if use_custom else None
                            }
                        )
                        if table_response.status_code == 200:
                            table_data = table_response.json()['table']
                            df = pd.DataFrame(table_data)
                            st.session_state.table_data = df
                            st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка: {str(e)}")
        
        # Filter dataframe if search term provided
        if search_term:
            mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False, na=False)).any(axis=1)
            df = df[mask]
            st.info(f"Найдено строк: {len(df)}")
        
        # Editable dataframe
        st.subheader("Редактируемая таблица")
        edited_df = st.data_editor(
            df,
            use_container_width=True,
            num_rows="fixed",
            height=600
        )
        
        # Update session state if edited
        if not edited_df.equals(st.session_state.table_data):
            st.session_state.table_data = edited_df
        
        # Export buttons
        st.markdown("---")
        st.subheader("📥 Экспорт данных")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV export
            csv_buffer = BytesIO()
            edited_df.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
            csv_buffer.seek(0)
            
            st.download_button(
                label="💾 Скачать CSV",
                data=csv_buffer,
                file_name="preproduction_table.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # XLSX export
            xlsx_buffer = BytesIO()
            with pd.ExcelWriter(xlsx_buffer, engine='openpyxl') as writer:
                edited_df.to_excel(writer, index=False, sheet_name='Препродакшн-таблица')
            xlsx_buffer.seek(0)
            
            st.download_button(
                label="💾 Скачать XLSX",
                data=xlsx_buffer,
                file_name="preproduction_table.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        
        # Statistics
        st.markdown("---")
        st.subheader("📈 Статистика")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Всего сцен", len(edited_df))
        with col2:
            scenes_with_chars = edited_df['Персонажи'].notna().sum() if 'Персонажи' in edited_df.columns else 0
            st.metric("Сцен с персонажами", scenes_with_chars)
        with col3:
            scenes_with_props = edited_df['Реквизит'].notna().sum() if 'Реквизит' in edited_df.columns else 0
            st.metric("Сцен с реквизитом", scenes_with_props)
    
    else:
        st.info("👆 Загрузите и обработайте сценарий на вкладке 'Загрузка и обработка'")

