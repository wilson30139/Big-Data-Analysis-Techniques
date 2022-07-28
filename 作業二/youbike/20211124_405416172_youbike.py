import requests, json
from jsonmerge import merge
import geopandas as gpd
import folium
from folium.plugins import MarkerCluster
import openrouteservice
from openrouteservice import convert
import http.server
import socketserver
import time
import sys
#for jupyter
# sys.setrecursionlimit(3000)



#https://openrouteservice.org/dev/#/home

#initialization
#TP
url = requests.get('https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json')
#sno(站點代號)、sna(場站中文名稱)、tot(場站總停車格)、sbi(場站目前車輛數量)、sarea(場站區域)、mday(資料更新時間)、lat(緯度)、lng(經度)、ar(地點)、sareaen(場站區域英文)、snaen(場站名稱英文)、aren(地址英文)、
#bemp(空位數量)、act(全站禁用狀態)、srcUpdateTime、updateTime、infoTime、infoDate
#NTP
url2 = requests.get('https://data.ntpc.gov.tw/api/datasets/71CD1490-A2DF-4198-BEF1-318479775E8A/json/')
#sno(站點代號)、sna(中文場站名稱)、tot(場站總停車格)、sbi(可借車位數)、sarea(中文場站區域)、mday(資料更新時間)、lat(緯度)、lng(經度)、ar(中文地址)、sareaen(英文場站區域)、snaen(英文場站名稱)、aren(英文地址)、
#bemp(可還空位數)、act(場站是否暫停營運)


text = url.text
text2 = url2.text
data = json.loads(text)
data2 = json.loads(text2)

#c = merge(data2,data )
c = data+data2
url = []
url2 = url
text = url
text2 = url
data = url
data2 = url
#print(data+data2)
#district = requests.get("https://blog.hanklu.tw/static/folium/TPgeo.json")
d2 = requests.get("https://raw.githubusercontent.com/g0v/twgeojson/master/json/twCounty2010merge.topo.json")
d2 = d2.json()
#gdf = gpd.GeoDataFrame(district.json())
routeurl = requests.get('https://dev.virtualearth.net/REST/V1/Routes/Walking?wp.0=25.01688,121.49534&wp.1=25.11856,121.52964&key=Ais8A854N2_XtQVTV6Ooe9ubN1a24G3hdY5aEIQGpWuArW3JY7g-PMqIIMc8MFZ4')
routetext = routeurl.text
routedata = json.loads(routetext)
#print(routedata)

import urllib.request
import xml.etree.ElementTree as ET
from xml.etree import ElementTree

import xmltodict
# Your Bing Maps Key 
bingMapsKey = "Ais8A854N2_XtQVTV6Ooe9ubN1a24G3hdY5aEIQGpWuArW3JY7g-PMqIIMc8MFZ4"
"""
# input information
stlongitude = 121.49534
stlatitude = 25.01688

delongitude = 121.52964
delatitude = 25.11856
"""
#get strict line to link between 2 stations
for i in range(0, len(c)):
  print(f"{i}: {c[i]['sna']}")
startpt = int(input("Please input the ID of starting point: "))
endpt = int(input("Please input the ID of destination: "))
## input information
stlongitude = str(c[startpt]['lng'])
stlatitude = str(c[startpt]['lat'])

delongitude = str(c[endpt]['lng'])
delatitude = str(c[endpt]['lat'])

##set data of openrouteservice
client = openrouteservice.Client(key='5b3ce3597851110001cf624822d290749a5046ac94065cc3eea24050') # Specify your personal API key
temp = [(eval(stlongitude),eval(stlatitude)),(eval(delongitude),eval(delatitude))]
geometry = client.directions(temp, profile='cycling-regular', optimize_waypoints=True)['routes'][0]['geometry']
decoded = convert.decode_polyline(geometry)
decoded_modded = []
for i in range(len(decoded["coordinates"])):
  #print(i)
  decoded_modded.append([decoded["coordinates"][i][1],decoded["coordinates"][i][0]])
#print(decoded_modded)


routeUrl = "http://dev.virtualearth.net/REST/V1/Routes/Walking?wp.0=" + str(stlatitude) + "," + str(stlongitude) + "&wp.1=" + str(delatitude) + "," + str(delongitude)  +"&output=xml"+ "&key=" + bingMapsKey
print(routeUrl)
request = urllib.request.Request(routeUrl)
#response = urllib.request.urlopen(request)
response = requests.get(routeUrl)
tree = ElementTree.fromstring(response.content)
route = []
#print(tree)

#r = response.read().decode(encoding="utf-8")
dict_data = xmltodict.parse(response.content)
print(len(dict_data.get("Response")["ResourceSets"]["ResourceSet"]["Resources"]["Route"]["RouteLeg"]["ItineraryItem"]))
for i in range(0,len(dict_data.get("Response")["ResourceSets"]["ResourceSet"]["Resources"]["Route"]["RouteLeg"]["ItineraryItem"])):

  temp = (eval(dict_data.get("Response")["ResourceSets"]["ResourceSet"]["Resources"]["Route"]["RouteLeg"]["ItineraryItem"][i]["ManeuverPoint"]["Latitude"]),eval(dict_data.get("Response")["ResourceSets"]["ResourceSet"]["Resources"]["Route"]["RouteLeg"]["ItineraryItem"][i]["ManeuverPoint"]["Longitude"])) 
  route.append(temp)
#print(dict_data.get("Response")["ResourceSets"]["ResourceSet"]["Resources"]["Route"]["RouteLeg"]["ItineraryItem"][0]["ManeuverPoint"]["Latitude"])

"""
result = json.loads(r)

itineraryItems = result["resourceSets"][0]["resources"][0]["routeLegs"][0]["itineraryItems"]

for item in itineraryItems:
    print(item["instruction"]["text"])

"""

#m = Map((25.0133904,121.52245), zoom_start = 15, control_scale=True)
#loc = [(25.0133904,121.52245), (25.133904,121.52245)]

m = folium.Map((25.0133904,121.52245), zoom_start= 15)

#topo version
folium.TopoJson(
  d2,
  'objects.layer1',
  name='市邊界'
).add_to(m)

#get stations information
cluster = folium.plugins.MarkerCluster().add_to(m)
cluster2 = folium.plugins.MarkerCluster().add_to(m)
cluster3 = folium.plugins.MarkerCluster().add_to(m)
cluster4 = folium.plugins.MarkerCluster().add_to(m)




cluster2.layer_name = "Bing導航"
cluster3.layer_name = "Open Routes Service導航"
yes =0
no =0
for i in range(0,round(len(c))):
    if (int(c[i]['act']) == 0) or (int(c[i]['bemp'])==0):
        col = "red"
        no+=1
        folium.Marker(
            location=[c[i]['lat'], c[i]['lng']],
            popup=c[i]['sna']+"</br>總共車位:"+str(c[i]['tot'])+"</br>可還車車位:"+str(c[i]['bemp'])+"</br>可借車輛:"+str(int(c[i]['tot'])-int(c[i]['bemp']))+"</br>緯度:"+str(c[i]['lat'])+"</br>經度:"+str(c[i]['lng']),
            tooltip=c[i]['sna'],
            icon=folium.Icon(color=col,icon_color="orange",icon='bicycle', prefix='fa')
        ).add_to(cluster4)
    else:
        col = "lightgreen"
        yes+=1
        folium.Marker(
            location=[c[i]['lat'], c[i]['lng']],
            popup=c[i]['sna']+"</br>總共車位:"+str(c[i]['tot'])+"</br>可還車車位:"+str(c[i]['bemp'])+"</br>可借車輛:"+str(int(c[i]['tot'])-int(c[i]['bemp']))+"</br>緯度:"+str(c[i]['lat'])+"</br>經度:"+str(c[i]['lng']),
            tooltip=c[i]['sna'],
            icon=folium.Icon(color=col,icon_color="orange",icon='bicycle', prefix='fa')
        ).add_to(cluster)

cluster.layer_name = str("可還車站點 "+str(yes))
cluster4.layer_name = str("不可還車站點 "+str(no))

folium.LayerControl(collapsed=False).add_to(m)

#MarkerCluster
pointx = []
pointy = []
## Get x and y coordinates for each point

#draw bing lines
bing_line = folium.PolyLine(route,
                color='red',
                weight=15,
                opacity=0.8,
                name="route_bing")
bing_line.add_to(cluster2)

#draw openroutesservice lines
oss_line = folium.PolyLine(decoded_modded,
                color='yellow',
                weight=15,
                opacity=0.8,
                name="***")
oss_line.add_to(cluster3)

m
m.save("index.html")



PORT = 8080
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()