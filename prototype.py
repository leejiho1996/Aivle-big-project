import folium
import json
import urllib
from urllib.request import Request, urlopen
import streamlit as st
from streamlit_folium import st_folium, folium_static
import pandas as pd
# *-- 3개의 주소 geocoding으로 변환한다.(출발지, 도착지, 경유지) --*
start = '부산광역시 부산진구 동성로 50'
goal = '부산 부산진구 전포대로175번길 22'
# waypoint = ''

#------------------------------------------------------------------------------------------------------------------------------------------
# 주소에 geocoding 적용하는 함수를 작성.
def get_location(loc) :
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
start = get_location(start)
goal = get_location(goal)

# 길찾기
#---------------------------------------------------------------------------------------------------------------------------------------------
option = 'trafast'

def get_optimal_route(start, goal, option=option ):
    # waypoint는 최대 5개까지 입력 가능, 
    # 구분자로 |(pipe char) 사용하면 됨(x,y 좌표값으로 넣을 것)
    # waypoint 옵션을 다수 사용할 경우, 아래 함수 포맷을 바꿔서 사용 
    client_id = 'xxjiuvgdum'
    client_secret = 'zs8BuNezQMQnUVj3y5tsOpcCFDfb0dAfYN6TEN6F' 
    # start=/goal=/(waypoint=)/(option=) 순으로 request parameter 지정
    url = f"https://naveropenapi.apigw.ntruss.com/map-direction-15/v1/driving?start={start[0]},{start[1]}&goal={goal[0]},{goal[1]}&option={option}"
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

# result = get_optimal_route(start, goal, option=option)
# route = result['route']['traoptimal'][0]['path'][:]

# for i in range(len(route)):
#     route[i] = [route[i][1], route[i][0]]

# route.append([float(goal[1]), float(goal[0])])

center = [start[1], start[0]]
# m = folium.Map(location=center, zoom_start=16)
# route_data = route
# folium.Marker(center).add_to(m)
# folium.PolyLine(locations=route_data[:], tooltip='polyLine').add_to(m)

# 데이터 프레임 가공----------------------------------------------------------------------------------------------------------------------------
df = pd.read_csv('대피소샘플.csv', encoding='cp949')
dr = []
distance_list = []
for i in range(len(df)):
    dr.append(df['위치'][i])
for i in dr:
    goal = get_location(i)
    result = get_optimal_route(start, goal, option=option)
    distance = result['route']['trafast'][0]['summary']['distance']
    distance_list.append(round(distance/1000,2))

df['거리(km)'] = distance_list 
df = df[['대피소명', '거리(km)', '위치']].copy()
df = df.sort_values(by='거리(km)')
df.reset_index(drop=True, inplace=True)
df['현재인원'] = [33,126,622,958,60]
df['최대인원'] = [59, 1952, 2240, 5240, 6242]
#---------------------------------------------------------------------------------------------------------------------------------------------

# 스트림릿
#-------------------------------------------------------------------------------------------------------------------------------------------
st.set_page_config(layout='wide')

html = """<!DOCTYPE html>
<html>
<img src = "https://aivle.edu.kt.co.kr/tpl/001/img/common/logo.svg" alt = 에이블로고 style="float: left; width:100px; height:30px;"> </img>
</html>"""
st.markdown(html, unsafe_allow_html=True)

st.title('🚨긴급 대피 시스템')
empty1, map1, empty2 = st.columns([0.1,0.8,0.1])
# st.dataframe(df)
# st_data = folium_static(m, width=1000)

# st.dataframe(df)

colms = st.columns((0.8, 0.8, 1.2, 0.9, 0.9, 1))
fields = df.columns

for col, field_name in zip(colms, fields):
            # header
    col.markdown('**'+field_name+'**')

for x in range(5):
    col1, col2, col3, col4, col5, col6 = st.columns((0.8, 0.8, 1.2, 0.9, 0.9, 1))
    col1.write(df[fields[0]][x])  
    col2.write(str(df[fields[1]][x])) 
    col3.write(df[fields[2]][x])  
    col4.write(str(df[fields[3]][x]))
    col5.write(str(df[fields[4]][x]))
    button_type = "출발" 
    button_phold = col6.empty()  # create a placeholder
    do_action = button_phold.button(button_type, key=x+100)
    if do_action:
        gool = df[fields[2]][x]
        gool = get_location(gool)       
        goal = gool
        # st.write(goal)
    else:
        pass


result = get_optimal_route(start, goal, option=option)
route = result['route']['trafast'][0]['path'][:]


for i in range(len(route)):
    route[i] = [route[i][1], route[i][0]]

route.append([float(goal[1]), float(goal[0])])
m = folium.Map(location=center, zoom_start=16)
route_data = route
folium.Marker(center).add_to(m)
folium.Marker([goal[1],goal[0]], icon=folium.Icon('red', icon='star')).add_to(m)
folium.PolyLine(locations=route_data[:], tooltip='polyLine').add_to(m)
with map1:
    st_data_r = folium_static(m, width=1200)


# 스트림릿
#-------------------------------------------------------------------------------------------------------------------------------------------