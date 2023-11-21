import streamlit as st
import pandas as pd
import numpy as np
import uuid


def main():
    st.title("Procesamiento de bases QPRO")
    
    # Agrega un componente de carga de archivos en la aplicación
    uploaded_file = st.file_uploader("Subir archivo CSV", type="csv")
    
    if uploaded_file is not None:
        # Lee el archivo CSV con pandas
        data = pd.read_csv(uploaded_file, sep= ";",encoding= "latin1")
        data["C1"] = data["C1"].str.strip()
        data = data[data["C1"] != ""]
        # Muestra los datos en una tabla
        st.dataframe(data.head())
        

        st.subheader("Variable principal de análisis")
        
        #Listamos los nombres de las columnas
        opciones = data.columns.tolist()
        
        # Armamos la lista desplegable para las columnas que van a quedar fijas.  
        valores_fijos= st.multiselect("Selecciona las columnas fijas (rango etario, genero, etc.) que acompañan a la variable de análisis", options= opciones)

        # Armamos la lista desplegable para la transformación de varias columnas a una sola.
        varias_una= st.multiselect("Selecciona las múltiples columnas que deseas transformar a una sola", options= opciones)

        # Ingresa el nombre de la columna que condensa todas las anteriores. 

        title = st.text_input('Ingresa el nombre de la columna principal de análisis')

        # Creamos el dataframe nuevo que repite n cantidad de veces los valores desados.
        melted_data = pd.melt(data, id_vars= valores_fijos, value_vars=varias_una, var_name='col', value_name=title, ignore_index=False)
        melted_data= melted_data.drop("col", axis= 1)

        original= data

        try:
            
            # Realizar merge con sufijos para las columnas duplicadas
            nuevo_melt = melted_data.merge(original, on='C1', how='left', suffixes=('', '_right'))

            # Eliminar columnas duplicadas del dataframe derecho
            duplicated_columns = [col for col in nuevo_melt.columns if col.endswith('_right')]
            nuevo_melt.drop(duplicated_columns, axis=1, inplace=True)
            nuevo_melt.replace(" ", np.nan, inplace=True)
            nuevo_melt.dropna(subset= title, inplace=True)
            
            data_transform= melted_data 
            data_transform.replace(" ", np.nan, inplace=True)
            data_transform.dropna(subset=title, inplace=True)

        except: 
            st.stop()

        
        
        #Creamos el dataframe con los valores repetidos que escojimos y el df original
        st.dataframe(data_transform)



        #----------------------------------
        # PREGUNTAS DE RESPUESTA ÚNICA
        #----------------------------------

        
        ## Agregar columnas unicas

        st.subheader("Preguntas simples de respuesta única")

        numero_col = st.number_input('Ingresa la cantidad de columnas de respuesta unica', step= 1,min_value=1,  max_value=10)


        options_col_unique= original.columns 
        
        list_text= []
        for i in range(1, numero_col +1):
            key_name = f"column_{i}"
            input_text = st.text_input(f"Ingresa el nombre de la columna {i}", key= key_name)
            list_text.append(input_text)
            nuevo_melt[input_text]= np.NaN
            selected_columns = []  # Lista para almacenar las columnas seleccionadas
            
            for j, ott_values in enumerate(nuevo_melt[title].unique()):
                key_name_j = f"column_{i}_value_{j}"
                columns_selected = st.multiselect(f"Ingresa la columna correspondiente a {ott_values}", options=options_col_unique, key=key_name_j, max_selections=1)
                
                if columns_selected:
                    selected_columns.append(columns_selected[0])  # Agregar la columna seleccionada a la lista de columnas
                else:
                    selected_columns.append(None)
                    #for a in selected_columns:
                    #    nuevo_melt[input_text]= np.where(nuevo_melt[title] == ott_values, nuevo_melt[a], np.nan)

            for unique_value, selected_value in zip(nuevo_melt[title].unique(), selected_columns):
                if selected_value is not None:
                    nuevo_melt.loc[nuevo_melt[title] == unique_value, input_text] = nuevo_melt.loc[nuevo_melt[title] == unique_value, selected_value]

        
        ## Mostramos el DF final con las columnas de respuestas unicas. 
        final_unicos= valores_fijos + [title] + list_text
        

        if selected_columns:
            df_final_unicos= nuevo_melt[final_unicos]
            df_final_unicos["df_origen"]= "df_unicos"

        else:
            df_final_unicos= pd.DataFrame()

        st.dataframe(df_final_unicos) 
        



        #----------------------------------
        # PREGUNTAS DE MULTIPLE CHOICE RESPUESTA SIMPLE
        #----------------------------------

        st.subheader("Preguntas múltiple choice simples")

        col_multiple = st.number_input('Ingresa la cantidad de columnas a generar', step=1, min_value=1, max_value=10)

        options_col_multiple = original.columns

        dfs_multi = []  # Lista para almacenar los DataFrames individuales

        for i in range(1, col_multiple + 1):
            key_name_multi_text = f"column_multi_text{i}"
            key_name_multi_number = f"column_multi_number{i}"
            input_text_multi_col = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {i}", key=key_name_multi_text)
            st.text(".........................................................")

            column_names_multi = []  # Lista para almacenar los nombres de las columnas generadas en cada iteración

            df_multi = pd.DataFrame()  # DataFrame vacío para cada iteración del bucle externo

            unic_multi= nuevo_melt[title].unique()
            for j, ott_values in enumerate(unic_multi):
                key_name_multi_2 = f"column_multi_2{i}_{j}"
                key_name_multi_3 = f"column_multi_3{i}_{j}"
                list_multi_fijas = st.multiselect(f"Selecciona columnas de respuesta única adicionales para {ott_values} (OPTATIVO)", options=options_col_multiple, key=key_name_multi_2)
                list_multi_nuevas = st.multiselect(f"Selecciona las columnas a transformar para {ott_values}", options=options_col_multiple, key=key_name_multi_3)
                st.text("                                                               ---                                           ")
                 
                if list_multi_nuevas:
                    fijas_multi= valores_fijos + list_multi_fijas 
                    df = pd.melt(data, id_vars= fijas_multi, value_vars=list_multi_nuevas, var_name='col', value_name='value', ignore_index=False)
                    df = df.drop("col", axis=1)
                    df[title]= ott_values
                    column_name = input_text_multi_col  # Generar un nombre de columna único para cada iteración
                    df.rename(columns={'value': column_name}, inplace=True)
                    df[column_name]= df[column_name].replace(" ", np.NaN)
                    df= df.dropna(subset=column_name, how= "all")
                    column_names_multi.append(column_name)  # Agregar el nombre de la columna generada a la lista   
                    df_multi = pd.concat([df_multi, df], axis=0)  # Concatenar cada dataframe generado en la iteración actual
                    
                
                    

            
            dfs_multi.append(df_multi)  # Agregar el dataframe generado en la iteración actual a la lista de dataframes
            
            #for df_multi in dfs_multi:
            #    df_multi_choice= df_multi.index.tolist()
            
            #try:
        if dfs_multi:
                df_multichoice = pd.concat(dfs_multi, axis=0)
                df_multichoice["df_origen"]= "df_multichoice"
                 
        else:
                df_multichoice = pd.DataFrame()  # Crear DataFrame vacío si no se generaron DataFrames
        
        
            
                

        st.dataframe(df_multichoice, width= 1500)
        st.text("Nota: Al cambiarse los nombres de las columnas de respuesta única adicionadas se unificaran en una columna.")      




        
        #----------------------------------
        # PREGUNTAS DE MATRIZ CRUZADA O RANKING
        #----------------------------------
    
        st.subheader("Preguntas de matriz cruzada o ranking")

        
        
        col_matriz_3 = st.number_input('Ingresa la cantidad de columnas a generar', step=1, min_value=1, max_value=10, key= "key_5")

        options_col_matriz = nuevo_melt.columns

        dfs_matriz = []  # Lista para almacenar los DataFrames individuales

        for h in range(1, col_matriz_3 + 1):
            key_name_matriz_text = f"column_matriz_text{h}"
            key_name_matriz_text2 = f"column_matriz_number{h}"
            key_number_input = f"number_input_{h}"  # Clave única para el widget number_input
            input_text_matriz = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {h} CREADA CON LOS VALORES TRANSFORMADOS ", key=key_name_matriz_text)
            input_text_matriz_2 = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {h} CREADA CON LOS TITULOS ANTIGUOS  ", key=key_name_matriz_text2)


            df_matriz_itera = pd.DataFrame()  # DataFrame vacío para cada iteración del bucle externo

            for a, ott_values_matrix in enumerate(nuevo_melt[title].unique()):
                key_name_matriz_2 = f"column_matriz_2{h}_{a}"
                key_name_matriz_3 = f"column_matriz_3{h}_{a}"
                list_matriz_fijas = st.multiselect(f"Selecciona columnas de respuesta única adicionales para {ott_values_matrix} (OPTATIVO)", options=options_col_matriz, key=key_name_matriz_2)
                list_matriz_nuevas = st.multiselect(f"Selecciona las columnas a transformar para {ott_values_matrix}", options=options_col_matriz, key=key_name_matriz_3)

                if list_matriz_nuevas:
                    fijas_matriz= valores_fijos + list_matriz_fijas
                    df_matriz = pd.melt(data, id_vars= fijas_matriz, value_vars=list_matriz_nuevas, var_name= input_text_matriz_2, value_name=input_text_matriz, ignore_index=False)
                    df_matriz[title]= ott_values_matrix
                    df_matriz[input_text_matriz]= df_matriz[input_text_matriz].replace(" ", np.NaN)
                    df_matriz= df_matriz.dropna(subset=input_text_matriz, how= "all")
                    df_matriz_itera = pd.concat([df_matriz_itera, df_matriz])  # Concatenar cada dataframe generado en la iteración actual

            dfs_matriz.append(df_matriz_itera)  # Agregar el dataframe generado en la iteración actual a la lista de dataframes
            
            
        try:
            if dfs_matriz:
                df_matriz_final = pd.concat(dfs_matriz)  # Concatenar todos los DataFrames generados
                df_matriz_final["df_origen"]= "df_matriz"

            else:
                df_matriz_final = pd.DataFrame()  # Crear DataFrame vacío si no se generaron DataFrames
                



            st.dataframe(df_matriz_final, width= 1500)    
            
        except:
            st.dataframe()


        #----------------------------------
        # AGREGAR COLUMNAS SIN TRANSFORMACIÓN 
        #----------------------------------

        st.subheader("Transformación de preguntas del caso original")
        
        unic_check= st.checkbox("Respuesta única")
        multi_check= st.checkbox("multiplechoice")
        matriz_check= st.checkbox("matriz")
                        
        
        df_sin_transformar= pd.DataFrame()
        if unic_check:
            st.subheader("columnas de respuesta única")
            list_original_nuevas = st.multiselect(f"Selecciona las columnas que quieres agregar (no incluyas las columnas fijas iniciales)", options=opciones)
            if list_original_nuevas:
                filtro_original= valores_fijos + list_original_nuevas
                df_sin_transformar= data[filtro_original]
                df_sin_transformar["df_origen"]= "df_casos"
            
        else:
            df_sin_transformar = pd.DataFrame()  # Crear DataFrame vacío si no se generaron DataFrames
        
        st.dataframe(df_sin_transformar, width= 1500)

        ###----------------###
        ### MULTICHECK
        ###----------------###
        multicheck_final= pd.DataFrame()
        if multi_check:
            st.subheader("columnas de respuesta multiple choice simple")
            col_multicheck = st.number_input('Ingresa la cantidad de columnas a generar', step=1, min_value=1, max_value=10, key= 1000)

            options_col_multicheck = data.columns

            dfs_multicheck = []  # Lista para almacenar los DataFrames individuales

            for i in range(1, col_multicheck + 1):
                key_multicheck_text = f"column_check_text{i}"
                key_multicheck_number = f"column_check_number{i}"
                key_multicheck_number2 = f"column_check_number2{i}"
                input_text_multicheck = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {i}", key=key_multicheck_text)
                st.text(".........................................................")

                columns_multicheck = []  # Lista para almacenar los nombres de las columnas generadas en cada iteración

                df_multicheck = pd.DataFrame()  # DataFrame vacío para cada iteración del bucle externo

                multicheck_fijas = st.multiselect(f"Selecciona columnas de respuesta única adicionales para {i} (OPTATIVO)", options=options_col_multicheck, key=key_multicheck_number)
                multicheck_nuevas = st.multiselect(f"Selecciona las columnas a transformar para la columna {1}", options=options_col_multicheck, key=key_multicheck_number2)
                st.text("                                                               ---                                           ")
                    
                if multicheck_nuevas:
                    fijas_multicheck= valores_fijos + multicheck_fijas 
                    df_check = pd.melt(data, id_vars= fijas_multicheck, value_vars=multicheck_nuevas, var_name='col', value_name='value', ignore_index=False)
                    df_check = df_check.drop("col", axis=1)
                    column_name_check = input_text_multicheck  # Generar un nombre de columna único para cada iteración
                    df_check.rename(columns={'value': column_name_check}, inplace=True)
                    df_check[column_name_check]= df_check[column_name_check].replace(" ", np.NaN)
                    df_check= df_check.dropna(subset=column_name_check, how= "all")
                    columns_multicheck.append(column_name_check)  # Agregar el nombre de la columna generada a la lista   
                    df_multicheck = pd.concat([df_multicheck, df_check], axis=0)  # Concatenar cada dataframe generado en la iteración actual
                        
                    
                        

                
                dfs_multicheck.append(df_multicheck)  # Agregar el dataframe generado en la iteración actual a la lista de dataframes
                
                #for df_multi in dfs_multi:
                #    df_multi_choice= df_multi.index.tolist()
                
                #try:
            if dfs_multicheck:
                    multicheck_final = pd.concat(dfs_multicheck, axis=0)
                    multicheck_final["df_origen"]= "df_multicheck"
                        
            else:
                    multicheck_final = pd.DataFrame()  # Crear DataFrame vacío si no se generaron DataFrames
            
            
                
                    

            st.dataframe(multicheck_final, width= 1500)
            st.text("Nota: Al cambiarse los nombres de las columnas de respuesta única adicionadas se unificaran en una columna.")   


        ###----------------###
        ### RANKINGCHECK
        ###----------------###  
        matrizcheck_final= pd.DataFrame()
        if matriz_check:
            st.subheader("columnas de respuesta tipo matriz cruzada o ranking")
            col_matrizcheck = st.number_input('Ingresa la cantidad de columnas a generar', step=1, min_value=1, max_value=10, key= 1500)

            options_col_check = data.columns

            dfs_matrizcheck = []  # Lista para almacenar los DataFrames individuales

            for i in range(1, col_matrizcheck + 1):
                key_matrizcheck_text = f"column_macheck_text{i}"
                key_matrizcheck_number = f"column_macheck_number{i}"
                key_matrizcheck_text2 = f"column_macheck_number2{i}"
                key_matrizcheck_number2= f"column_macheck_number3{i}"
                input_text_matrizcheck = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {i} CREADA CON LOS VALORES TRANSFORMADOS", key=key_matrizcheck_text)
                input_text_matrizcheck2 = st.text_input(f"INGRESA EL NOMBRE DE LA COLUMNA {i} CREADA CON LOS TÍTULOS ANTIGUOS", key=key_matrizcheck_text2)
                st.text(".........................................................")

                #columns_matrizcheck = []  # Lista para almacenar los nombres de las columnas generadas en cada iteración

                df_matrizcheck = pd.DataFrame()  # DataFrame vacío para cada iteración del bucle externo

                matrizcheck_fijas = st.multiselect(f"Selecciona columnas de respuesta única adicionales para {i} (OPTATIVO)", options=options_col_check, key=key_matrizcheck_number)
                matrizcheck_nuevas = st.multiselect(f"Selecciona las columnas a transformar para la columna {1}", options=options_col_check, key=key_matrizcheck_number2)
                st.text("                                                               ---                                           ")
                    
                if matrizcheck_nuevas:
                    fijas_matrizcheck= valores_fijos + matrizcheck_fijas 
                    df_macheck = pd.melt(data, id_vars= fijas_matrizcheck, value_vars=matrizcheck_nuevas, var_name=input_text_matrizcheck2, value_name=input_text_matrizcheck, ignore_index=False)
                    #df_macheck = df_macheck.drop("col", axis=1)
                    column_name_matrizcheck = input_text_matrizcheck  # Generar un nombre de columna único para cada iteración
                    df_macheck.rename(columns={'value': column_name_matrizcheck}, inplace=True)
                    df_macheck[column_name_matrizcheck]= df_macheck[column_name_matrizcheck].replace(" ", np.NaN)
                    df_macheck= df_macheck.dropna(subset=column_name_matrizcheck, how= "all")
                    #columns_matrizcheck.append(column_name_matrizcheck)  # Agregar el nombre de la columna generada a la lista   
                    df_matrizcheck = pd.concat([df_matrizcheck, df_macheck], axis=0)  # Concatenar cada dataframe generado en la iteración actual
                        
                    
                        

                
                dfs_matrizcheck.append(df_matrizcheck)  # Agregar el dataframe generado en la iteración actual a la lista de dataframes
                

            if dfs_matrizcheck:
                    matrizcheck_final = pd.concat(dfs_matrizcheck, axis=0)
                    matrizcheck_final["df_origen"]= "df_matrizcheck"
                        
            else:
                    matrizcheck_final = pd.DataFrame()  # Crear DataFrame vacío si no se generaron DataFrames
            
             

            st.dataframe(matrizcheck_final, width= 1500)
            st.text("Nota: Al cambiarse los nombres de las columnas de respuesta única adicionadas se unificaran en una columna.")    



        #----------------------------------
        # CONCATENAR TODAS LAS TABLAS
        #----------------------------------

        st.subheader("Transformaciones texto y columnas")

        #Los dfs que haya creado, los concatena todos en uno.      
        dfs_concatenados= []

        if df_final_unicos is not None:
            dfs_concatenados.append(df_final_unicos)

        if df_multichoice is not None:
            dfs_concatenados.append(df_multichoice)

        if df_matriz_final is not None:
            dfs_concatenados.append(df_matriz_final)

        if df_sin_transformar is not None:
            dfs_concatenados.append(df_sin_transformar)

        if multicheck_final is not None:
            dfs_concatenados.append(multicheck_final)

        if matrizcheck_final is not None:
            dfs_concatenados.append(matrizcheck_final)

        if dfs_concatenados:
            concatenados_final= pd.concat(dfs_concatenados)


             
        else:
            concatenados_final= pd.DataFrame()

        st.write(" ")
        st.write(" ")

        hola = st.button("Presiona para concatenar todas las tablas creadas")

        if hola:
            st.dataframe(concatenados_final, width=1500)

        st.write(" ")
        
        df_columnas = pd.DataFrame()
        df_columnas["columnas_vigentes"] = concatenados_final.columns.tolist()
        df_columnas["nuevo_nombre"] = ""
        df_columnas["nuevo_nombre"] = df_columnas["nuevo_nombre"].astype(str)

        nombres_col= st.checkbox("Cambiar nombre de columnas")
        if nombres_col: 
            # Modificación de nombres de columnas.
            st.caption("Si nombras igual a más de una columna, estas se agruparan en una sola")
            edit_df = st.data_editor(df_columnas, hide_index=True, width=1000)
            nombres_cambiados = edit_df.loc[edit_df["nuevo_nombre"] != "", ["columnas_vigentes", "nuevo_nombre"]]

            # VALORES REPETIDOS (COLUMNAS PARA TRANSFORMAR)
            duplicated_nuevos = nombres_cambiados[nombres_cambiados["nuevo_nombre"].duplicated(keep=False)]["nuevo_nombre"].tolist()
            unique_duplicated = list(set(duplicated_nuevos))

            for i in unique_duplicated:
                dfs_i = nombres_cambiados.loc[nombres_cambiados["nuevo_nombre"] == i].index.tolist()
                valores_col_vig = nombres_cambiados.loc[dfs_i, "columnas_vigentes"].tolist()
                concatenados_final[i] = np.nan
                    
                for j in valores_col_vig:
                    concatenados_final[i] = concatenados_final[i].fillna(concatenados_final[j])
                    concatenados_final= concatenados_final.drop(columns= j)

            #VALORES UNICOS (SÓLO REEMPLAZO NOMBRE)

            no_repit= edit_df.loc[(edit_df["nuevo_nombre"] != "") & (edit_df["nuevo_nombre"].notnull())]
            no_repit= no_repit.loc[no_repit['nuevo_nombre'].duplicated(keep=False) == False]
            diccionario_nombres = dict(zip(no_repit['columnas_vigentes'], no_repit['nuevo_nombre']))
            concatenados_final= concatenados_final.rename(columns= diccionario_nombres)
            
        
            st.dataframe(concatenados_final)

        # transformación de texto
        textos_col= st.checkbox("Cambiar valores de datos")

        concatenados_final= concatenados_final.astype(str)
        
        
        if "copia" not in st.session_state:
            st.session_state.copia= concatenados_final.copy()

        if textos_col:
            #st.session_state.copia= concatenados_final
            opt_text= concatenados_final.columns
            text_columns= st.multiselect(options= opt_text, label= "Ingresa las columnas con los valores a modificar")
            options_transform= ["Empieza con...", "Termina con...", "Contiene", "Valor"]
            transform= st.selectbox(options= options_transform, label= "Ingresa el tipo de reemplazo que deseas hacer")
            if text_columns:
                for i in text_columns:
                    if transform == "Empieza con...":
                        input_empieza= st.text_input("Ingresa los valores iniciales")
                        input_empieza= str(input_empieza)
                        input_emp_rem= st.text_input("Ingresa el valor de reemplazo")
                        input_emp_rem= str(input_emp_rem)
                        boton_start= st.button("Ejecutar")
                        #---
                        if boton_start:
                            st.session_state.copia[i]= st.session_state.copia[i].astype(str)
                            filtro= st.session_state.copia.loc[concatenados_final[i].str.startswith(input_empieza), i].unique()
                            st.session_state.copia[i].replace(filtro,input_emp_rem, inplace=True)
                            print(st.session_state.copia)   
                            

                    if transform == "Termina con...":
                        input_termina= st.text_input("Ingresa los valores finales")
                        input_termina= str(input_termina)
                        input_ter_rem= st.text_input("Ingresa el valor de reemplazo")
                        input_ter_rem= str(input_ter_rem)
                        boton_end= st.button("Ejecutar")
                        if boton_end:
                            st.session_state.copia[i]= st.session_state.copia[i].astype(str)
                            termina_con= st.session_state.copia[i].str.endswith(input_termina)
                            st.session_state.copia.loc[termina_con, i]= input_ter_rem
                            



                    if transform == "Contiene":
                        input_contiene= st.text_input("Ingresa los valores contenidos")
                        input_contiene= str(input_contiene)
                        input_contiene_rem= st.text_input("Ingresa el valor de reemplazo")
                        input_contiene_rem= str(input_contiene_rem)
                        boton_contiene= st.button("Ejecutar")
                        if boton_contiene:
                            st.session_state.copia[i]= st.session_state.copia[i].astype(str)
                            contiene= st.session_state.copia[i].str.contains(input_contiene)
                            st.session_state.copia.loc[contiene, i]= input_contiene_rem
                            
                            

                    if transform == "Valor":
                        i = str(i)
                        values_valor= pd.DataFrame(concatenados_final)
                        #print(values_valor.columns)
                        #values_valor= values_valor[i].loc[(values_valor[i] != "nan") & (values_valor.notnull()) & (values_valor[i] != str(" "))].unique()
                        values_valor= values_valor[i].unique()
                        df_valor= pd.DataFrame()
                        df_valor["valores_actuales"]= values_valor
                        df_valor["valores_nuevos"]= ""
                        valor_edit = st.data_editor(df_valor, hide_index=True, width=1000)
                        boton_valor= st.button("Ejecutar")
                        if boton_valor:
                            valor_edit["valores_nuevos"]=valor_edit["valores_nuevos"].str.strip() 
                            valor_comp= valor_edit.loc[(valor_edit["valores_nuevos"] != "") & (valor_edit["valores_nuevos"].notnull()) & (valor_edit["valores_nuevos"] != "nan") & valor_edit["valores_nuevos"] != " " ]
                            dicc_valor= dict(zip(valor_comp["valores_actuales"],valor_comp["valores_nuevos"]))
                            dicc_valor= {clave: valor for clave, valor in dicc_valor.items() if valor}
                            print(dicc_valor)
                            concatenados_final[i].replace(dicc_valor, inplace=True)
                            
                            

        
            st.dataframe(concatenados_final)

        def convert_df(df):
            return df.to_csv(index=False).encode("latin1")
            
            
        csv= convert_df(concatenados_final)

         
        st.download_button("Descargar archivo final", data= csv, file_name= "base_final.csv")
        
        

        

if __name__ == "__main__":
    main() 

