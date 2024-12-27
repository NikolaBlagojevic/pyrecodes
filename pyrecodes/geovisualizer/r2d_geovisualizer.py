import geopandas
from pyrecodes.geovisualizer.concrete_geovisualizer import ConcreteGeoVisualizer

class R2D_GeoVisualizer(ConcreteGeoVisualizer):
    """
    Class that visualizes components created using R2D output files as geospatial plots.
    """
    
    def create_geodataframe(self) -> None:
        # TODO: Fix this method, ugly.
        buildings_dataframe = self.create_empty_dataframe()
        for i, component in enumerate(self.components):
            geometry_WKT_format = None
            if hasattr(component, 'footprint'):
                geometry_WKT_format = self.get_polygon_in_WKT_format(component) 
            elif hasattr(component, 'geometry'):
                geometry_WKT_format = component.geometry

            if geometry_WKT_format is not None:
                current_row = len(buildings_dataframe) + 1
                component_data_for_df = [i, geometry_WKT_format,
                                            'Functional']              
                buildings_dataframe.loc[current_row] = component_data_for_df

        geo_series = geopandas.GeoSeries.from_wkt(buildings_dataframe['Footprint_WKT'])
        geodataframe = geopandas.GeoDataFrame(buildings_dataframe, geometry=geo_series, crs="EPSG:4326")
        self.buildings_geodataframe = geodataframe.to_crs(epsg=3857)   

    def plot_component_localities(self, number_of_localities=10):
        components_to_plot = []
        for component in self.components:
            if self.component_has_geometry(component):
                components_to_plot.append(component)
        self.create_localities_figure(components_to_plot, number_of_localities, save=True)

    def component_has_geometry(self, component) -> bool:
        if hasattr(component, 'geometry') or hasattr(component, 'footprint'):
            return True
        else:
            return False
    
    def get_polygon_in_WKT_format(self, component) -> str:
        if self.footprint_in_WKT_format(component.footprint):
            return component.footprint
        else:
            building_polygon_coordinates_as_list = [[str(coordinate_x) + ' ' + str(coordinate_y)][0] for
                                                    coordinate_x, coordinate_y in
                                                    component.footprint['geometry']['coordinates'][0]]
            building_polygons_as_one_string = ','.join(building_polygon_coordinates_as_list)
            building_polygon_WKT_format = 'POLYGON((' + building_polygons_as_one_string + '))'
            return building_polygon_WKT_format
    
    def footprint_in_WKT_format(self, footprint) -> bool:
        if 'POLYGON' in footprint:
            return True
        else:
            return False   
        