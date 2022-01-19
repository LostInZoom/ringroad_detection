# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 15:26:34 2022

@author: QPotie
"""
import osmnx as ox
import momepy # gdf to graphs
import geopandas as gpd
import matplotlib.pyplot as plt
import networkx as nx
import time

# engine for postgis:
import psycopg2
from sqlalchemy import create_engine


ENGINE_PARAM = "postgresql://postgres:Postgres32167!@localhost:5432/ringroad"
SQL_GET_ROADS = "SELECT * FROM roads WHERE city_name IN ('NANTES')"
# , 'PARIS', 'AMIENS'

# starting time
start = time.time()

# 1) postgis to gdf
engine = create_engine(ENGINE_PARAM)
gdf_roads = gpd.GeoDataFrame.from_postgis(SQL_GET_ROADS, engine, geom_col="geometry")


print("shape: ", gdf_roads.shape)
print("columns: ", gdf_roads.columns)
print(gdf_roads.head())


# 2) gdf to graph ()
graph = momepy.gdf_to_nx(gdf_roads, approach='primal')



# 3) display

#nx.draw(graph)

# doesn't work :
# g_projected = ox.project_graph(graph)
# save_path = "images/" + "nantes.png"
# ox.plot_graph(g_projected, save=True, filepath=save_path)



# 4) get cycles
#cycles = nx.cycle_basis(graph)
cycle = nx.find_cycle(graph)

# end time
end = time.time()

# total time taken
print(f"Runtime of the program is {end - start}")

# print("nb_cycles : ", len(cycles))
# print(cycles[0], cycles[1], cycles[-1])
