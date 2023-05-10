import streamlit as st
from streamlit_lottie import st_lottie_spinner
import pickle
import json
from inputSample import *

def main():
    st.title("URL Phishing Detection")
    url = st.text_input("Enter the URL: ")
    
    detection = ""
    loadLogo = json.load(open('gears.json','r'))
    if st.button("Detect"):
        display = st.empty()
        msg = st.empty()
        print(url)
        if url:
            with st_lottie_spinner(loadLogo, key="load"):
                detection = ""
                prepared_input = prepare_input(url)
                detection = make_prediction(prepared_input)
            
            display.write(prepared_input)
            if detection == 1:
                msg.error("Phishing Link")
            if detection == 0:
                msg.success("Not a Phishing")
                st.balloons()
        else:
            msg.warning("Please check if the Input is empty")
    
    

if __name__ == '__main__':
    main()