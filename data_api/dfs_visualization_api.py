# Importing data ingestion engine to access data from dfsu files:
from * import dfs_ingestion_api.dfsu_ingestion_engine as dfsu_ingestion_engine
# Importing data management packages:
import math
import pandas as pd
import json
# Importing data visualization packages:
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
# Importing Dash library packages:
import dash
import dash_core_components as dcc
import dash_html_components as html

# Class that handels and processes the model's map and other GIS data:
class gis_model(object):
    """
    This object is used to store information and build data structures about
    the GIS model for a specific client Dashboard. The main data structures
    generated by input parameters are used to create an interactive Matchbox
    map.

    Parameters
    ----------
    center_loc : tuple
        A tuple of (lat,long) data that represents the center of the map area.
        This tuple would be used to center the Scattermapbox satellite map.

    client_model : str
        The string representing the name of the client model that the object is
        plotting. It will be used to query data from the file directory via
        the data API.

    access_token : str
        The access token for the Mapbox API.
    """

    def __init__(self, center_loc, client_model, access_token):

        # Instance Variables:
        self.center_loc = center_loc
        self.client_model = client_model
        self.access_token = access_token

        # Initalizing methods that build data structures based on input parms:
        self.data_points = self.build_coord_lst()


    def build_coord_lst(self):
        '''
        Internal method that queries the file search api and builds a list of all
        the lat and long points that will be displayed on this instance of the
        GIS model.

        Returns
        -------
        coord_dict : dict
            A python dictionary that contains all of the latitude and longnitude
            data to be plotted onto the Scattermapbox plot. Dict follows the structure:
            {'lat': [list of lat values], 'long': [list of long values]}
        '''
        # TODO: Invoke and initalize the file query api
        data_points = []

        return data_points


    def build_map_fig(self):

        # For Dev-- Mapbox public access token:
        access_token = "pk.eyJ1IjoibWF0dGhld3RlZSIsImEiOiJja2FwaW5xYWMwbDJ1MndwMXJmMDM0b2hoIn0.lrkYRxipKJe4s5IyA1kq7w"

        # Creating test Scatter Map Box Graph Object:
        fig = go.Figure(go.Scattermapbox())

        # Updating figure to display Sat data:
        fig.update_layout(
            mapbox = {
                'accesstoken' : access_token,
                'style' : 'satellite',
                'center': dict(lat=10.008, lon=-60.306 ),
                'zoom' : 7
            }
        )

        return fig

#gis_model((14.097,-60.896), 'BP_TT_Cypre', '')


# Class that produces a dashboard displaying data on a single node:
class dashboard(dfsu_ingestion_engine):
    '''
    The dashboard object is used to ingest data generated by the dfsu_ingestion_engine
    and provide an API that allows dashboards displaying the data to be generated and
    displayed using the plotly library.

    The object is initalized via a filepath and uses its various methods
    to return plotly figure objects that can be compiled into a dashboard.

    Parameters
    ----------
    filepath : str
        The filepath of the .dfsu file used to initalize the dfsu_ingestion_engine

    gis_filepath : str
        This is the filepath of the GeoJSON file that will be used to initalize the
        gis_model() object used for plotting maps and spatial visualization.
    '''

    def __init__(self, filepath, gis_filepath):

        self.filepath = filepath

        # Initalizing dfsu_ingestion_engine:
        super().__init__(filepath) # NOTE: initalizes ingestion engine internally.

        # Initalizing the gis model data:
        self.gis_model = gis_model(gis_filepath)

        # Key-Value store of config information for each time series plot:
        self.timeseries_format = {
            'Salinity': {'df_column': 'Salinity', 'title':'Water Salinity','units':'PSU'},
            'Temperature' : {'df_column':'Temperature', 'title':'Water Temperature', 'units':'Degrees Celsius'},
            'Density' : {'df_column':'Density', 'title':'Water Density', 'units':'kg/m^3'},
            'Current direction' : {'df_column':'Current direction', 'title':'Current Direction', 'units':'Radians'},
            'Current speed' : {'df_column':'Current speed', 'title':'Current Speed', 'units': 'm/s'},
                                }

        # Key-Value store of config information for each polar radial plot:
        self.barpolar_format = {}
    # Method that returns a figure representing the main dashboard of a single point:
    def plot_node_data(self, long, lat, depth):
        '''
        Method returns a plotly figure object containing all the relevant graphs
        for a dfsu file that contains the following data categories:
            - Current speed (meter per sec)
            - Density (kg per meter pow 3)
            - Temperature (degree Celsius)
            - Current direction (Horizontal) (radian)
            - Salinity (PSU)

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        depth : float
            The depth value of the location point

        Returns
        -------
        subplot_figure : plotly figure object
            This is the figure object that in this case contains subplots
            with all the relevant graphs plotted. It is intended to be placed
            passed into a Dash applicaiton or a Django view.
        '''

        # Creating the subplot format:
        fig = make_subplots(
            rows=4, cols=2,
            #shared_xaxes=True,
            #print_grid=True,
            vertical_spacing=0.5/3,
            subplot_titles=(
            self.timeseries_format['Current speed']['title'],
            'Polar Plot of Speed and Direction',
            self.timeseries_format['Temperature']['title'],
            self.timeseries_format['Density']['title'],
            self.timeseries_format['Salinity']['title']),
            # Specifying the format types for each subplot:
            specs = [[{'type':'xy'}, {'rowspan': 4, 'type': 'polar'}],
                     [{'type':'xy'}, None],
                     [{'type':'xy'}, None],
                     [{'type':'xy'}, None]]
                     )
        fig['layout'].update(height=800) # Pysical Size of Page

        # Current Speed:
        fig.add_trace(self.create_timeseries(long, lat, depth, 'Current speed'),
        row=1, col=1)
        fig.update_yaxes(title_text=self.timeseries_format['Current speed']['units'],
            row=1, col=1)

        # Temperature:
        fig.add_trace(self.create_timeseries(long, lat, depth, 'Temperature'),
            row=2, col=1)
        fig.update_yaxes(title_text=self.timeseries_format['Temperature']['units'],
            row=2, col=1)

        # Density:
        fig.add_trace(self.create_timeseries(long, lat, depth, 'Density'),
            row=3, col=1)
        fig.update_yaxes(title_text=self.timeseries_format['Density']['units'],
            row=3, col=1)

        # Salinity:
        fig.add_trace(self.create_timeseries(long, lat, depth, 'Salinity'),
            row=4, col=1)
        fig.update_yaxes(title_text=self.timeseries_format['Salinity']['units'],
            row=4, col=1)

        # Polar Current Direction and Speed Plot:
        fig.add_trace(self.create_polar_plot(long, lat, depth, 'Current speed',
        'Current direction'), row=1, col=2)

        # Building title text string based on coordinate input:
        title_text = f'CDL Analytics Dashboard for Model Node Located at \
[Long:{long}     Lat:{lat}   Depth:{depth}]'

        fig.update_layout(title_text=title_text,
            xaxis_rangeslider_visible=False,
            showlegend=False,
            # Setting polar plot axis to correct directional format:
            polar=dict(
                angularaxis = dict(
                        rotation=90,
                        direction= 'clockwise',
                        ),
                radialaxis = dict(showticklabels=False),
                    )
                )

        return fig
    # Method that returns a figure containing summary plots about a single point water column:
    def plot_water_column_table(self, long, lat): # TODO: Name to long winded?
        '''
        This method generates a plotly figure that displays a summary table of
        information on each water column for a specific long, lat point.

        The table contains the depth of each depth level, the corresponding
        average data values for each depth level on:

        - Current Speed
        - Water Salinity
        - Water Temperature
        - Water Density

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        Returns
        -------
        table_figure : plotly graph object
            This is the plotly graph object that displays a table of summary data
            for each water depth layer at a specific long and lat point.
        '''
        # Extracting the dictionary of data indexes for specific water column:

        #column_data = self.get_node_layers(long, lat)
        # NOTE: FOR DEVELOPMENT:
        column_data = {-12.39876: 59927, -10.16637: 2, -8.297584: 3, -6.722366: 35, -5.382481: 59683,
         -4.229135: 59684, -3.221019: 85, -2.322656: 59600, -1.50297: 8, -0.7340443: 38, 0.01: 9}

        # Creating the dataframe that will be used to create the plotly table:
        table_df = pd.DataFrame(columns=['Depth', 'Avg Current Speed (m/s)',
            'Avg Water Salinity (PSU)', 'Avg Water Temperature (Degrees Celsius)', 'Avg Water Density (kg/m^3)'])

        print(table_df)
         # Loop that itterates over column_data dict to create dataframe of relevant data:
        for depth, index in column_data.items():

            # Extracting the water data based on the index value and declaring vars:
            current_speed_data = self.extract_data('Current speed',
                index)[self.timeseries_format['Current speed']['df_column']].mean()

            salinity_data = self.extract_data('Salinity',
                index)[self.timeseries_format['Salinity']['df_column']].mean()

            temperature_data = self.extract_data('Temperature',
                index)[self.timeseries_format['Temperature']['df_column']].mean()

            density_data = self.extract_data('Density',
                index)[self.timeseries_format['Density']['df_column']].mean()

            # Creating dicit of column names and column vals to be appended to table_df:
            df_map_dict = {
                'Depth':depth,
                'Avg Current Speed (m/s)':current_speed_data.round(2),
                'Avg Water Salinity (PSU)':salinity_data.round(2),
                'Avg Water Temperature (Degrees Celsius)':temperature_data.round(2),
                'Avg Water Density (kg/m^3)':density_data.round(2)
                    }

            # Adding row to table_df:
            table_df = table_df.append(df_map_dict, ignore_index=True)
            # Invertnig dataframe to display shallowest level first:
            table_df = table_df.reindex(index=table_df.index[::-1])

        # Creating and formatting plotly table graph object:
        table = go.Table(
            # Plotting Table Header:
            header = dict(values=list(table_df.columns)),
            # Adding data to cells:
            cells = dict(values=[table_df['Depth'], table_df['Avg Current Speed (m/s)'],
                table_df['Avg Water Salinity (PSU)'], table_df['Avg Water Temperature (Degrees Celsius)'],
                table_df['Avg Water Density (kg/m^3)']])
                )

        return go.Figure(data=table)
    # Method that returns a timeseries scatterplot plotly object based on input data:
    def create_timeseries(self, long, lat, depth, plot_name):
        '''
        Method plots and returns a plotly graph objects of timeseries data. The
        data is extracted from the dfsu_ingestion_engine and the format of the
        timeseries is set by the timeseries_format dict.

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        depth : float
            The depth value of the location point

        plot_name : str
            This is the category string that will be used to retrieve the dfsu data
            and to determine the format of the timeseries.

        Returns
        -------
        timeseries_plot : plotly.graph_objects
            The plotly graph object that can be plotted either as a standalone or
            onto a subplot.
        '''

        # Extracting data based on category:
        timeseries_data = self.get_node_data(long, lat, depth, plot_name)

        # Creating the timeseries plot and formatting it based on timeseries_format:
        timeseries_plot = go.Scatter(x=timeseries_data.index,
            y=timeseries_data[self.timeseries_format[plot_name]['df_column']],
            name= self.timeseries_format[plot_name]['title'])

        return timeseries_plot
    # Method that plots a specific polar plot:
    def create_polar_plot(self, long, lat, depth, r_column, theta_column):
        '''
        Method plots and returns a plotly graph object that contains a polar/radial
        plot based on the input coordinates and the graph format pulled from a
        formatting dictionary

        Parameters
        ----------
        long : float
            The longnitude value of the location point

        lat : float
            The latitude value of the location point

        depth : float
            The depth value of the location point

        r_column : str
            A string indicating the data category that will be extracted to form
            the r values in the (r, theta) polar coordinate system via the data
            extraction api.

        theta_column : str
            A string indicating the data category that will be extracted to form
            the theta values in the (r, theta) polar coordinate system via the data
            extraction api. This value MUST be either radians or degrees.

        Returns
        -------
        barpolar_plot : plotly.graph_objects
            A plotly graphing object that can be inserted into a plotly figure.
        '''

        # Extracting data from the ingestion engine:
        r = self.get_node_data(long, lat, depth, r_column)
        theta = self.get_node_data(long, lat, depth, theta_column)

        # Attempting to convert the theta to degree values of they are in radians:
        try:
            theta = theta.apply(lambda x : math.degree(x))
        except:
            pass


        # Initalizing the barpolar plot based on formatting dict:
        barpolar_plot = go.Barpolar(
                r=r[self.timeseries_format[r_column]['df_column']],
                theta=theta[self.timeseries_format[theta_column]['df_column']],
                width=7.0,
                opacity=0.8,
                marker=dict(
                    color=r[self.timeseries_format[r_column]['df_column']],
                    colorscale="Viridis",
                    colorbar=dict(
                        title=self.timeseries_format[r_column]['units']
                        )
                    )
                )

        return barpolar_plot
