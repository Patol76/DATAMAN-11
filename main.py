import streamlit as st
import distutils.core
# Import page functions
from home import home_page
from technical_analysis import technical_analysis_page
from future_forecast import future_forecast_page # type: ignore

def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select navigation bar:", ['Home', 'Technical Analysis', 'Future Forecast'])

    if page == "Home":
        home_page()
    elif page == "Technical Analysis":
        technical_analysis_page()
    elif page == "Future Forecast":
        future_forecast_page()

if __name__ == "__main__":
    main()
