# -*- coding: utf-8 -*-
"""Gender Representation at the Olympics.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/11Sbe5GxGlztykYxmo4RtMNBKHHaJ3Fk2
"""

"""## Summary


The dataset I chose to study contains historical data from both Summer and Winter Olympics Games from the very beginning in 1896 up until 2016. The data focuses on athlete demographic information as well as sport, team, and medal won (if applicable). I found my data on [Tidy Tuesday](https://github.com/rfordatascience/tidytuesday/blob/master/data/2024/2024-08-06/readme.md).

I wanted to focus on studying patterns among gender in different sports and over time. In the beginning of the semester I started to investigate and demonstrate the question if female representation has increased over time. Since that question was a pretty easy "yes", I started to dive more into the specific sports, team (or country), season, and even specific years to narrow my data. The visualizations below attempt to show the comparison of male versus female representation across different sports and teams over time, allowing users to filter the data as they'd like to find trends in the data.

# Visualizations

Below is a series of visualizations that I'd like to include in my web app.
"""

#Read Data
url = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vRuzokuPJke3HyE-ooCbVKlkyOikFxi3CDQzvosz7KJGf4otbxgH-HWXDpF5iIXTMLGC37rx6mI0VUV/pub?output=csv'

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import base64
import io
from dash import Dash, dcc, html, Input, Output
pd.read_csv(url)

# Load the dataset
df = pd.read_csv(url)

# Filter out years and sports where only Season='Winter' is present
summer_data = df[df['season'] == 'Summer']
valid_years = summer_data['year'].unique()
valid_sports = summer_data['sport'].unique()

# Update dropdown options and slider marks based on filtered data
sports_options = [{'label': sport, 'value': sport} for sport in valid_sports]
year_marks = {str(year): str(year) for year in sorted(valid_years)}

# Function to calculate total athletes and female athletes per team by year and sport
def calculate_team_stats(df, year, sport):
    # Filter by the selected year, sport, and season
    df_filtered = df[(df['year'] == year) & (df['season'] == 'Summer')]
    if sport:
        df_filtered = df_filtered[df_filtered['sport'] == sport]

    # Group by 'team' to calculate total athletes and female athletes
    team_stats = df_filtered.groupby('team').agg(
        total_athletes=('sex', 'count'),
        female_athletes=('sex', lambda x: (x == 'F').sum())
    ).reset_index()

    # Calculate the percentage of female athletes
    team_stats['female_percentage'] = (team_stats['female_athletes'] / team_stats['total_athletes']) * 100
    return team_stats

# Initialize the Dash app
app = Dash("My Dash App")
server = app.server

# Define app layout
app.layout = html.Div([
    html.H1("Gender Representation at the Olympics"),

    # Dropdown for selecting a sport
    dcc.Dropdown(
        id='sport-dropdown',
        options=sports_options,
        placeholder="Select a sport",
        clearable=True
    ),

    # Slider for selecting year
    dcc.Slider(
        id='year-slider',
        min=min(valid_years),
        max=max(valid_years),
        step=1,
        value=min(valid_years),
        marks=year_marks,
    ),

    # Layout for all 3 charts side by side
    html.Div([
        # Choropleth map visualization
        dcc.Graph(id='choropleth-map', style={'display': 'inline-block', 'width': '40%', 'height': '400px'}),

        # Line chart visualization
        dcc.Graph(id='line-chart', style={'display': 'inline-block', 'width': '40%', 'height': '400px', 'margin-top': '20px'}),

        #Sunburst visualization
        dcc.Graph(id='sunburst-chart', style={'display': 'inline-block', 'width': '18%', 'height': '400px', 'margin-top': '20px'}),
    ], style={'text-align': 'center'}),

        # Markdown takeaway section
    html.Div([
        dcc.Markdown(
            """
            **Hover over the choropleth map** to see how specific countries contribute to female representation. Use the dropdown filter to select a specific sport, the timeline feature to select a year, or keep it broad by selecting no filter to explore the gender trends among all combined sports.

            ### Key Takeaways:
            - Countries with higher female participation often show steady increases over time in gender equality.
            - Sports like **swimming** and **gymnastics** show a fairly narrow gap between male and female representation over time. Others like **football** and **weightlifting** don't even show female representation for decades.
            - Medals are distributed fairly evenly between genders in some sports but show disparities in others. You can see for some countries, like the United States in 2012, there was a slightly higher percentage of male athletes at the Olympics, but the representation of medals across all sports shows a majority went to females (almost doubling the amount of medals going to males).
            """
        )
    ], style={
        'margin-top': '20px',
        'padding': '10px',
        'background-color': '#f9f9f9',
        'border': '1px solid #ccc',
        'border-radius': '5px'
    })
    ])

# Define callback to update the map based on the selected year and sport
@app.callback(
    Output('choropleth-map', 'figure'),
    [Input('year-slider', 'value'),
     Input('sport-dropdown', 'value')]
)
def update_map(selected_year, selected_sport):
    # Calculate team stats for the selected year and sport
    team_stats_df = calculate_team_stats(df, selected_year, selected_sport)

    # Create the choropleth map
    fig = px.choropleth(
        team_stats_df,
        locations="team",               # Column with country names (assumes 'team' has country names)
        locationmode="country names",    # Use country names for geographic locations
        color="female_percentage",       # Column to base color on
        color_continuous_scale="RdBu",   # Diverging color scale from Red to Blue
        range_color=(0, 100),            # Set color range from 0% to 100%
    )

    # Center the color scale at 50%
    fig.update_coloraxes(cmid=50)

    # Find the country with the highest number of females
    max_female = team_stats_df.loc[team_stats_df['female_athletes'].idxmax()]

    # Find the country with the highest percentage of females
    max_female_percentage = team_stats_df.loc[team_stats_df['female_percentage'].idxmax()]

    # Add annotation for the country with the highest female percentage below the visualization
    fig.add_annotation(
        text=f"Team with the highest <b>percentage</b> of female athletes: {max_female_percentage['team']} ({max_female_percentage['female_percentage']:.1f}%)</b><br>Team with the highest <b>number</b> of female athletes: {max_female['team']} ({max_female['female_athletes']:.1f})",
        x=max_female['team'],  # Country name
        y=-0.05,  # Position below the map (negative y-value for below the plot area)
        xref="paper",  # Reference to the paper coordinates
        yref="paper",  # Reference to the paper coordinates
        showarrow=True,
        arrowhead=2,
        font=dict(size=14, color="black"),
        align="left"
    )

    # Customize the hover tooltip
    fig.update_traces(
        hovertemplate=(
            "<b>%{location}</b><br>"
            "Female Percentage: %{z:.1f}%<br>"
            "Total Female Athletes: %{customdata[0]}<extra></extra>"  # Displays the total female athletes
        ),
        # Pass the total female athletes as custom data
        customdata=team_stats_df[['female_athletes']].values
    )

    # Update layout
    fig.update_layout(
        legend=dict(font=dict(size=8)),
        margin=dict(t=30, l=10, r=10, b=10),
        coloraxis_colorbar=dict(title='Female Percentage', len=0.5),
        title=dict(
          text=f"Percentage of Female Athletes by Team<br>at the Olympics in {selected_year} (Sport: {selected_sport or 'All'})",
          x=0,  # Align the title to the left
          xanchor="left",  # Anchor the title to the left
          y=0.95,  # Adjust the vertical alignment
          yanchor="top",
          font=dict(size=18, color="black", family="Arial")
    )
    ),

    fig.update_geos(
    showcountries=True,
    countrycolor="lightgrey",  # Set country borders
    showcoastlines=True,
    coastlinecolor="lightgrey",
    showocean=True,
    oceancolor="white",
    bgcolor="white",
    projection_type="equirectangular"
)

    return fig

# Callback to update the line chart based on the selected sport and year
@app.callback(
    Output('line-chart', 'figure'),
    [Input('choropleth-map', 'hoverData'),
     Input('year-slider', 'value'),
     Input('sport-dropdown', 'value')]
)

def update_line_chart(hover_data, selected_year, selected_sport):
    # Extract the hovered team
    hovered_team = hover_data['points'][0]['location'] if hover_data and 'points' in hover_data else None

    # Filter the dataset for 'Summer' and the hovered team (if any)
    df_filtered = df[(df['season'] == 'Summer')]
    if hovered_team:
        df_filtered = df_filtered[df_filtered['team'] == hovered_team]
    if selected_sport:
        df_filtered = df_filtered[df_filtered['sport'] == selected_sport]

    # Group by 'year' and 'sex' to count athletes
    athlete_counts = df_filtered.groupby(['year', 'sex']).size().reset_index(name='count')

    # Create the line chart
    fig = go.Figure()
    for gender, color in zip(['F', 'M'], ['darkblue', 'darkred']):
        gender_data = athlete_counts[athlete_counts['sex'] == gender]
        fig.add_trace(go.Scatter(
            x=gender_data['year'],
            y=gender_data['count'],
            mode='lines+markers',
            name='Female' if gender == 'F' else 'Male',
            line=dict(color=color),
            hovertemplate='Year: %{x}<br>Count of Athletes: %{y}'
        ))


    # Add a vertical line for the selected year
    fig.add_vline(x=selected_year, line_dash="dash", line_color="black", annotation_text=f"Year: {selected_year}", annotation_position="top right")

    # Update layout
    title = f"Athlete Count by Gender Over Time {'for ' + hovered_team if hovered_team else 'Globally'}"
    fig.update_layout(
        title=dict(text=title, x=0, xanchor="left", y=0.95, yanchor="top",
        font=dict(
            size=18,
            color="black",
            family="Arial")),
        xaxis=dict(
            title="Year",
            titlefont=dict(color="black"),  # Title font color
            tickfont=dict(color="black"),  # Tick labels font color
            showgrid=True,                 # Show gridlines
            gridcolor="lightgrey",         # Color of gridlines
            zeroline=True,                 # Show zero line if relevant
            zerolinecolor="black",         # Color of the zero line
            linecolor="black",             # Color of the axis line
            ticks="outside"                # Place ticks outside the chart
        ),
        yaxis=dict(
            title="Count of Athletes",
            titlefont=dict(color="black"),  # Title font color
            tickfont=dict(color="black"),  # Tick labels font color
            showgrid=True,                 # Show gridlines
            gridcolor="lightgrey",         # Color of gridlines
            zeroline=False,                 # Show zero line
            linecolor="black",             # Color of the axis line
            ticks="outside"                # Place ticks outside the chart
        ),
        legend_title="Gender",
        plot_bgcolor="white",  # Set the background color to white
        margin=dict(t=50, l=10, r=10, b=10)
    )

    return fig

# Callback to update the sunburst chart based on the selected year
@app.callback(
    Output('sunburst-chart', 'figure'),
    [Input('choropleth-map', 'hoverData'),
     Input('year-slider', 'value'),
     Input('sport-dropdown', 'value')]
)
def update_sunburst(hover_data, selected_year, selected_sport):
    # Extract the hovered team
    hovered_team = hover_data['points'][0]['location'] if hover_data else None

    # Filter data for the selected year and 'Summer' season
    df_filtered = df[(df['year'] == selected_year) & (df['season'] == 'Summer')]
    if hovered_team:
        df_filtered = df_filtered[df_filtered['team'] == hovered_team]
    if selected_sport:
        df_filtered = df_filtered[df_filtered['sport'] == selected_sport]

    # Group by 'medal' and 'sex' to count occurrences
    medal_counts = df_filtered.groupby(['sex', 'medal']).size().reset_index(name='count')

    # Define static colors for the sunburst
    colors = {'F': 'darkblue', 'M': 'darkred'}

    # Create the sunburst chart
    fig = px.sunburst(
        medal_counts,
        path=['sex', 'medal'],  # Hierarchical path: Gender > Medal type
        values='count',
        title=(
            f"Medal Counts by Gender for {selected_year} "
            f"{f'(Team: {hovered_team})' if hovered_team else '(Global)'}"
        ),
        color='sex',  # Use 'sex' for static color assignment
        color_discrete_map=colors  # Static color map
    )

    # Customize hover information
    fig.update_traces(
        hovertemplate=(
            "Gender: %{parent}<br>"  # For medal nodes
            "Medal: %{label}<br>"
            "Count: %{value}<extra></extra>"
        ),
        selector=dict(type="sunburst")  # Apply to all nodes in the sunburst
    )

    # Set hover data for parent (gender) nodes specifically
    for trace in fig.data:
        if 'labels' in trace and 'parents' in trace:
            trace['hovertemplate'] = [
                f"Gender: {label}<br>Count: {value}<extra></extra>"
                if parent == "" else  # For top-level gender nodes
                f"Gender: {parent}<br>Medal: {label}<br>Count: {value}<extra></extra>"
                for label, parent, value in zip(trace['labels'], trace['parents'], trace['values'])
            ]

    # Update layout
    fig.update_layout(
        margin=dict(t=50, l=10, r=10, b=10),
        title=dict(
            text=f"Medal Counts by Gender {'for ' + hovered_team if hovered_team else 'Globally'}",
            x=0, xanchor="left", y=0.95, yanchor="top",
            font=dict(
            size=18,
            color="black",
            family="Arial")),
        showlegend=False  # Remove legend
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True, jupyter_mode="external")
