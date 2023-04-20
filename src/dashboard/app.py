import streamlit as st
import altair as alt
from datetime import datetime, timedelta
from src.cloud.bigquery import BigQueryClient


# function to download the data from BigQuery
@st.cache_data()
def download_table(country_code, date_range, dataset_id="youtube", table_prefix="trending"):
    """
    Downloads data from BigQuery table for given country code and date range
    """
    # create a BigQuery client object
    bigquery_client = BigQueryClient(project_id="sandbox-381517")
    table_id = f"{table_prefix}_{country_code}"
    # construct SQL query to download data for the given country code and date range
    query = f"""
            SELECT *
            FROM `{dataset_id}.{table_id}`
            WHERE published_at >= '{date_range[0].strftime('%Y-%m-%d')}'
            AND published_at <= '{date_range[1].strftime('%Y-%m-%d')}'
            """

    # download the table
    table = bigquery_client.download_table(query=query, dataset_id=dataset_id, table_id=table_id)

    return table


# Define functions to create charts
def view_count_chart(df, max_videos):
    df = df.sort_values(by='view_count', ascending=False).head(max_videos)
    chart = alt.Chart(df).mark_bar().encode(
        x='view_count',
        y=alt.Y('title', sort='-x')
    ).properties(title=f'Top {max_videos} Most Viewed Videos')
    return chart


def like_count_chart(df):
    df = df.groupby('channel_id').agg({'like_count': 'sum', 'title': 'count'}).reset_index()
    df = df.sort_values(by='like_count', ascending=False).head(5)
    chart = alt.Chart(df).mark_bar().encode(
        x='like_count',
        y=alt.Y('channel_id', sort='-x'),
        tooltip=['channel_id', 'like_count', 'title']
    ).properties(title='Top 5 Channels by Like Count')
    return chart


# Main function
def main():
    # Set up page
    st.set_page_config(page_title='Trending Videos Dashboard', page_icon=':chart_with_upwards_trend:')
    st.title('Trending Videos Dashboard')
    st.write('This dashboard has been created using Chat GPT in collaboration with the author.')

    # Get user input
    countries = ['US', 'GB', 'IN', 'JP']
    country_code = st.sidebar.selectbox('Select a country code:', countries)
    end_date = datetime.now().date()
    start_date = st.date_input('Select start date:', value=(end_date - timedelta(days=7)))
    if start_date > end_date:
        st.error('Error: Start date must be before end date.')
        return
    elif end_date - start_date > timedelta(days=30):
        st.warning('Warning: Maximum date range is 30 days.')
        end_date = start_date + timedelta(days=30)
    else:
        end_date = end_date
        start_date = start_date

    date_range = [start_date, end_date]
    # Download data from BigQuery
    df = download_table(country_code, date_range)

    # Divide the page into two columns
    col1, col2 = st.columns(2)

    # Create charts
    # TODO: there are repeated rows in the dataset, find out why and fix it
    max_videos = st.slider('Select max number of videos to show:', min_value=5, max_value=20, value=10)
    view_count_chart_obj = view_count_chart(df, max_videos=max_videos)
    col1.altair_chart(view_count_chart_obj, use_container_width=True)
    col1.write(f'The above chart shows the top {max_videos} most viewed videos in {country_code} between {start_date} and {end_date}.')

    # Second chart: Top channels by like count
    like_count_chart_obj = like_count_chart(df)
    col2.altair_chart(like_count_chart_obj, use_container_width=True)
    col2.write('The above chart shows the top 5 channels by total like count for videos in the selected date range.')


if __name__ == '__main__':
    main()