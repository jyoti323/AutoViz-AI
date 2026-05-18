import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="AutoViz AI",
    page_icon="",
    layout="wide"
)

st.markdown("""
    <style>

    .main {
        background-color: #0E1117;
        color: white;
    }

    h1 {
        color: #00FFFF;
        text-align: center;
    }

    .stButton>button {
        background-color: #00FFFF;
        color: black;
        border-radius: 10px;
        height: 3em;
        width: 100%;
    }

    .stFileUploader {
        border: 2px dashed #00FFFF;
        padding: 10px;
        border-radius: 10px;
    }

    </style>
""", unsafe_allow_html=True)


st.sidebar.title("Dashboard Menu")

st.sidebar.info("""
Upload a CSV file and let AI analyze your data automatically.
""")

# App title
st.title("AI Data Visualization Assistant")

# Upload CSV
uploaded_file = st.file_uploader(
    "Upload your CSV file",
    type=["csv"]
)




# If file uploaded
if uploaded_file is not None:

    # Read CSV
    df = pd.read_csv(uploaded_file)

    # Dataset preview
    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Dataset shape
    st.subheader("Dataset Shape")
    col1, col2 = st.columns(2)

    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])

    # Statistics
    st.subheader("Dataset Statistics")
    st.write(df.describe())

    # Detect columns
    numeric_columns = df.select_dtypes(include=['number']).columns
    categorical_columns = df.select_dtypes(include=['object']).columns

    # Show column types
    st.subheader("Numeric Columns")
    st.write(numeric_columns)

    st.subheader("Categorical Columns")
    st.write(categorical_columns)

    # Scatter plot
    if len(numeric_columns) >= 2:

        x_column = numeric_columns[0]
        y_column = numeric_columns[1]

        st.subheader("Automatic Scatter Plot")

        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{x_column} vs {y_column}"
        )

        st.plotly_chart(fig)

    # Bar chart
    if len(categorical_columns) > 0 and len(numeric_columns) > 0:

        cat_column = categorical_columns[0]
        num_column = numeric_columns[0]

        st.subheader("Automatic Bar Chart")

        fig = px.bar(
            df,
            x=cat_column,
            y=num_column,
            title=f"{num_column} by {cat_column}"
        )

        st.plotly_chart(fig)

    # Histogram
    if len(numeric_columns) > 0:

        st.subheader("Histogram")

        fig = px.histogram(
            df,
            x=numeric_columns[0],
            title=f"Distribution of {numeric_columns[0]}"
        )

        st.plotly_chart(fig)