# -*- coding: utf-8 -*-
'''
streamlit run webqc.py
'''
import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import math
from streamlit_extras.dataframe_explorer import dataframe_explorer
# disable chained assignments
#pd.options.mode.chained_assignment = None 

st.set_page_config(
    page_title="WebQC",
    page_icon="🗃️",
    layout="wide",
    initial_sidebar_state="expanded"
)

#START HIDE the TOP an burger menu!
st.markdown("""
<style>
	[data-testid="stDecoration"] {
		display: none;
	}
    .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}

</style>""",
unsafe_allow_html=True)

ms = st.session_state
if "themes" not in ms: 
  ms.themes = {"current_theme": "dark",
                    "refreshed": True,
                    
                    "light": {"theme.base": "dark",
                              "button_face": "🌜"},

                    "dark":  {"theme.base": "light",
                              "button_face": "🌞"},
                    }


if ms.themes["current_theme"]=="dark":
    hide_streamlit_style = """
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0.5rem;}
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                    background-color: Chocolate;
                    border-color: #ff0000;
                }
            body
        </style>
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    
        """
else:
    hide_streamlit_style = """
        <style>
            #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0.5rem;}
            .stSelectbox div[data-baseweb="select"] > div:first-child {
                    background-color: gray;
                    border-color: #000000;
                }
            body
        </style>
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    
        """

st.markdown(hide_streamlit_style, unsafe_allow_html=True)
#STOP HIDE the TOP an burger menu!

def ChangeTheme():
  previous_theme = ms.themes["current_theme"]
  tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
  for vkey, vval in tdict.items(): 
    if vkey.startswith("theme"): st._config.set_option(vkey, vval)

  ms.themes["refreshed"] = False
  if previous_theme == "dark": ms.themes["current_theme"] = "light"
  elif previous_theme == "light": ms.themes["current_theme"] = "dark"
  
st.sidebar.title("Web QC")
st.sidebar.title("Navigation Options")
# Display different functionalities
choice = st.sidebar.selectbox('Select....', options=["Load Data", "Edit Dataframe", "Quality Control"], index=0)
btn_face = ms.themes["light"]["button_face"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]["button_face"]
st.sidebar.write (':blue[\nChange Theme:]')
st.sidebar.button(btn_face, on_click=ChangeTheme)

if ms.themes["refreshed"] == False:
  ms.themes["refreshed"] = True
  st.rerun()


def function_cleaner(x):
   x = x.replace(' ', '_')
   x = x.replace(':', '_')
   x = x.replace('[', '_')
   x = x.replace(']', '_')
   x = x.replace('.', '_')
   x = x.replace('/', '_')
   print('change '+str(x))
   return x


def load_data_2_dataframe(file,separaval):
    '''
     Input Parameters
    ----------
    file : the file needs to be of type CSV
    Description
    -------
    Loads the data from the CSV file into a pandas dataframe
 
    Returns
    -------
    session_state containing dataframe df
    '''
    if 'df' not in st.session_state:
        df = pd.read_csv(file,sep=separaval)
        
        
        for tmpcol in df.columns:
            cleanCol=function_cleaner(tmpcol)
            df.rename(columns={tmpcol: cleanCol}, inplace=True)
        
        st.session_state['df'] = df
        #st.data_editor(df, num_rows="dynamic")
        st.data_editor(df)
    else:
        #st.data_editor(st.session_state['df'], num_rows="dynamic")
        st.data_editor(st.session_state['df'])
        
    return st.session_state['df']

def reset_data():
    if 'df' not in st.session_state:
        print('Dataframe not found')
    else:
        del st.session_state['df']
    load_data()    
    
def qc():
    st.title(':blue[Assign QC Flags] 📈')
    if 'df' in st.session_state:  
        seedata = st.toggle('See dataframe', key="2")
        df= st.session_state['df']   
        #df = dataframe_explorer(df, case=False)
        if "WebQCIndex" not in df.columns:
            df['WebQCIndex'] = range(1, len(df) + 1)
            st.write('To manage the QC, a column labelled WebQCIndex has been added to the dataframe')
        if seedata:
            st.write(df)    
        
        colsGrid = st.columns(4)
        param_column=['']
        param_column.extend(df.columns)
        qc_column=['']
        qc_column.extend(df.columns)
        with colsGrid[0]:
            selected_param_column = st.selectbox('Select param column to check:', param_column)
        with colsGrid[1]:
            selected_qc_column = st.selectbox('Select QC flag column:', qc_column)
        
        if selected_param_column != '' and selected_qc_column != '':
            #myX=selected_index_column
            myY=selected_param_column
            myZ=selected_qc_column
            point_selector = alt.selection_point("point_selection")
            interval_selector = alt.selection_interval("interval_selection")
            chart = (
                alt.Chart(df)
                .mark_circle()
                .encode(
                    x="WebQCIndex",
                    y=myY,
                    #size=myZ+":N",
                    color=myZ+":N",
                    tooltip=["WebQCIndex", myY, myZ],
                    fillOpacity=alt.condition(point_selector, alt.value(1), alt.value(0.3))
                )
                .add_params(point_selector, interval_selector)
                .properties(width=1100, height=900)
            )          
            event = st.altair_chart(chart, theme="streamlit", key="alt_chart", on_select="rerun")
            downloaddata = st.toggle('Download data CSV format', key="1")
            if downloaddata:
                import time
                import uuid
                idrnd = uuid.uuid4()
                savename=str(time.strftime("%Y%m%d%H%M%S")+'-'+str(idrnd))
                st.download_button(
                    label="Download Saved data data as CSV", data=df.to_csv(index=False), file_name="Saved_data"+savename+".csv",
                    mime="text/csv"
                )            
            if str(event)!='{\'selection\': {\'interval\': {}}}':
                with colsGrid[2]:
                    myFlags=[0,1,2,3,4,5,6,7,8,9]
                    selected_flag = st.selectbox('Select QC FLAG:', myFlags)
                with colsGrid[3]: 
                    st.write('')
                    st.write('')
                    if st.button("Assign QC FLAG"):                    
                        x = event.get("selection").get("interval_selection").get("WebQCIndex")
                        y = event.get("selection").get("interval_selection").get(myY)
                        if str(event)!='{\'selection\': {\'interval\': {}}}':
                            count=0
                            for u in x:
                                if count==0:
                                    bottomId = math.floor(u)
                                    #bottomId = u
                                    count+=1
                                else:
                                    topId = math.ceil(u)   
                                    #topId = u
                            count=0
                            for e in y:
                                if count==0:
                                    #bottomParam = math.ceil(e)
                                    #bottomParam = math.floor(e)
                                    bottomParam = e
                                    count+=1
                                else:
                                    topParam = e 
                                    #topParam = math.ceil(e)
                            
                            for i in range(bottomId, topId):
                                #print(str(df[myZ][i])+' to '+str(selected_flag))
                                if df[myY][i] >= bottomParam and df[myY][i] <= topParam:
                                    
                                    df[myZ][i]=selected_flag
                                    #print(str(df[myZ][i])+' to '+str(selected_flag))
                                    #df.loc[df[myZ], i] = selected_flag
                            st.rerun()
        
    else:
        st.write('Please LOAD DATA')

def load_data():
    '''
    loads the selected file into a dataframe
    stores the selected file and dataframe in st.session_state
    '''
    st.title(':blue[Load CSV dataset] 📂')
    # check if the dataframe df in st.session_state and is not blank
    if 'df' in st.session_state and st.session_state['df'] is not None:
        df=load_data_2_dataframe(st.session_state['selected_file'])
        
    else:
        file = st.file_uploader("Upload a file", type=['csv'])
        separa = st.radio(
            "Specify the separator",
            ["COMMA", "TAB", "COLON", "SEMICOLON"])       
        if file is not None:     
            if separa == 'COMMA':
                separaval=','
            if separa == 'TAB':
                separaval='\t'
            if separa == 'COLON':
                separaval=':'
            if separa == 'SEMICOLON':
                separaval=';'
            st.session_state['selected_file'] = file
            df=load_data_2_dataframe(st.session_state['selected_file'],separaval)




def loadDataEditor():
    if 'df' in st.session_state:
        df= st.session_state['df']
        
        #st.write('Data Editor')
        st.title(':blue[Data Editor] 📝')
        #df = dataframe_explorer(df, case=False)
        cols = st.columns(2)
        with cols[0]:
            selected_column = st.selectbox('Select column name to delete:', df.columns,index=None, placeholder="Select ...",)
            #st.write('')
            if st.button("Delete Column"):
                if selected_column is not None:
                    df.drop(columns=[selected_column], axis=1, inplace=True)
                
        with cols[1]:
            #st.write('Insert column name')
            
            title = st.text_input(
                "Insert column name to create a new one 👇",
                "",
                key="placeholder",
            )
            if st.button("Create Column"):
                if title != '':
                    df[title] = ''
                

            
        st.data_editor(dataframe_explorer(df, case=False), num_rows="dynamic")
        #clean_data() 
    else:
        st.write('Please LOAD DATA')

            
if choice == "Load Data":
    reset_data()
elif choice == "Edit Dataframe":
    loadDataEditor()
elif choice == "Quality Control":
    qc()
