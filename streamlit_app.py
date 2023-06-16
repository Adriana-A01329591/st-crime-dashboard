# Actividad Integradora
# Adriana Abella Kuri
# A01329591

# streamlit run Actividad_Integradora.py

import pandas as pd
import plotly.express as px
import streamlit as st
import zipfile
import shutil

st.set_page_config(page_title="Actividad Integradora",
                   page_icon=":yum:",
                   layout="wide")

@st.cache_data
def get_data():
    # Specify the path to the ZIP file
    zip_path = 'database.zip'
    # Specify the name of the CSV file within the ZIP folder
    csv_filename = 'Reduced_DB.csv'
    # Extract the CSV file from the ZIP folder
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extract(csv_filename, path='temp_folder')
    # Read the CSV file into a DataFrame
    csv_filepath = 'temp_folder/' + csv_filename
    df = pd.read_csv(csv_filepath)
    # Clean up: Remove the temporary extracted folder and file
    shutil.rmtree('temp_folder')
    return df

df = get_data()

# Sidebar (Filters)

st.sidebar.header("Filters")

incident_year = st.sidebar.multiselect(
    "Incident Year:",
    options = df['Incident Year'].unique(),
    default = df['Incident Year'].unique()
)

incident_day_of_week = st.sidebar.multiselect(
    "Incident Day of Week:",
    options = df['Incident Day of Week'].unique(),
    default = df['Incident Day of Week'].unique()
)

incident_category = st.sidebar.multiselect(
    "Incident Category:",
    options = df['Incident Category'].unique(),
    default = df['Incident Category'].unique()
)

analysis_neighborhood = st.sidebar.multiselect(
    "Analysis Neighborhood:",
    options = df['Analysis Neighborhood'].unique(),
    default = df['Analysis Neighborhood'].unique()
)

df_selection = df.query(
    "`Incident Category` == @incident_category & `Analysis Neighborhood` == @analysis_neighborhood & `Incident Day of Week` == @incident_day_of_week & `Incident Year` == @incident_year"
)

# st.dataframe(df_selection)

# Mainpage

st.title("🔪 Crime Dashboard")
st.markdown("##")

incident_count = df_selection['Incident ID'].nunique()
top_category = df_selection['Incident Category'].value_counts().idxmax()
highest_incident_neighborhood = df_selection['Analysis Neighborhood'].value_counts().idxmax()
lowest_incident_neighborhood = df_selection['Analysis Neighborhood'].value_counts().idxmin()

column1, column2, column3, column4 = st.columns(4)
with column1:
    st.subheader("Total Incidents:")
    st.subheader(incident_count)
with column2:
    st.subheader("Top Incident Category:")
    st.subheader(top_category)
with column3:
    st.subheader("Highest Incident Neighborhood:")
    st.subheader(highest_incident_neighborhood)
with column4:
    st.subheader("Lowest Incident Neighborhood:")
    st.subheader(lowest_incident_neighborhood)

st.markdown("---")

# Incidents by day of week (Bar chart)

incidents_by_neighborhood = df_selection[["Analysis Neighborhood", "Row ID"]].groupby(by=["Analysis Neighborhood"]).count()

fig_neighborhood_incidents = px.bar(
    incidents_by_neighborhood,
    x = "Row ID",
    y = incidents_by_neighborhood.index,
    orientation = "h",
    title = "<b>Incidents by Neighborhood</b>",
    color_discrete_sequence = ["#0083B8"] * len(incidents_by_neighborhood),
    template = "plotly_white"
)

fig_neighborhood_incidents.update_layout(
    plot_bgcolor = "rgba(0,0,0,0)",
    xaxis = (dict(showgrid=False, title="Number of Incidents"))
)

# st.plotly_chart(fig_neighborhood_incidents)

# incidents by day of week (bar chart)

incidents_by_day_of_week = df_selection[["Incident Day of Week", "Row ID"]].groupby(by=["Incident Day of Week"]).count()

day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

fig_incidents_by_day = px.bar(
    incidents_by_day_of_week,
    x = incidents_by_day_of_week.index,
    y = "Row ID",
    title = "<b>Incidents by Day of Week</b>",
    color_discrete_sequence = ["#0083B8"] * len(incidents_by_day_of_week),
    template = "plotly_white",
    category_orders={"Incident Day of Week": day_order}
)

fig_incidents_by_day.update_layout(
    plot_bgcolor = "rgba(0,0,0,0)",
    yaxis = (dict(showgrid=False, title="Number of Incidents"))
)

# st.plotly_chart(fig_incidents_by_day)

column1, column2 = st.columns(2)

column1.plotly_chart(fig_incidents_by_day, use_container_width=True)
column2.plotly_chart(fig_neighborhood_incidents, use_container_width=True)

# heatmap

df_incident_count = df_selection[['Latitude', 'Longitude', 'Row ID']].groupby(by=['Latitude', 'Longitude']).count().reset_index()

df_incident_count.columns = ['Latitude', 'Longitude', 'Number of Incidents']

fig_incident_density_map = px.density_mapbox(
    df_incident_count, 
    lat='Latitude', 
    lon='Longitude', 
    z='Number of Incidents', 
    radius=10,
    center={'lat': df['Latitude'].mean(), 'lon': df['Longitude'].mean()},
    zoom=10,
    mapbox_style="stamen-terrain"
)

st.plotly_chart(fig_incident_density_map)
