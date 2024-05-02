import pandas as pd
import streamlit as st
from pandas.api.types import is_object_dtype
import streamlit.components.v1 as components


class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    to_filter_columns = st.multiselect("Filter results by", df.columns, key="filter_columns")

    for column in to_filter_columns:
        left, right = st.columns((1, 20))
        left.write("↳")

        if is_object_dtype(df[column]):
            user_text_input = right.text_input(
                f"Search by {column}",
                key=f"text_{column}"
            )
            if user_text_input:
                df = df[df[column].str.contains(user_text_input, case=False, na=False)]
        else:
            column_min = df[column].min()
            column_max = df[column].max()
            step = (column_max - column_min) / 100
            user_num_input = right.slider(
                f"Values for {column}",
                float(column_min),
                float(column_max),
                (float(column_min), float(column_max)),
                step=step,
            )
            df = df[df[column].between(*user_num_input)]

    return df


def display_songs(df: pd.DataFrame, num_results: int):
    session_state = SessionState(displayed_songs=[])

    filtered_df = df[~df["track_uri"].isin(session_state.displayed_songs)].copy()
    filtered_df = filtered_df.sample(frac=1).reset_index(drop=True)

    if len(filtered_df) == 0:
        st.write("No more results to display.")
        return

    num_displayed = len(session_state.displayed_songs)
    remaining_df = filtered_df.iloc[num_displayed:]

    if len(remaining_df) == 0:
        st.write("No more results to display.")
        return

    if len(remaining_df) <= num_results:
        display_df = remaining_df
    else:
        display_df = remaining_df.iloc[:num_results]

    for i, result in display_df.iterrows():
        track_uri = result['track_uri']
        html_string = f'<div style="left: 0; width: 100%; height: 380px; position: relative;"><iframe src="https://open.spotify.com/embed/track/{track_uri}?utm_source=oembed" style="top: 0; left: 0; width: 100%; height: 100%; position: absolute; border: 0;" allowfullscreen allow="clipboard-write; encrypted-media; fullscreen; picture-in-picture;"></iframe></div>'
        st.markdown(html_string, unsafe_allow_html=True)
        session_state.displayed_songs.append(track_uri)

def main():

    from PIL import Image

    im = Image.open('spotify_search_engine/images/download (1).jpg')

    st.set_page_config(page_title="Spotify Search Engine", page_icon=im, layout="wide")

    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)

    st.title("🔍 Spotify Search Engine")
    st.markdown("Find new songs by searching with different tags.")

    file1_path = "spotify_search_engine/data/half1.csv"
    file2_path = "spotify_search_engine/data/half2.csv"

    # Read the two CSV files into DataFrames
    df1 = pd.read_csv(file1_path)
    df2 = pd.read_csv(file2_path)

    df = pd.concat([df1, df2])

    filtered_df = filter_dataframe(df)

    st.header("Showing results...")
    num_results = 5
    display_songs(filtered_df, num_results)
    num_results = 0
    if len(filtered_df) > num_results:
        show_other = st.button("Show Other")
        if show_other:
            display_songs(filtered_df, num_results)

    st.header("Filtered Results Information")
    st.dataframe(filtered_df)

    st.header("Additional Information")
    st.markdown("Search for songs based on different criteria.")
    st.markdown("Columns used for search:")
    st.markdown("- **Title**: The title of the song.")
    st.markdown("- **Artist**: The artist of the song.")
    st.markdown("- **Genre**: The genre of the artist.")
    st.markdown("- **Duration**: The duration of the track in ms.")
    st.markdown("- **Type**: Album, single, or compilation.")
    st.markdown("- **Danceability**: A measure of how suitable a track is for dancing based on a combination of musical elements.")
    st.markdown("- **Energy**: Represents the intensity and activity level of a track.")
    st.markdown("- **Loudness**: The overall loudness of a track in decibels (dB).")
    st.markdown("- **Speechiness**: Indicates the presence of spoken words in a track. Higher values indicate more spoken words.")
    st.markdown("- **Acousticness**: Represents the likelihood of a track being acoustic (i.e., without electronic amplification).")
    st.markdown("- **Instrumentalness**: Measures the amount of instrumental content in a track. Higher values suggest instrumental tracks.")
    st.markdown("- **Liveness**: Represents the probability of a track being performed live. Higher values indicate a live performance.")
    st.markdown("- **Valence**: Describes the musical positivity of a track. Higher values represent more positive (happy) tracks.")
    st.markdown("- **Tempo**: The overall estimated tempo of a track in beats per minute (BPM).")

    footer_container = st.container()
    footer_container.image("spotify_search_engine/images/download (2).jpg", use_column_width=True)
    st.markdown("###### Note: The data used was last updated on 21/05/2023 and was gathered using spotipy.", unsafe_allow_html=True)
    st.markdown("If you would like to keep using this tool please consider supporting the project.", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
