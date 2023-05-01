import pandas as pd
import streamlit as st
import altair as alt
from datetime import datetime, timedelta
from src.cloud.bigquery import BigQueryClient
from src.dashboard.charts import ChannelCharts


# function to download the data from BigQuery
@st.cache_data()
def download_table(country_code, date_range, dataset_id="youtube", table_id="trending"):
    """
    Downloads data from BigQuery table for given country code and date range
    """
    # create a BigQuery client object
    bigquery_client = BigQueryClient(project_id="sandbox-381517")

    # construct SQL query to download data for the given country code and date range
    query = f"""
            SELECT *
            FROM `{dataset_id}.{table_id}`
            WHERE published_at >= '{date_range[0].strftime('%Y-%m-%d')}'
            AND published_at <= '{date_range[1].strftime('%Y-%m-%d')}'
            AND region_code = '{country_code}'
            """

    # download the table
    table = bigquery_client.download_table(query=query, dataset_id=dataset_id, table_id=table_id)

    return table


# Main function
def main():
    # Set up page
    st.set_page_config(page_title='Trending Videos Dashboard', page_icon=':chart_with_upwards_trend:')
    st.title('Trending Videos Dashboard')
    st.write('This dashboard has been created using Chat GPT in collaboration with the author.')

    # Get user input
    countries = ["UK", "US", "BR", "DE", "FR", "MX"]
    country_code = st.sidebar.selectbox('Select a country code:', countries)
    end_date = datetime.now().date()
    start_date = st.sidebar.date_input('Select start date:', value=(end_date - timedelta(days=7)))
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
    df['published_at'] = pd.to_datetime(df['published_at'], format='%Y-%m-%d')

    # Create charts
    charts = ChannelCharts(df)

    max_videos = st.sidebar.slider('Select max number of videos to show:', min_value=5, max_value=20, value=10)
    max_channels = st.sidebar.slider('Select max number of channels to show:', min_value=1, max_value=10, value=5)

    c1 = charts.create_view_count_chart(max_videos=max_videos).properties(title="", width=600)
    c2 = charts.create_like_count_chart(max_channels=max_channels).properties(title="", width=600, height=200)
    hchart = (c1 & c2)
    st.altair_chart(hchart)

    # Divide the page into two columns
    # col1, col2 = st.columns(2)
    # with col1:
    #     max_videos = st.slider('Select max number of videos to show:', min_value=5, max_value=20, value=10)
    #     view_count_chart = charts.create_view_count_chart(max_videos=max_videos)
    #     st.altair_chart(view_count_chart, use_container_width=True)
    #     st.write(f'The above chart shows the top {max_videos} most viewed videos in {country_code} between {start_date} and {end_date}.')

    # with col2:
    #     max_channels = st.slider('Select max number of channels to show:', min_value=1, max_value=10, value=5)
    #     like_count_chart = charts.create_like_count_chart(max_channels=max_channels)
    #     st.altair_chart(like_count_chart, use_container_width=True)
    #     st.write('The above chart shows the top 5 channels by total like count for videos in the selected date range.')


if __name__ == '__main__':
    main()
