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
    st.header("Загрузите сценарий")
    
    uploaded_file = st.file_uploader(
        "Выберите файл сценария (PDF или DOCX)",
        type=['pdf', 'docx'],
        help="Поддерживаются файлы объемом до 120 страниц"
    )
    
    if uploaded_file is not None:
        # Show file info
        file_size = len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer
        
        col1, col2 = st.columns(2)
        with col1:
            st.info(f"📄 Файл: {uploaded_file.name}")
        with col2:
            st.info(f"📏 Размер: {file_size / 1024:.2f} KB")
        
        # Process button
        if st.button("🔄 Обработать сценарий", type="primary", use_container_width=True):
            with st.spinner("Обработка сценария... Это может занять до 5 минут."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    # Upload file to backend
                    status_text.text("Загрузка файла...")
                    progress_bar.progress(10)
                    
                    files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_URL}/upload", files=files, timeout=300)
                    
                    progress_bar.progress(50)
                    status_text.text("Извлечение элементов...")
                    
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.processed_scenes = data['scenes']
                        
                        progress_bar.progress(100)
                        status_text.text("✅ Обработка завершена!")
                        time.sleep(1)
                        
                        st.success(f"✅ Успешно обработано {data['total_scenes']} сцен!")
                        
                        # Generate table
                        status_text.text("Генерация таблицы...")
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
                        else:
                            st.error(f"Ошибка генерации таблицы: {table_response.text}")
                    
                    else:
                        st.error(f"Ошибка обработки: {response.text}")
                        progress_bar.empty()
                        status_text.empty()
                
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

