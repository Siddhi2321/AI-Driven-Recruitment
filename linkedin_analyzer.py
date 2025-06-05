import streamlit as st
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Set page title only if running standalone
if __name__ == "__main__":
    st.set_page_config(page_title="LinkedIn Analytics Dashboard", layout="wide")

# RapidAPI Key for LinkedIn post extraction
RAPID_API_KEY = os.getenv("RAPID_API_KEY")

def fetch_linkedin_post_data(profile_url):
    """Fetch LinkedIn post data using RapidAPI."""
    api_url = "https://fresh-linkedin-profile-data.p.rapidapi.com/get-profile-posts"
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
        "X-RapidAPI-Host": "fresh-linkedin-profile-data.p.rapidapi.com"
    }
    querystring = {"linkedin_url": profile_url, "type": "posts"}
    response = requests.get(api_url, headers=headers, params=querystring)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def analyze_post_data(json_data):
    """Process and visualize the LinkedIn post data."""
    data = json_data['data'][:10]  # First 10 posts

    post_urls = [item['post_url'] for item in data]
    num_likes = [item.get('num_likes', 0) for item in data]
    num_comments = [item.get('num_comments', 0) for item in data]
    num_reposts = [item.get('num_reposts', 0) for item in data]

    total_likes = sum(num_likes)
    total_impressions = total_likes + sum(num_reposts)
    total_engagements = total_likes

    col1, col2, col3 = st.columns(3)
    col1.metric("👍 Total Likes", total_likes)
    col2.metric("👀 Total Impressions", total_impressions)
    col3.metric("💬 Total Engagements", total_engagements)

    df = pd.DataFrame({
        'Post URL': post_urls,
        'Number of Likes': num_likes,
        'Number of Comments': num_comments,
        'Number of Reposts': num_reposts,
    })

    st.subheader("📊 Engagement Trends")
    col_likes, col_comments = st.columns(2)
    with col_likes:
        st.bar_chart(df['Number of Likes'])
    with col_comments:
        st.bar_chart(df['Number of Comments'])

    st.subheader("📌 Top Posts Table")
    st.table(df)

    top_post = df.sort_values("Number of Likes", ascending=False).iloc[0]
    insight = f"Most Liked Post: {top_post['Post URL']}, with {top_post['Number of Likes']} likes and {top_post['Number of Reposts']} reposts."
    st.info(insight)

    st.subheader("📈 Engagement Area Chart")
    st.area_chart(df[['Number of Likes', 'Number of Reposts']])

    return insight

def show_linkedin_analyzer():
    st.title("🔗 LinkedIn Profile Analyzer")
    st.write("Analyze public LinkedIn profile post performance using AI-powered insights.")

    profile_url = st.text_input("Paste your public LinkedIn profile URL")

    if st.button("🔍 Analyze Profile"):
        if not profile_url:
            st.warning("Please enter a valid LinkedIn profile URL.")
            return

        with st.spinner("Fetching and analyzing LinkedIn post data..."):
            json_data = fetch_linkedin_post_data(profile_url)
            if not json_data or 'data' not in json_data:
                st.error("Failed to fetch data. Please check the profile URL or API key.")
                return

            insight = analyze_post_data(json_data)

            st.subheader("🧠 AI Summary")
            st.write(f"This LinkedIn profile shows active engagement. {insight}")

            st.subheader("💡 Recommendations")
            st.write("Consider posting more consistently, engaging with comments, and leveraging reposts for increased impressions.")

# If running directly
if __name__ == "__main__":
    show_linkedin_analyzer()
