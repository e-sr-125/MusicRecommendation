import streamlit as st
from spotify_recommendation_project import hybrid_recommendation,music_df

st.title('Music Recommendation system')
st.write('Enter a song in your playlist to get the recommendation')
song_input=st.text_area('playlist')
if st.button('Get recommendations'):
    if song_input:
        recommendations=hybrid_recommendation(song_input,10)
        st.write('Recommended songs:')
        # for song in recommendations:
        #     st.write(song)
        st.write(recommendations)
    else:
        st.write('Please enter a playlist.')

