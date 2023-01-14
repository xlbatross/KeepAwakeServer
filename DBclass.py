from unittest import result
import pymysql

class Database:
    def __init__(self):
        self.host = '127.0.0.1'
        self.port = 3306
        self.user = "root"
        self.password = "1234"
        self.dbname = "drive"
        self.charset = "utf8"
    
    # DB connect 메서드
    def Connect(self):
        return pymysql.connect(
            host = self.host,
            port = self.port,
            user = self.user,
            password = self.password,
            db = self.dbname,
            charset = self.charset
        )

    # DB Drinving Insert 메서드

    def DrowsyTimeInsert(self, User ,Drowsy ,DTime):
        conn = self.Connect()
        curs = conn.cursor()
        sql = f"""INSERT INTO drive.driving (UserNumber,DrowsyCount,DrowsyInterval)
                  VALUES ({User},{Drowsy},'{DTime}');"""
        curs.execute(sql)
        conn.commit()
        conn.close()

    def UserInfoInsert(self, Src):
        conn = self.Connect()
        curs = conn.cursor()
        sql = f"""SELECT UserNumber FROM drive.user WHERE ImageSrc = "{Src}" ;"""
        result = curs.execute(sql)
        if result is not None:
            conn.close
        sql = f"""INSERT INTO drive.user (ImageSrc)
                VALUES('{Src}');"""
        curs.execute(sql)
        conn.commit()
        conn.close()

    
    ## DB Drinving Update 메서드    
    # def DriveUpdate(self,num,time):
    #     conn = self.Connect()
    #     curs = conn.cursor()
    #     sql = f"""update driving
    #               set FristDrivingTime = '{time}'
    #               where UserNumber ={num};"""
    #     curs.execute()
    #     conn.commit()
    #     conn.close()


    # test select 
    def UserLogin(self, imgPath):
        conn = self.Connect()
        curs = conn.cursor()
        sql = f"""select UserNumber
                    from drive.User
                    WHERE imagesrc = '{imgPath}';"""
                    #where imagesrc like '%1%'
        curs.execute(sql)
        result = curs.fetchone()
        userNumber = -1
        if not result is None:
            userNumber = result[0]
        # for row in curs:
        #     for el in row:
        #         rowlist.append(el)
        conn.commit()
        conn.close()
        return userNumber
        
    # 해당유저 아이디에대한 평균DrowsyTime 찾아오는 메서드
    def avgDrowsyTime(self,usernum):
        conn = self.Connect()
        curs = conn.cursor()
        sql = f"""select avg(drowsytime)
                  from drive.driving
                  where usernumber = {usernum}
                  group by drowsycount;"""
        curs.execute(sql)
        result = curs.fetchone()
        DrowsyResult = -1
        if not DrowsyResult is None:
            DrowsyResult = result
        # rowlist = []
        # for row in curs:
        #     for el in row:
        #         rowlist.append(el)
        conn.commit()
        conn.close()
        return DrowsyResult


    # DB select 메서드
    def Select(self ,coulmn ,table):
        conn = self.Connect()
        curs = conn.cursor()
        sql = f"""select {coulmn}
                  from drive.{table}"""
        curs.execute(sql)
        # rowlist = {}
        rowlist = []
        for row in curs:
            rowlist.append(list(row))
            # rowlist[row[1]]=row[2]
        conn.commit()
        conn.close()
        return rowlist