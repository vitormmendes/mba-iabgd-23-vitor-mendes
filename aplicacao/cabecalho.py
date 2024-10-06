import streamlit as st

def gerar_cabecalho():
    # Define the custom style for the header with gray background
    st.markdown("""
        <style>
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #d3d3d3; /* Cinza claro */
            padding: 10px 20px;
            border-bottom: 1px solid #ccc;
            font-family: 'Arial', sans-serif;
        }
        .header .app-name {
            font-size: 20px;
            font-weight: bold;
        }
        .header .icons {
            display: flex;
            align-items: center;
        }
        .header .icon {
            font-size: 18px;
            margin-left: 20px;
        }
        .header .icon:hover {
            cursor: pointer;
        }
        </style>
        <div class="header">
            <div class="app-name">Aplicativo de comida</div>
            <div class="icons">
                <span class="icon">🔔</span>
                <span class="icon">⋮</span>
            </div>
        </div>
        """, unsafe_allow_html=True)