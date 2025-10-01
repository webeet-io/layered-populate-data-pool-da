#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fetch Berlin parks & playgrounds from OSM (Overpass via osmnx),
normalize to project schema, and write Parquet/GeoJSON.

Usage:
  python playgrounds_parks/scripts/osm_play_parks.py --place "Berlin, Germany"
"""

import argparse
import os
import json
import pandas as pd
import geopandas as gpd
import osmnx as ox
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry

ox.settings.use_cache = True
ox.settings.timeout = 300
ox.settings.overpass_rate_limit = True

TAGS_PARKS = {
    "leisure": ["park", "garden", "nature_reserve"],
    "landuse": ["recreation_ground"],
    "boundary": ["national_park"],
}
TAGS_PLAY = {"leisure": ["playground"]}

OUT_DIR = "playgrounds_parks/data"

TARGET_COLS = [
    "source","category","name","operator","brand",
    "latitude","longitude",
    "addr_street","addr_housenumber","addr_postcode","addr_city",
    "access","wheelchair","opening_hours",
    "website","phone","email",
    "surface","playground_features","sport",
    "osm_id","osm_type","wikidata","wikipedia",
    "geometry","tags_json"
]

def _geom_to_point(geom: BaseGeometry):
    if geom is None or geom.is_empty:
        return None
    if geom.geom_type == "Point":
        return geom
    return geom.representative_point()

def _category_from_tags(row: pd.Series) -> str:
    leisure = row.get("leisure")
    landuse = row.get("landuse")
    boundary = row.get("boundary")
    if leisure == "park": return "park"
    if leisure == "garden": return "garden"
    if leisure == "nature_reserve": return "nature_reserve"
    if landuse == "recreation_ground": return "recreation_ground"
    if boundary == "national_park": return "national_park"
    if leisure == "playground": return "playground"
    return None

def _collect_playground_features(row: pd.Series) -> str:
    keys = [k for k in row.index if isinstance(k, str) and k.startswith("playground:")]
    items = []
    for k in keys:
        v = row.get(k)
        if pd.notna(v):
            items.append(f"{k.split(':',1)[1]}={v}")
    return "; ".join(items) if items else None

def _features_from_place(place: str, tags: dict) -> gpd.GeoDataFrame:
    gdfs = []
    for k, vals in tags.items():
        for v in vals:
            try:
                g = ox.features_from_place(place, tags={k: v})
                if not g.empty:
                    gdfs.append(g)
            except Exception as e:
                print(f"[WARN] query failed for {k}={v}: {e}")
    if not gdfs:
        return gpd.GeoDataFrame(crs="EPSG:4326")
    gdf = pd.concat(gdfs, ignore_index=True)
    # drop duplicates by osmid if present
    if "osmid" in gdf.columns:
        gdf = gdf.drop_duplicates(subset=["osmid"])
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True, allow_override=True)
    else:
        gdf = gdf.to_crs(epsg=4326)
    return gdf

def _normalize(gdf: gpd.GeoDataFrame, source_hint="osm") -> gpd.GeoDataFrame:
    if gdf.empty:
        return gpd.GeoDataFrame(columns=TARGET_COLS, geometry="geometry", crs="EPSG:4326")

    df = gdf.copy()

    # osm_id / osm_type
    df["osm_id"] = df["osmid"] if "osmid" in df.columns else None
    df["osm_type"] = df["element_type"] if "element_type" in df.columns else None

    # representative lon/lat
    pts = df.geometry.apply(_geom_to_point)
    df["longitude"] = pts.apply(lambda p: p.x if isinstance(p, Point) else None)
    df["latitude"]  = pts.apply(lambda p: p.y if isinstance(p, Point) else None)

    # basic fields
    df["category"] = df.apply(_category_from_tags, axis=1)
    df["name"] = df.get("name")
    df["operator"] = df.get("operator")
    df["brand"] = df.get("brand")
    df["access"] = df.get("access")
    df["wheelchair"] = df.get("wheelchair")
    df["opening_hours"] = df.get("opening_hours")
    df["website"] = df.get("website")
    df["phone"] = df.get("phone")
    df["email"] = df.get("email")
    df["surface"] = df.get("surface")
    df["sport"] = df.get("sport")
    df["addr_street"] = df.get("addr:street")
    df["addr_housenumber"] = df.get("addr:housenumber")
    df["addr_postcode"] = df.get("addr:postcode")
    df["addr_city"] = df.get("addr:city")
    df["wikidata"] = df.get("wikidata")
    df["wikipedia"] = df.get("wikipedia")
    df["playground_features"] = df.apply(_collect_playground_features, axis=1)
    df["source"] = source_hint

    # tags_json = همه تگ‌ها برای مراجعات بعدی
    keep_exclude = set(TARGET_COLS) - {"tags_json"}
    tag_cols = [c for c in df.columns if c not in keep_exclude]
    df["tags_json"] = df[tag_cols].apply(
        lambda r: {k: r[k] for k in tag_cols if pd.notna(r[k])}, axis=1
    )

    out = df[TARGET_COLS].copy()
    out = gpd.GeoDataFrame(out, geometry="geometry", crs="EPSG:4326")
    return out

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--place", type=str, default="Berlin, Germany")
    args = parser.parse_args()

    os.makedirs(OUT_DIR, exist_ok=True)

    parks_raw = _features_from_place(args.place, TAGS_PARKS)
    plays_raw = _features_from_place(args.place, TAGS_PLAY)

    parks = _normalize(parks_raw, "osm")
    plays = _normalize(plays_raw, "osm")

    # فیلتر مطمئن
    parks = parks[parks["category"].isin(["park","garden","nature_reserve","recreation_ground","national_park"])]
    plays  = plays[plays["category"] == "playground"]

    both = pd.concat([parks, plays], ignore_index=True)

    # write parquet
    parks_path = os.path.join(OUT_DIR, "osm_parks.parquet")
    plays_path = os.path.join(OUT_DIR, "osm_playgrounds.parquet")
    both_path  = os.path.join(OUT_DIR, "osm_parks_playgrounds_merged.parquet")
    parks.to_parquet(parks_path, index=False)
    plays.to_parquet(plays_path, index=False)
    both.to_parquet(both_path, index=False)

    # optional GeoJSON for quick view
    try:
        parks.to_file(parks_path.replace(".parquet", ".geojson"), driver="GeoJSON")
        plays.to_file(plays_path.replace(".parquet", ".geojson"), driver="GeoJSON")
    except Exception as e:
        print(f"[WARN] GeoJSON write skipped: {e}")

    print(f"[OK] parks={len(parks)} | playgrounds={len(plays)} | total={len(both)}")
    print(f"[OK] saved:\n  {parks_path}\n  {plays_path}\n  {both_path}")

if __name__ == "__main__":
    main()
