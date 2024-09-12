import streamlit as st
import requests
from bs4 import BeautifulSoup
import time


  
  
def home_page():
    st.title('Real-Time News Headlines with Summaries')

    url = 'https://www.moneycontrol.com/news/stocksinnews-142.html'  # Replace with your actual URL

    st.sidebar.header('Settings')
    refresh_interval = st.sidebar.slider('Refresh Interval (seconds)', min_value=5, max_value=60, value=30)

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        
        headlines = soup.find_all('h2')  # Adjust as needed
        summaries = soup.find_all('p')   # Adjust as needed

        data = []
        for headline, summary in zip(headlines, summaries):
            data.append({
                'headline': headline.text.strip(),
                'summary': summary.text.strip()
            })

        headlines = [item['headline'] for item in data]
        selected_headline = st.selectbox('Select a headline', headlines, key='headline_selectbox')

        for item in data:
            if item['headline'] == selected_headline:
                st.write(f"**{item['headline']}**")
                st.write(item['summary'])
                break

        st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        if st.button('Refresh Now'):
            response = requests.get(url)
            if response.status_code == 200:
                html_content = response.text
                soup = BeautifulSoup(html_content, 'html.parser')
                
                headlines = soup.find_all('h2')  # Adjust as needed
                summaries = soup.find_all('p')   # Adjust as needed

                data = []
                for headline, summary in zip(headlines, summaries):
                    data.append({
                        'headline': headline.text.strip(),
                        'summary': summary.text.strip()
                    })

                headlines = [item['headline'] for item in data]
                selected_headline = st.selectbox('Select a headline', headlines, key='headline_selectbox')

                for item in data:
                    if item['headline'] == selected_headline:
                        st.write(f"**{item['headline']}**")
                        st.write(item['summary'])
                        break

                st.write(f"Last updated: {time.strftime('%Y-%m-%d %H:%M:%S')}")
