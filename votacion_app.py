import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Calculadora de Cuociente Electoral",
    page_icon="🗳️",
    layout="wide"
)

st.title("🗳️ Calculadora de Cuociente Electoral")
st.markdown("---")

st.markdown("""
### ¿Qué es el Cuociente Electoral?
El cuociente electoral es un sistema utilizado para la elección de juntas directivas que garantiza la representación de minorías.
Se calcula dividiendo el total de votos válidos entre el número de puestos a proveer.
""")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Configuración")
    
    puestos = st.number_input(
        "Número de puestos a elegir:",
        min_value=1,
        value=3,
        help="Cantidad total de puestos disponibles en la junta directiva"
    )
    
    st.subheader("📊 Planchas Participantes")
    
    if 'planchas' not in st.session_state:
        st.session_state.planchas = [
            {"nombre": "Lista A", "votos": 345},
            {"nombre": "Lista B", "votos": 90}
        ]
    
    for i, plancha in enumerate(st.session_state.planchas):
        with st.container():
            st.markdown(f"**Plancha {i+1}:**")
            col_nombre, col_votos = st.columns([2, 1])
            
            with col_nombre:
                nuevo_nombre = st.text_input(
                    f"Nombre", 
                    value=plancha["nombre"],
                    key=f"nombre_{i}"
                )
                st.session_state.planchas[i]["nombre"] = nuevo_nombre
            
            with col_votos:
                nuevos_votos = st.number_input(
                    f"Votos",
                    min_value=0,
                    value=plancha["votos"],
                    key=f"votos_{i}"
                )
                st.session_state.planchas[i]["votos"] = nuevos_votos
    
    col_add, col_remove = st.columns(2)
    
    with col_add:
        if st.button("➕ Agregar Plancha"):
            st.session_state.planchas.append({
                "nombre": f"Lista {chr(65 + len(st.session_state.planchas))}",
                "votos": 0
            })
            st.rerun()
    
    with col_remove:
        if len(st.session_state.planchas) > 1:
            if st.button("➖ Eliminar Última"):
                st.session_state.planchas.pop()
                st.rerun()

with col2:
    st.subheader("🏆 Resultados del Cuociente Electoral")
    
    planchas_validas = [p for p in st.session_state.planchas if p["votos"] > 0]
    
    if planchas_validas and puestos > 0:
        total_votos = sum(p["votos"] for p in planchas_validas)
        cuociente_electoral = total_votos / puestos
        
        st.markdown("### 📋 Fórmula del Cuociente")
        st.latex(r'''
        \text{Cuociente Electoral} = \frac{\text{Total de Votos}}{\text{Número de Puestos}}
        ''')
        
        st.info(f"""
        **Cuociente Electoral = {total_votos:,} ÷ {puestos} = {cuociente_electoral:.2f}**
        """)
        
        resultados = []
        for plancha in planchas_validas:
            cociente = plancha["votos"] // cuociente_electoral
            residuo = plancha["votos"] % cuociente_electoral
            porcentaje = (plancha["votos"] / total_votos) * 100
            
            resultados.append({
                "Plancha": plancha["nombre"],
                "Votos": plancha["votos"],
                "Porcentaje": porcentaje,
                "Cociente": int(cociente),
                "Residuo": residuo,
                "Puestos_Inicial": int(cociente)
            })
        
        puestos_asignados = sum(r["Cociente"] for r in resultados)
        puestos_restantes = puestos - puestos_asignados
        
        resultados.sort(key=lambda x: x["Residuo"], reverse=True)
        
        for i in range(min(puestos_restantes, len(resultados))):
            resultados[i]["Puestos_Final"] = resultados[i]["Puestos_Inicial"] + 1
        
        for i in range(puestos_restantes, len(resultados)):
            resultados[i]["Puestos_Final"] = resultados[i]["Puestos_Inicial"]
        
        st.markdown("### 🎯 Asignación Final de Puestos")
        
        df_resultados = pd.DataFrame(resultados)
        
        for _, row in df_resultados.iterrows():
            with st.container():
                col_info, col_puestos = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"""
                    **{row['Plancha']}**
                    - Votos: {row['Votos']:,} ({row['Porcentaje']:.1f}%)
                    - División: {row['Votos']:,} ÷ {cuociente_electoral:.2f} = {row['Votos']/cuociente_electoral:.2f}
                    - Cociente: {row['Cociente']} | Residuo: {row['Residuo']:.2f}
                    """)
                
                with col_puestos:
                    st.metric(
                        label="Puestos Asignados",
                        value=f"{int(row['Puestos_Final'])}",
                        delta=f"+{int(row['Puestos_Final'] - row['Puestos_Inicial'])}" if row['Puestos_Final'] > row['Puestos_Inicial'] else None
                    )
                
                st.markdown("---")
        
        st.markdown("### 📈 Visualización de Resultados")
        
        fig_votos = px.pie(
            df_resultados, 
            values='Votos', 
            names='Plancha',
            title="Distribución de Votos por Plancha"
        )
        st.plotly_chart(fig_votos, use_container_width=True)
        
        fig_puestos = px.bar(
            df_resultados,
            x='Plancha',
            y='Puestos_Final',
            title="Puestos Asignados por Plancha",
            text='Puestos_Final'
        )
        fig_puestos.update_traces(textposition='outside')
        st.plotly_chart(fig_puestos, use_container_width=True)
        
        st.success(f"""
        **Resumen Final:**
        - Total de votos: {total_votos:,}
        - Puestos disponibles: {puestos}
        - Puestos asignados: {sum(int(r['Puestos_Final']) for r in resultados)}
        - Cuociente electoral: {cuociente_electoral:.2f}
        """)
        
        if puestos_restantes > 0:
            st.info(f"""
            **Método de asignación de residuos:**
            {puestos_restantes} puesto(s) adicional(es) se asignaron a las planchas con mayores residuos.
            """)
    
    else:
        st.warning("⚠️ Ingrese al menos una plancha con votos válidos para calcular la asignación.")

st.markdown("---")
st.markdown("""
### 📚 Información Legal
Este sistema está basado en el Artículo 197 del Código de Comercio de Colombia y es obligatorio para 
sociedades anónimas, exceptuando las Sociedades por Acciones Simplificadas (SAS).

**Objetivo:** Garantizar la representación proporcional y evitar que los accionistas mayoritarios 
monopolicen todos los puestos de la junta directiva.
""")