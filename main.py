import streamlit as st
import pandas as pd
import scipy.stats as stats

# Configuración para pantalla completa
st.set_page_config(layout="wide")

st.title("Kolmogorov Smirnov")
st.divider()

# Función para realizar las operaciones
def multiplicador_constante(constante, semilla1, iteraciones):
    # Lista para almacenar los resultados
    resultados = []
    
    for i in range(iteraciones):
        # Calcula el producto de la semilla
        producto = semilla1 * constante
        longitud = len(str(producto))
        
        # Asegurándonos de que producto tenga 0 a la izquierda si es necesario
        if longitud <= 8:
            producto = f"{producto:08}"
        elif longitud <= 16:
            producto = f"{producto:016}"
        elif longitud <= 32:
            producto = f"{producto:032}"
        
        # Tomando los 4 dígitos de en medio según la longitud
        if longitud <= 8:
            medio = producto[2:6]
        elif longitud <= 16:
            medio = producto[6:10]
        elif longitud <= 32:
            medio = producto[14:18]
        
        # Convirtiendo a int()
        medio = int(medio)
        
        # Obteniendo ri
        ri = medio / 10000
        
        # Guardamos los resultados en una lista
        resultados.append({
            'Semilla 1': semilla1,
            'Constante': constante,
            'Producto': producto,
            'Longitud': longitud,
            'Medio': medio,
            'ri': ri
        })
                
        # La nueva semilla será el valor de 'medio' calculado en esta iteración
        semilla1 = medio
        
    return resultados

# Lógica para navegar entre páginas
if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"  # Página inicial por defecto
    
# Página inicial
if st.session_state.pagina == "inicio":

    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.5, 3])

    with col1:
        st.header("1. Ingresa los datos")
        semilla_input = st.text_input("Ingresa tu semilla (número de dígitos pares y mayor a 0):")
        constante_input = st.text_input("Ingresa tu constante (número de dígitos pares y mayor a 0):")
        iteraciones_input = st.number_input("Ingresa las iteraciones:", min_value = 0, max_value = 30, step = 1)
    

    # Si ambos inputs están llenos, hacer las validaciones y mostrar los resultados
    if semilla_input and constante_input and iteraciones_input:
        try:
            semilla1 = int(semilla_input)  # Convertir la semilla a entero
            constante = int(constante_input)  # Convertir la semilla a entero
            iteraciones = int(iteraciones_input)  # Convertir las iteraciones a entero

            # Validación de las condiciones de entrada
            if semilla1 > 0 and len(str(semilla1)) % 2 == 0 and constante > 0 and len(str(constante)) % 2 == 0 and iteraciones > 0:
                # Obtener los resultados de las operaciones
                resultados = multiplicador_constante(constante, semilla1, iteraciones) 
                
                # Guardar los resultados en session_state para usarlos en otra página
                st.session_state.datos = resultados
                            
                # Mostrar la tabla en la columna derecha
                with col2:
                    st.header("Tabla Generada con Multiplicador Constante")
                                    
                    # Convertir la lista de diccionarios en un DataFrame
                    df = pd.DataFrame(resultados)
                    
                    df.index = df.index + 1
                    df = df.rename_axis("Iteración")
                    st.dataframe(df, use_container_width = True)  
                    
                with col1:
                    st.divider()
                    st.header("2. Genera")
                    if st.button("Ir a Kolmogorov Smirnov"):
                        st.session_state.pagina = "Resolver"
                        st.rerun()  # Recarga la página               

            else:
                st.error("Recuerda que la semilla debe tener un número de dígitos pares y mayor a 0, y las iteraciones deben ser mayores a 0.")
        except ValueError:
            st.error("Por favor, ingresa valores numéricos válidos para la semilla y las iteraciones.")
            
# Página de resolución
elif st.session_state.pagina == "Resolver":

    # Crear columnas para organizar el diseño (entrada en la izquierda y resultados en la derecha)
    col1, espacio, col2 = st.columns([2, 0.2, 3])
    
    if "resultados" in st.session_state:  # Verifica que los datos existan
        resultados = st.session_state.resultados

    if "datos" in st.session_state:  # Verifica que los datos existan
        datos = st.session_state["datos"]
    
        with col1:
            # Crear un DataFrame solo con la columna 'ri'
            df_ri = pd.DataFrame(datos)[['ri']]
            
            # Mostrar la tabla con solo la columna 'ri'
            st.subheader("Números Pseudoaleatorios")
            df_ri.index = df_ri.index + 1
            df = df_ri.rename_axis("Datos")
            st.dataframe(df, use_container_width = True)

        with col2:
            st.subheader("Ingreso de datos")
            # Intervalo de confianza
            
            intervalo_de_cf = st.number_input("Ingresa el intervalo de confianza:", min_value = 0, max_value = 100, step = 1)
            
            if intervalo_de_cf:
                resultados = []

                # Alpha
                alpha = (100 - intervalo_de_cf) / 100

                # Contar número de elementos
                n = len(df_ri)

                # Haciendo lista para poder generar un for
                ri_lista = df_ri['ri'].tolist()

                # Ordenamos la lista para la distribución teórica
                ri_lista_ordenada = sorted(ri_lista)

                # Lista para diferencias
                diferencias = []

                for i, num in enumerate(ri_lista, start=1):
                    # Distribución empírica
                    distr_emp = i / n  # Nota: Aquí cambié num/n por i/n

                    # Distribución teórica (tomando el orden correcto)
                    distr_teo = ri_lista_ordenada[i - 1]  

                    # Diferencia
                    diferencia = abs(distr_emp - distr_teo)
                    diferencias.append(diferencia)

                    # Agregar los resultados a la lista
                    resultados.append({
                        'Distribución Emp.': distr_emp,
                        'Distribución Teórica': distr_teo,
                        'Diferencia': diferencia,
                    })    

                # Convertir los resultados en un DataFrame para mostrar
                df_resultados = pd.DataFrame(resultados)

                # Ajustar el índice de df_resultados para empezar desde 1
                df_resultados.index = df_resultados.index + 1
                df_resultados = df_resultados.rename_axis("Número")

                # Valor máximo de las diferencias
                valor_max = max(diferencias)

                # Crear la nueva fila con valores totales
                nueva_fila = pd.DataFrame({
                    'Distribución Emp.': "",
                    'Distribución Teórica': "",
                    'Diferencia': valor_max,
                }, index=["Valor Máximo"]) 

                # Concatenar manteniendo el índice nombrado
                df_final = pd.concat([df_resultados, nueva_fila]).rename_axis("Número")

                # Mostrar la tabla con la fila extra
                st.subheader("Tabla de Kolmogorov-Smirnov")
                st.dataframe(df_final, use_container_width=True)

                # Muestra la imagen de la tabla Kolmogorov-Smirnov            
                st.image("kolmogoro_smirnov.png", caption="Tabla de Kolmogorov - Smirnov.")
                
                # Comparar el valor de la tabla con el de valor_max
                ks = stats.ksone.ppf(1 - alpha / 2, n)  # Prueba bilateral
                st.write(f"El valor crítico de Kolmogorov - Smirnov es {ks}")
                
                # Validacion de valor maximo y kolmogorov - smirnnov
                if valor_max < ks:
                    st.success("Se aprueba la hipótesis nula y son uniformes")
                else:
                    st.error("No se aprueba la hipótesis nuña y no son uniformes")

    else:
        st.error("No hay datos disponibles. Regresa a la página principal.")

    with st.expander("Hecho por:"):
        st.write("Rodrigo González López S4A")               
                