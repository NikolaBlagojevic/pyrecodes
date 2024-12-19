import json
import importlib
import shapely

def read_json_file(file_name: str) -> dict:
    """Reads a JSON file and returns its contents as a dictionary.

    Args:
        file_name (str): The name of the JSON file to be read.

    Returns:
        dict: The dictionary representation of the JSON data.
    """
    with open(file_name, 'r') as file:
        file = json.load(file)
    return file

def get_class(module_name: str, class_name: str, folder_name: str) -> object:
    """Imports a class from a file"""
    class_module = importlib.import_module(f'pyrecodes.{folder_name}.{module_name}')
    target_class = getattr(class_module, class_name)
    return target_class

def create_locality_polygon(bounding_box: list) -> shapely.Polygon:
    return shapely.Polygon([(lat, long) for long, lat in bounding_box])

def component_inside_bounding_box(component_geometry: shapely.Point, polygon: shapely.Polygon) -> bool:
    return component_geometry.within(polygon)

def create_component_geometry_from_wkt(geometry_string: str) -> shapely.geometry.base.BaseGeometry:
    return shapely.wkt.loads(geometry_string)

def create_component_geometry_as_point(component_location: list) -> shapely.Point:
    return shapely.Point(component_location[0], component_location[1])

def get_locality_coordinates_from_geojson(locality_info: dict) -> dict:
    geojson_file = json.load(open(locality_info['GeoJSON']['Filename'], 'r'))            
    return {'BoundingBox': geojson_file['features'][0]['geometry']['coordinates'][0][0]}

def format_locality_id(locality_string) -> int:
    return int(locality_string.split(' ')[-1])