# -*- coding: utf-8 -*-
# python 3.9
# ox environment

# Import french road data from osm, around specified cities, in a postgis database using osmnx library

# The bible : https://www.postgresqltutorial.com/postgresql-python/

# IMPORTS
import osmnx as ox
import pandas as pd
import geopandas as gpd
# engine for postgis:
import psycopg2
from sqlalchemy import create_engine


# PARAMS 
# server and database connexion
ENGINE_PARAM = "postgresql://postgres:Postgres32167!@localhost:5432/ringroad"
# roads table:
EXTENT_M = 5000 # 5km from the center
EXTENT_DEG = 0.2
# select all cities
#SQL_GET_CITIES = "SELECT geometry, insee, nom, pop_2010, long_deg, lat_deg FROM city"
SQL_GET_CITIES = "SELECT geometry, insee, nom, pop_2010, long_deg, lat_deg FROM cities WHERE pop_2010>100000"
CITIES_CSV = "villes_france_cleaned.csv"


# CREATE CITY TABLE FROM CSV, APPEND IF TABLE EXISTS
def create_city_table(table_name):
    # CSV --> DF
    cities = pd.read_csv(CITIES_CSV, sep=";")
    # DF --> GDF
    cities_gdf = gpd.GeoDataFrame(cities, geometry=gpd.points_from_xy(cities.long_deg, cities.lat_deg))
    df_check(cities_gdf)
    # GDF --> POSTGIS
    engine = create_engine(ENGINE_PARAM)
    cities_gdf.to_postgis(table_name, engine, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)




# CREATE A TABLE OF ROADS THAT ARE AROUND THE CITIES
def create_road_table(table_name, highway_tag):
    engine = create_engine(ENGINE_PARAM)
    
    # import cities from postgis
    gdf_cities = gpd.GeoDataFrame.from_postgis(SQL_GET_CITIES, engine, geom_col="geometry")
    df_check(gdf_cities)
    
    nb_cities = gdf_cities.shape[0]
    
    print("Number of cities : ", nb_cities)
    
    gdfs_roads = []
    
    # for each city
    i=1
    for index, row in gdf_cities.iterrows():
        city_name = row['nom']
        city_center = (row['lat_deg'], row['long_deg'])
        print(type(row['lat_deg']))
        
        # get all roads around and stock them in a gdf
        #gdf_roads = ox.geometries.geometries_from_address(city_name, tags={"highway":"motorway"}, dist=EXTENT_M)
        gdf_roads = ox.geometries.geometries_from_point(city_center, tags={"highway":highway_tag}, dist=EXTENT_M)
        #"['highway'~'motorway|trunk|primary']"
        
        # ajouter le nom de la ville en tant qu'attribut
        gdf_roads = gdf_roads.assign(city_name = city_name)
        
        # regrouper le gdf de la ville avec ceux des autres villes
        gdfs_roads.append(gdf_roads)
        
        print("gdf_roads for city {}/{} created".format(i, nb_cities))
        i+=1

    # Fusion all gdfs_roads, put NaN when attribut is empty
    gdf_roads = pd.concat(gdfs_roads, ignore_index=True, sort=False)
    print("gdfs fusioned")
    
    # Keep only linear features (others are errors from contributors)
    #gdf_roads = gdf_roads[gdf_roads[]]
    
    # import the roads in postgis in a table
    gdf_roads.to_postgis(table_name, engine, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
        
    print("Roads imported")
        

def create_main_road_table(tables_from, table_to):
    engine = create_engine(ENGINE_PARAM)
    print("engine created")
    
    for road_type in tables_from:
        print("in loop on road_type " + road_type)
        
        # get gdf, keep only town name and geom, and add column "highway"
        query = "SELECT geometry, highway, nodes, maxspeed, city_name FROM public." + road_type
        gdf_road_type = gpd.GeoDataFrame.from_postgis(query, engine, geom_col="geometry")
        print("gdf created")
        
        # keep only data where geom_type = linestring
        gdf_road_type = gdf_road_type[gdf_road_type.geom_type == "LineString"]
        print("LineString filtered")
        
        # import it on main table
        gdf_road_type.to_postgis(table_to, engine, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)
        print("import done")
    
    

    
    #gdf_roads.to_postgis(table_name, engine, if_exists='append', index=True, index_label=None, chunksize=None, dtype=None)


def create_road_graphs(cities_gdf):
    for index, row in cities_gdf.iterrows():
        city_name = row["nom"]
        g = ox.graph.graph_from_address(city_name, dist=5000, dist_type='bbox', network_type='drive', simplify=True, retain_all=False, truncate_by_edge=False, return_coords=False, clean_periphery=True, custom_filter="['highway'~'motorway|trunk|primary']")

        g_projected = ox.project_graph(g)
        save_path = "images/" + city_name + ".png"
        ox.plot_graph(g_projected, save=True, filepath=save_path)

def df_check(df):
    print(type(df))
    print("shape: ", df.shape)
    #print("info: ", df.info())
    print("columns: ", df.columns)
    print(df.head())

# Import cities from postgis db




road_types = ["motorway", "trunk", "primary", "secondary", "tertiary", "unclassified", "residential", "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "living_street"]

# for road_type in road_types:
#     create_road_table(road_type, road_type)

create_main_road_table(road_types, "roads")



    

# tracer plot du nombre d'habitants par tranche de 10k

# BBOX_FRANCE = (41.65, 51.58, -5.56, 9.16)
# BBOX_LILLE = (50.50, 50.74, 2.65, 3.22)
# test = {"city_id":2, "city_name":"truc", "city_geom":""}

### Extract gdf from bounding box :
# gdf = ox.geometries.geometries_from_bbox(*BBOX_LILLE,tags={'highway':"motorway"})
# Filter columns we're interested in
# gdf = gdf[['highway', 'geometry']]

# gdf = ox.geometries.geometries_from_bbox(*BBOX_LILLE,tags={'highway':"trunk"})



### le transformer au format json avec geopandas :
# road_csv = gdf.to_csv()
# writting it to a file
# f = open("road.csv", "w+")
# f.write(road_csv)
# f.close()


