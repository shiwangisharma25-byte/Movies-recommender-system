import streamlit as st
import pickle
import pandas as pd
import os

# ── Set base path to where all pkl files are ─────────────────────────────────
BASE_DIR = r'C:\Users\Shivangi\PycharmProjects\PythonProject\Movies-recommender-system'

# ── Load Data ─────────────────────────────────────────────────────────────────
movies_dict  = pickle.load(open(os.path.join(BASE_DIR, 'movie_dict.pkl'),    'rb'))
movies       = pd.DataFrame(movies_dict)

details_dict = pickle.load(open(os.path.join(BASE_DIR, 'movie_details.pkl'), 'rb'))
details_df   = pd.DataFrame(details_dict)

similarity   = pickle.load(open(os.path.join(BASE_DIR, 'similarity.pkl'),    'rb'))

# ── Fix types ─────────────────────────────────────────────────────────────────
movies['title']     = movies['title'].astype(str).str.strip()
details_df['title'] = details_df['title'].astype(str).str.strip()


# ── Helper Functions ──────────────────────────────────────────────────────────
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(
        list(enumerate(similarity[index])),
        reverse=True,
        key=lambda x: x[1]
    )
    return [movies.iloc[i[0]].title for i in distances[1:6]]


def clean_field(val):
    if isinstance(val, list):
        return ', '.join([str(v) for v in val])
    if isinstance(val, str):
        cleaned = val.strip("[]").replace("'", "").strip()
        return cleaned if cleaned else 'N/A'
    return 'N/A'


def get_details(movie_title):
    movie_title = str(movie_title).strip()
    mask = details_df['title'] == movie_title

    if mask.sum() == 0:
        return {
            'overview': 'No description available.',
            'genres'  : 'N/A',
            'keywords': 'N/A',
            'cast'    : 'N/A',
            'crew'    : 'N/A',
        }

    row = details_df[mask].iloc[0]

    # overview was split into a list in notebook — rejoin
    overview = row['overview']
    if isinstance(overview, list):
        overview = ' '.join(overview)

    return {
        'overview': overview if overview else 'No description available.',
        'genres'  : clean_field(row['genres']),
        'keywords': clean_field(row['keywords']),
        'cast'    : clean_field(row['cast']),
        'crew'    : clean_field(row['crew']),
    }


# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

# ── Movie Selector ────────────────────────────────────────────────────────────
selected_movie = st.selectbox('🎥 Select a Movie:', movies['title'].values)

# ── Selected Movie Detail Card ────────────────────────────────────────────────
info = get_details(selected_movie)

st.markdown("---")
st.subheader(f"📽️ {selected_movie}")

col1, col2 = st.columns([2, 1])

col1.markdown("### 📝 Description")
col1.write(info['overview'])

col2.markdown("### 🎭 Cast")
col2.write(info['cast'])

col2.markdown("### 🎬 Director")
col2.write(info['crew'])

col2.markdown("### 🎞️ Genres")
col2.write(info['genres'])

col2.markdown("### 🔑 Keywords")
col2.write(info['keywords'])

# ── Recommendations ───────────────────────────────────────────────────────────
st.markdown("---")
if st.button('🔍 Recommend Similar Movies'):
    recommended = recommend(selected_movie)

    st.subheader("🎯 Top 5 Similar Movies")
    cols = st.columns(5)

    for col, name in zip(cols, recommended):
        rec = get_details(name)
        col.markdown(f"**🎬 {name}**")
        col.markdown("**Genres:**")
        col.caption(rec['genres'])
        col.markdown("**Cast:**")
        col.caption(rec['cast'])
        col.markdown("**Director:**")
        col.caption(rec['crew'])
        col.markdown("**Overview:**")
        preview = rec['overview'][:120] + "..." if len(rec['overview']) > 120 else rec['overview']
        col.caption(preview)
        col.markdown("---")