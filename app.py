import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
from plotly import express
import plotly.express as px


DATA_URL = (
    "C:\\Users\\diksh\\PycharmProjects\\streamlitapp\\Motor_Vehicle_Collisions_-_Crashes.csv"
            )

st.title("Motor Vehicle Collision in NYC")
st.markdown("This is streamlit dashboard thata can be used to analyze motor vehicle collision in NYC")

#load data
@st.cache(persist= True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows= nrows, parse_dates= [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset= ['LATITUDE', 'LONGITUDE'], inplace = True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis ='columns', inplace= True)
    data.rename(columns= {'crash_date_crash_time': 'date/time'}, inplace= True)
    return data

data = load_data(100000)
#make copy of data
og_data = data

#visualize data on map
st.header("Where are most people injured in NYC?") #ask qs to data
injured_people = st.slider("How many people injured ?", 0, 19)
st.map(data.query('injured_persons >=@injured_people')[['latitude', 'longitude']].dropna(how ='any')) #filter data according to slider value

#filtering data and interactive so that raw data table in app changes accordingly
st.header("How many collisions occured during given period of day ?")
hour = st.slider("Hour to look at", 0, 23)
data = data[data['date/time'].dt.hour == hour] #subset the data of hour/time according to hour slider value

#plot filtered data with 3D interactive map
st.markdown("Vehicle collision at %i:00 and %i:00" %(hour, (hour + 1) %24))
midpoint = (np.average(data['latitude']), np.average(data['longitude'])) #set midpoint for initial_view_state of deckgl

#pydeck code
st.write(pdk.Deck(
    map_style= "mapbox://styles/mapbox/light-v9",
    initial_view_state= {
        'latitude': midpoint[0],
        'longitude': midpoint[1],
        'zoom': 11,
        'pitch': 50,
    },
    layers= [
        pdk.Layer(
            "HexagonLayer",
            data = data[['date/time', 'latitude', 'longitude']],
            get_position = ['longitude', 'latitude'],
            radius = 100,
            extruded = True,
            pickable = True,
            elevation_scale = 4,
            elevation_range = [0, 1000],
        ),
    ],
))
#charts and graphs using plotly
#here will breakdown the date/time into minutes value
#from plotly import express import plotly.express as px

st.subheader("Breakdown by minutes between %i:00 and %i:00" %(hour, (hour + 1) %24))
filtered = data[
    (data['date/time'].dt.hour >= hour) & (data['date/time'].dt.hour < (hour +1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins =60, range=(0, 60))[0]
chart_data = pd.DataFrame({'minutes': range(60), 'crashes': hist})
fig = px.bar(chart_data, x='minutes', y='crashes', hover_data= ['minutes', 'crashes'], height= 400)
st.write(fig)

#Select data using dropdowns
#to get most dangerous street for vehicles to travel and injured people from data

st.header("Top 5 dangerous street by type of vehicle drivers affected")
select = st.selectbox("Type of vehicle drivers affected", ['Pedestrians', 'Cyclists', 'Motorists'])

#if else statements for selected driver types
#to that we need data that is not filtered set og_data = data that we loaded previously

if select == 'Pedestrians':
    st.write(og_data.query('injured_pedestrians >=1')[['on_street_name', 'injured_pedestrians']].sort_values(by= ['injured_pedestrians'], ascending= False).dropna(how= "any")[:5])
elif select == 'Cyclists':
    st.write(og_data.query('injured_cyclists >=1')[['on_street_name', 'injured_cyclists']].sort_values(by= ['injured_cyclists'], ascending= False).dropna(how ='any')[:5])
else:
    st.write(og_data.query('injured_motorists >=1')[['on_street_name', 'injured_motorists']].sort_values(by= ['injured_motorists'], ascending= False).dropna(how = 'any')[:5])


if st.checkbox("Show Raw Data", False):
    st.subheader("RAW DATA")
    st.write(data)


