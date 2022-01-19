# -*- coding: utf-8 -*-
# python 3.9


import osmnx as ox
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

def df_check(df):
    print(type(df))
    print("shape: ", df.shape)
    #print("info: ", df.info())
    print("columns: ", df.columns)
    print(df.head())
    
address = "Lille"
    
g = ox.graph.graph_from_address(address, dist=5000, dist_type='bbox', network_type='drive', simplify=True, retain_all=False, truncate_by_edge=False, return_coords=False, clean_periphery=True, custom_filter="['highway'~'motorway|trunk|primary']")

g_projected = ox.project_graph(g)
save_file = "Lille.png"
ox.plot_graph(g_projected, save=True, filepath=save_file)