# YouTube Analytics Tool

See the source code here: [https://github.com/fontanads/ytbot](https://github.com/fontanads/ytbot).  

This is a personal project experimenting with the YouTube API.  
This was made to practice and for fun, so don't expect much from it, it is a WIP without a deadline.  

<iframe width="560" height="315" src="https://www.youtube.com/embed/CENftD5GBHo" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

_Disclaimer_: some code has been written with help of our coding buddy Chat GPT and GitHub Copilot on VS Code, which was also a part of the project - experimenting with AI aid in writing code. However, almost every snippet that came out of the generative AI outputs has been modified to some extent. In general, my experience is iteratively going back and forth until you achieve the functionality you desired. So I'd say this is more like an "AI-in-the-loop" codestyle.

Current functionality includes:
- API requests to collect trending video statistics and metadata
- upload to Big Query tables
- a Streamlit app with a simple dashboard displaying the collected data.  


1. [Installing the project](#installing-the-project)  
2. [YouTube API Credentials](#credentials-for-the-api)
3. [Getting data for trending videos](#trending-videos-by-country)
4. [Big Query API](#big-query-api-to-upload-data)
5. [Streamlit Dashboard](#streamlit-dashboard)  


## Installing the project

The dependencies are found in the `pyproject.toml` file.
I suggest you use [`poetry`](https://python-poetry.org/) to install the dependencies.  
Once you have poetry installed and configured, run `poetry install` in the folder you cloned the repo.  Use `poetry shell` to spin up the Python virtual environment manually and run any scripts of the project.


## Credentials for the API

To instantiate the API class, it is necessary to deal with the credentials.  
This version requires manual authentication on browser.  

First step is authorizing the credentials on your Google Cloud Platform (GCP) project.  
Follow [this link](https://developers.google.com/youtube/registering_an_application#create_project) for detailed instructions.  


Once you've been through the steps above, you'll be able to see the API listed in your GCP project: [`https://console.cloud.google.com/apis/dashboard?project=YOUR_PROJECT_ID`](https://console.cloud.google.com/apis/dashboard).

The code is taking a variable `YOUTUBE_CLIENT_SECRET_FILE` from a `.env` file (not in the repo, you need to create it yourself). This variable contains just the path to the JSON file with the API secret. The JSON file follows this format:
```
{
	"web":
	{
		"client_id":"YOUR_CLIENT_ID.apps.googleusercontent.com",
		"project_id":"GCP_PROJECT_ID",
		"auth_uri":"https://accounts.google.com/o/oauth2/auth",
		"token_uri":"https://oauth2.googleapis.com/token",
		"auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs",
		"client_secret":"YOUR_CLIENT_SECRET"
	}
}
```

Feel free to change this implementation modifying `__init__` method of `YouTube` class in [`src/core/youtube.py`](src/core/youtube.py).

## Trending videos by country

The script is found in [`src/analytics/trending_videos_by_country.py`](src/analytics/trending_videos_by_country.py).  

It requests data from trending videos (descending order by view count) per region with no specific topic query. It goes over a list of regions (country codes) and deals with pagination to retrieve a maximum number of video ids.  

A second request implements a batch request of statistics and metadata for the listed videos in the first search.  

Be mindful with the [quota limits of the YouTube API](https://developers.google.com/youtube/v3/determine_quota_cost).  

## Big Query API to Upload Data

The code for the use of the API is found here: [`src/cloud/bigquery.py`](src/cloud/bigquery.py).  
Credentials here are not being passed explicitly, if you want to change its implementation modify the `__init__` method of the `BigQueryClient` class.  
To use it from your local machine without writing a new implementation to deal with the credentials, configure your GCP client [following instructions here](https://cloud.google.com/bigquery/docs/bigquery-web-ui#before_you_begin).  

The method `upload_dataframe` is the one with more implementation details. It has input flags to delete the destination table, in case it exists, and also to overwrite date partitions.

## Streamlit Dashboard

The source code is in [`src/dashboard/app.py`](src/dashboard/app.py).  
To run the application, run this command your terminal:  
```bash
streamlit run src/dashboard/app.py 
```  

The Big Query client has `download_table` that is used in the dashboard to collect the data. The helper functions in the app code use the Streamlit decorator `@st.cache_data` to cache the downloaded DataFrames while the app is executing. Each region table is downloaded separetely running a filtered query. Changing between regions in the drop-down menu **does not** reset the cache.
