import altair as alt


class ChannelCharts:
    def __init__(self, df, min_opacity=0.3):
        self.df = df
        self.min_opacity = min_opacity
        self.first_channel_id = self.df.sort_values(by='like_count', ascending=False)['channel_id'].iloc[0]
        self.highlight_selection = self.get_selection(highlight=self.first_channel_id)

    def get_selection(self, highlight=None):
        return alt.selection(
            type='single',
            on='mouseover',
            fields=['channel_id'],
            nearest=True,
            empty='none',
            init={'channel_id': highlight},
            bind='legend'
        )

    def view_count_videos_df_view(self, max_videos=10):
        return self.df.sort_values(by='view_count', ascending=False).head(max_videos)

    def like_count_channels_df_view(self, max_channels=10):
        like_df = self.df.groupby(['channel_title', 'channel_id']).agg({'like_count': 'sum', 'title': 'count'}).reset_index()
        like_df = like_df.sort_values(by='like_count', ascending=False).head(max_channels)
        return like_df

    def create_view_count_chart(self, data=None, max_videos=10, default_color='#7fc7ff', highlight_color='#F63366'):

        if data is None:
            data = self.view_count_videos_df_view(max_videos=max_videos)

        base_chart = alt.Chart(data).mark_bar().encode(
            x=alt.X('view_count', axis=alt.Axis(format=',d'), title='View Count'),
            y=alt.Y('title', sort='-x', title='Video Title'),
            tooltip=[
                alt.Tooltip('title', title='Title'),
                alt.Tooltip('channel_title', title='Channel'),
                alt.Tooltip('view_count', title='View Count', format=','),
                alt.Tooltip('like_count', title='Like Count', format=','),
                alt.Tooltip('comment_count', title='Comment Count', format=','),
                alt.Tooltip('published_at', title='Published Date', format='%Y-%m-%d'),
            ],
            color=alt.condition(
                self.highlight_selection,
                alt.value(highlight_color),
                alt.value(default_color)),
            opacity=alt.condition(
                self.highlight_selection,
                alt.value(1),
                alt.value(self.min_opacity))
        )

        view_count_chart = (base_chart).add_selection(self.highlight_selection)
        # Set chart properties
        view_count_chart = view_count_chart.properties(
            title=alt.TitleParams(f'Top {max_videos} Videos by Total Views', anchor='middle')
        )
        return view_count_chart

    def create_like_count_chart(self, data=None, max_channels=10, default_color='#7fffc7', highlight_color='#F66633'):
        if data is None:
            data = self.like_count_channels_df_view(max_channels=max_channels)

        # Create base chart with horizontal bar
        base_chart = alt.Chart(data).mark_bar().encode(
            y=alt.Y('like_count', axis=alt.Axis(format=',d'), title='Total Likes'),
            x=alt.X('channel_title', sort='-y', title='Channel', axis=alt.Axis(labelAngle=-90)),
            tooltip=[
                alt.Tooltip('channel_title', title='Channel'),
                alt.Tooltip('like_count', title='Like Count', format=',')],
            color=alt.condition(
                self.highlight_selection,
                alt.value(highlight_color),
                alt.value(default_color)),
            opacity=alt.condition(
                self.highlight_selection,
                alt.value(1),
                alt.value(self.min_opacity))
        )

        # Combine base and highlighted chart, and add selection
        like_count_chart = base_chart.add_selection(self.highlight_selection)

        # Set chart properties
        like_count_chart = like_count_chart.properties(
            title=alt.TitleParams(f'Top {max_channels} Channels by Total Likes', anchor='middle')
        )

        return like_count_chart

    def update_highlight(self, channel_id):
        # TODO: find out how to bind the execution of this function to the selection of the chart

        # Update the highlight selection
        self.highlight_selection = self.get_selection(highlight=channel_id)

        # Update the view count chart
        self.view_count_chart = self.create_view_count_chart(highlight=channel_id)

        # Update the like count chart
        self.like_count_chart = self.create_like_count_chart(highlight=channel_id)
