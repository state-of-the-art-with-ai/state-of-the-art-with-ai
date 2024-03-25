
import streamlit as st


from tiny_data_wharehouse.data_wharehouse import DataWharehouse
tdw = DataWharehouse()

df = tdw.event('state_of_the_art_summary')
run_number = st.selectbox('Run number',  list(range(-1, -10, -1)))

header =  "From Date " +  df['from_date'].values[run_number] + ' To date: ' + df['to_date'].values[run_number]
st.text(header)

st.markdown(df['summary'].values[run_number])


#st.table(df)