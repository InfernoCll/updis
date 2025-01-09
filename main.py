from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import psycopg2
import json

app = FastAPI()

# 数据库连接设置
DATABASE_CONFIG = {
    "dbname": "city_planning",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DATABASE_CONFIG)

# 实时空间数据统计接口
@app.get("/area")
def get_area(region: str):
    query = """
    SELECT SUM(area) AS total_area
    FROM buildings
    WHERE region = %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (region,))
            result = cursor.fetchone()
    return {"region": region, "total_area": result[0] if result[0] else 0}

# 历史数据查询接口
@app.get("/buildings")
def get_new_buildings(region: str, start: datetime, end: datetime):
    query = """
    SELECT COUNT(*) AS new_buildings_count
    FROM buildings
    WHERE region = %s AND timestamp BETWEEN %s AND %s;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (region, start, end))
            result = cursor.fetchone()
    return {
        "region": region,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "new_buildings_count": result[0]
    }

# 通勤行为模拟接口
class CommuteRequest(BaseModel):
    region: str
    destination: str
    transport_modes: List[str]

@app.post("/commute")
def simulate_commute(data: CommuteRequest):
    commute_results = {}

    query = """
    SELECT ST_Distance(home.coordinates, work.coordinates) AS distance, average_speed, transport_mode
    FROM agents
    JOIN buildings AS home ON agents.home_region = home.region
    JOIN buildings AS work ON agents.work_region = work.region
    WHERE home.region = %s AND work.region = %s
    AND transport_mode = ANY(%s);
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, (data.region, data.destination, data.transport_modes))
            result = cursor.fetchall()
            

    for mode in data.transport_modes:
        speeds = [row[1] for row in result if row[2] == mode and row[1] > 0]  
        distances = [row[0] for row in result if row[2] == mode] 
        if distances and speeds:
            average_time = sum(d / s for d, s in zip(distances, speeds)) / len(distances)  
            commute_results[mode] = {"average_commute_time": round(average_time, 2)}
        else:
            commute_results[mode] = {"average_commute_time": None}  
    return {
        "region": data.region,
        "destination": data.destination,
        "transport_modes": commute_results
    }
