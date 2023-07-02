import folium
import json
import urllib
from urllib.request import Request, urlopen
import streamlit as st
from streamlit_folium import st_folium, folium_static
import pandas as pd
from haversine import haversine, Unit


#------------------------------------------------------------------------------------------------------------------------------------------
# 주소에 geocoding 적용하는 함수를 작성.
def get_location(loc ='서울 송파구 잠실로 209') :
    client_id = 'xxjiuvgdum'
    client_secret = 'zs8BuNezQMQnUVj3y5tsOpcCFDfb0dAfYN6TEN6F'
    url = f"https://naveropenapi.apigw.ntruss.com/map-geocode/v2/geocode?query=" \
    			+ urllib.parse.quote(loc)
    
    # 주소 변환
    request = urllib.request.Request(url)
    request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
    request.add_header('X-NCP-APIGW-API-KEY', client_secret)
    
    response = urlopen(request)
    res = response.getcode()
    
    if (res == 200) : # 응답이 정상적으로 완료되면 200을 return한다
        response_body = response.read().decode('utf-8')
        response_body = json.loads(response_body)
        print(response_body)
        # 주소가 존재할 경우 total count == 1이 반환됨.
        if response_body['meta']['totalCount'] == 1 : 
        	# 위도, 경도 좌표를 받아와서 return해 줌.
            lat = response_body['addresses'][0]['y']
            lon = response_body['addresses'][0]['x']
            return (lon, lat)
        else :
            print('location not exist')
        
    else :
        print('ERROR')
        
#  함수 적용
start = '서울 송파구 잠실로 209'
s_loc = start


start = get_location(start)



#---------------------------------------------------------------------------------------------------------------------------------------------
# 길찾기
def get_optimal_route(start, goal, option='trafast' ):
    client_id = 'xxjiuvgdum'
    client_secret = 'zs8BuNezQMQnUVj3y5tsOpcCFDfb0dAfYN6TEN6F' 
    # start=/goal=/(waypoint=)/(option=) 순으로 request parameter 지정
    url = f"https://naveropenapi.apigw.ntruss.com/map-direction/v1/driving?start={start[0]},{start[1]}&goal={goal[0]},{goal[1]}&option={option}"
    request = urllib.request.Request(url)
    request.add_header('X-NCP-APIGW-API-KEY-ID', client_id)
    request.add_header('X-NCP-APIGW-API-KEY', client_secret)
    
    response = urllib.request.urlopen(request)
    res = response.getcode()
    
    if (res == 200) :
        response_body = response.read().decode('utf-8')
        results = json.loads(response_body)
        return results            
    else :
        print('ERROR')
#-------------------------------------------------------------------------------------------------------------------------------------------   


#---------------------------------------------------------------------------------------------------------------------------------------------
st.set_page_config(layout='wide')

html = """<!DOCTYPE html>
<html>
<img src = "https://aivle.edu.kt.co.kr/tpl/001/img/common/logo.svg" alt = 에이블로고 style="float: left; width:100px; height:30px;"> </img>
</html>"""
st.markdown(html, unsafe_allow_html=True)

st.title('🚨긴급 대피 시스템')

#---------------------------------------------------------------------------------------------------------------------------------------------
# 옵션 - 최단거리
option = 'trafast'
# 현재위치를 텍스트로 입력받음
write_loc = st.text_input('위치를 입력하세요: ', value = '서울 송파구 잠실로 209')
start = write_loc
s_loc = start

# 출발지의 위경도 값을 호출
start = get_location(start)

# folium을 위한 리스트 형식의 위경도값 생성
center = [start[1], start[0]]

# haversine적용을 위한 튜플형식의 위경도값 생성
center_tuple = (float(start[1]), float(start[0]))

# 데이터 프레임 가공----------------------------------------------------------------------------------------------------------------------------
df = pd.read_csv('옥외대피소_포화도추가.csv')
dr = []
distance_list = []

# haversine을 통해 현위치 기준 가장 가까운 대피소 search
for i in range(len(df)):
    goal_lat = df['위도'][i]
    goal_lon = df['경도'][i]
    goal_position = (goal_lat, goal_lon)
    dist = haversine(center_tuple, goal_position, unit='km')
    distance_list.append(dist)
    
df['거리(km)'] = distance_list
df['거리(km)'] = round(df['거리(km)'],2)
df = df.sort_values('거리(km)')
df = df.head()
df.reset_index(drop=True, inplace=True)
df_r  = df[['경도','위도','비율']].copy()
biyul = df_r['비율'].values
df = df[['대피소명','거리(km)','위치', '현재인원', '수용가능인원']]

# 스트림릿
#----------------------------------------------------------------------------------------------------------------------------------------------
map1, empty2 = st.columns([0.8,0.1])

colms = st.columns((0.8, 0.8, 1.2, 0.9, 0.9, 1))
fields = df.columns

# column name 생성
for col, field_name in zip(colms, fields):
    col.markdown('**'+field_name+'**')
a = 'no'

# 각 column, row 내용 및 출발버튼 생성
for x in range(5):
    col1, col2, col3, col4, col5, col6 = st.columns((0.8, 0.8, 1.2, 0.9, 0.9, 1))
    col1.write(df[fields[0]][x])  
    col2.write(str(df[fields[1]][x])) 
    col3.write(df[fields[2]][x])  
    col4.write(str(df[fields[3]][x]))
    col5.write(str(df[fields[4]][x]))
    button_type = "출발" 
    button_phold = col6.empty()
    do_action = button_phold.button(button_type, key=x+100)
    # 출발 버튼을 눌렀을시 해당 목적지로 설정, 최단루트 안내
    if do_action:
        a = 'yes'
        gool = df[fields[2]][x]
        gool = get_location(gool)       
        goal = gool
        result = get_optimal_route(start, goal, option=option)
        route = result['route']['trafast'][0]['path'][:]
        for i in range(len(route)):
            route[i] = [route[i][1], route[i][0]]
        route.append([float(goal[1]), float(goal[0])])
        m = folium.Map(location=center, zoom_start=15)
        route_data = route
        folium.Marker(center).add_to(m)
        folium.Marker([goal[1],goal[0]], icon=folium.Icon('red', icon='star')).add_to(m)
        folium.PolyLine(locations=route_data[:], tooltip='polyLine').add_to(m)
    else:
        pass

# 출발 버튼을 누르지 않았을때, 주변 5개의 대피소를 지도에 시각화
if a == 'no':
    m = folium.Map(location=center, zoom_start=16)
    for i in range(len(df_r)):
        if biyul[i] > 0.8:
            folium.Marker([df_r['위도'][i], df_r['경도'][i]] , icon=folium.Icon('red')).add_to(m)
        elif biyul[i] > 0.5:
            folium.Marker([df_r['위도'][i], df_r['경도'][i]] , icon=folium.Icon('orange')).add_to(m)
        else:
            folium.Marker([df_r['위도'][i], df_r['경도'][i]] , icon=folium.Icon('green')).add_to(m)
    
    folium.Marker(center).add_to(m)
else:
    pass

with map1:
    st.markdown('### '+'현재위치: '+s_loc)
    st_data_r = folium_static(m, width=1200)
