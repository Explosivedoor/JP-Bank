import streamlit as st
import pandas as pd
from io import StringIO
import plotly
st.title("JP Bank (Yucho) CSV Visualizer")
uploaded_file = st.file_uploader("Upload a JP Bank CSV here")
if uploaded_file is not None:

        
    # Read the entire file content as a string
    file_content = uploaded_file.read().decode('shift_jis',)
    
    lines = file_content.splitlines()
    
    # Extract metadata (first 6 lines, or as many as needed)
    metadata_lines = lines[5:6]
    current_cash = lines[1:2]
    current_cash = "\n".join(current_cash).replace(',','').replace('"','').replace('円','')          
    title,current_cash = current_cash.split("：")
    current_cash = int(current_cash)
   
    


    metadata_text = "\n".join(metadata_lines)
    metadata_text_buffer = StringIO(metadata_text)
    first_rows = pd.read_csv(metadata_text_buffer, encoding='shift_jis')
    # Combine the remaining lines into a CSV format
    csv_content = "\n".join(lines[7:])
    csv_buffer = StringIO(csv_content)
    
    remaining_rows = pd.read_csv(csv_buffer, encoding='shift_jis')
    remaining_rows = remaining_rows.drop(remaining_rows.columns[[7]], axis=1)
    remaining_rows['取引日'] = remaining_rows['取引日'].astype(str)
    remaining_rows['取引日'] = remaining_rows['取引日'].str.replace(',', '', regex=False)
    remaining_rows['入出金明細ＩＤ'] = remaining_rows['入出金明細ＩＤ'].astype(str)
    remaining_rows['取引日'] = remaining_rows['取引日'].str.replace(',', '', regex=False)
    



    # Display the metadata
    metadata_text= metadata_text.replace(' 年','/').replace('月','/').replace('日','')       
    st.header(metadata_text)
    st.metric(title,f"￥{current_cash:,}")
    on = st.toggle("See all transactions")
    if on:
        st.write(remaining_rows)
    remaining_rows = remaining_rows.drop(remaining_rows.columns[[0, 1,6]], axis=1)
    money_in = remaining_rows.iloc[:,0]
    money_out = remaining_rows.iloc[:,1]
    money_in_value = money_in.sum()
    money_out_value = money_out.sum()
    
    st.header("Money Flow Info")
    col1,col2 = st.columns(2)
    col1.metric( "Money in", f"{money_in_value:,}")
    col2.metric("Money out", f"{money_out_value:,}")
    value_counts = remaining_rows.iloc[:,3].value_counts()
    #st.write(value_counts)
    pay_places = []
    for i in value_counts.index:
        pay_places.append(i)



 
    df = []
    #getting totals for each payer    
    for i in pay_places:
        pay_info = remaining_rows.loc[remaining_rows.iloc[:,3] == i]
        #st.write(remaining_rows.loc[remaining_rows.iloc[:,3] == i])
        name = pay_info.iloc[0,3]
        money_in = pay_info.iloc[:,0].sum()
        money_out = pay_info.iloc[:,1].sum()
        new_row = {"Name":name,"Money in":money_in,"Money out":money_out}
        df.append(new_row)

    
    df = pd.DataFrame(df) 
    st.bar_chart(df.set_index('Name'))
    col1,col2 = st.columns(2)
    
    col1.text("Highest in")
    col1.metric((df.iloc[df['Money in'].idxmax()][0]),f"{(df.iloc[df['Money in'].idxmax()][1]):,}")
    col2.text("Highest out")
    col2.metric((df.iloc[df['Money out'].idxmax()][0]),f"{(df.iloc[df['Money out'].idxmax()][2]):,}")
    


    on = st.toggle("See all transactions", key="all")
    if on:
        st.dataframe(df, hide_index=True) 
    select = st.selectbox("Pick A Payer/Payee",pay_places, index=None)
    
    #select row where payment person == this
    on = st.toggle("See all transactions", key="individual")
    if on:
        
        st.dataframe( remaining_rows.loc[remaining_rows.iloc[:,3] == select], hide_index=True)

    selection2 = remaining_rows.loc[remaining_rows.iloc[:,3] == select]
    st.header(select)
    col1,col2 = st.columns(2)
    
    col1.metric("Money received",f"{selection2.iloc[:,0].sum():,}") 
    col2.metric("Money sent",f"{selection2.iloc[:,1].sum():,}") 
   