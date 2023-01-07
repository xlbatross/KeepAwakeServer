from DBclass import DB 
import datetime
import random
import time

# 아이디 찾기
#임의로 페이스 아이디인 이미지 파일을 만들어놓음
id = ['1.jpg' ,'2.jpg','3.jpg','4.jpg','5.jpg']



DB().UserInfoInsert('6.jpg')
# 페이스 아이디인 이미지데이터와 
# 현재 사용자가 같은 이미지가 있는지 체크
# 페이스 아이디와 이미지 파일 같으면 
# 운전자의 아이값을 넘겨줌 
def SreachId(id):
    userinfo = DB().UserLogin(id) # ImageSrc
    return (len(userinfo) > 0) #운전자의 아이디값 (UserNumber)
s = SreachId('6.jpg')
print(s)


print(DB().avgDrowsy(1))
print(DB().DrowsyCount())
# 운전자의 아이디값으로 DrowsyCount 마다의 평균 시간 뽑기
# def avgtime(s):
    
    


# userinfo = DB().Select2()
# print(userinfo)
# # print(userinfo.keys())
# a = '5.jpg'
# # if :
#     # print('ok') 

# if bool(a == userinfo[0]) is False:
#     print("다름")
# else:
#     print("같음")
# # dc = DB().DrowsyCount()
# # print(dc)