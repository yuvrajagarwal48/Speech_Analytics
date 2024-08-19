import streamlit as st
from speech_analysis import give_analysis

st.set_page_config(page_title="Speaker Analytics")
st.title("Speaker Analytics Dashboard")

# Upload the DOCX file
uploaded_file = st.file_uploader("Upload DOCX file", type="docx")
analyzing_info=''

# Initialize session state for analytics
if 'analytics' not in st.session_state:
    st.session_state.analytics = {}
    st.session_state.speaker_names = []

if uploaded_file:
    # Input for speakers
    speaker_names = st.text_area("Enter speaker names separated by commas").split(",")
    submit_button = st.button("Submit")

    if submit_button:
        if speaker_names and speaker_names != st.session_state.speaker_names:
            # Only run the analysis if the speaker names have changed
            st.session_state.analytics = give_analysis(uploaded_file, speaker_names)
            st.session_state.speaker_names = speaker_names

def st_dashboard(analytics):
    selected_speaker = st.selectbox("Select a speaker to display analytics", st.session_state.speaker_names)
    if selected_speaker:
        # Display the analytics for the selected speaker
        st.subheader(f"Analytics for {selected_speaker}")
        data = analytics[selected_speaker]
        st.write(f"**Total Words Spoken:** {data['Total Words Spoken']}")
        st.write(f"**Total Sentences Spoken:** {data['Total Sentences Spoken']}")
        st.write(f"**Most Common Words:** {data['Most Common Words']}")
        st.write(f"**Filler Frequency:** {data['Filler Frequency']}")
        st.write(f"**Average Sentence Length:** {data['Average Sentence Length']:.2f} characters")
        st.write(f"**Clarity (Flesch Reading Ease):** {data['Clarity']:.2f}")
        st.write(f"**Tone:** {data['Tone'][0]} (Polarity: {data['Tone'][1]:.2f})")
        st.write(f"**Vocabulary Diversity:** {data['Vocabulary Diversity']:.2f}")
        st.write(f"**Question Frequency:** {data['Question Frequency']}")
        st.write(f"**Summary:** {data['Summary']}")
        
        if data['Grammar Issues']:
            st.write("**Grammar Issues:**")
            for i, issue in enumerate(data['Grammar Issues']):
                st.write(f"**Mistake {i+1}:**")
                st.write(f"***Sentence:*** {issue['Sentence']}")
                st.write(f"***Mistake:*** {issue['Mistake']}")
                st.write(f"***Suggestion:*** {', '.join(issue['Suggestion'])}")

if uploaded_file and st.session_state.analytics:
    st_dashboard(st.session_state.analytics)

