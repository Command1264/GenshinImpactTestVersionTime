import json, datetime, re, os
from datetime import date, timedelta
# TODO 可以用 list 先把有要加的事件存起來，最後再加一遍
class GIDateMoney:
    def __init__(self, filePath: str = __file__, 
                startDate: date = date.today(),
                endDate: date = (date.today() + datetime.timedelta(days = 1)) ):
        self.__runPath = os.path.dirname(filePath) + "\\"
        self.__GITimePath = self.__runPath + "GenshinImpactTime.json"
        self.__versionKeysRe = re.compile("v[1-4]")
        self.__subVersionKeysRe = re.compile("[1-4].[0-8]")
        self.__startDate = startDate
        self.__endDate = endDate
        self.__dtffDays = abs(self.__endDate - self.__startDate)
        self.__jDict = dict()
        self.__timeFormat = "%Y %m %d"
        self.__CVTLst = [20, 22]
        self.__minDays = 0
        self.__cantFindFlag = False

        self.__currVerTime = None
        self.__currVerName = None

        self.__readBasic()
    
    def __readBasic(self):
        with open(self.__GITimePath, "r", encoding="utf-8") as fp: # read GITime json file
            if (fp.readable()): self.__jDict = json.load(fp)
        for key, value in self.__jDict.items(): # 先讀取 timeFormat and CVTLst 的值
            if (key == "time_format"):
                self.__timeFormat = value
            if (key == "changeVersionTime"):
                self.__CVTLst = list(self.__jDict[key].values())
                # CVTLst = [jDict[key]["up"], jDict[key]["down"]]

    # 讀取版本時間
    def readVerTime(self):
        self.__readBasic()

        VerTime = None
        VerName = None

        flag = [False, False, False]
        allBreakFlag = False
        for index, key in enumerate(self.__jDict.keys()):
            if (self.__versionKeysRe.match(key)): # 確認大版本的 key
                # 確保跑到最後一個時，可以把數值取出來，做接下來的運算
                if (index == len(self.__jDict) - 1): flag[0] = True

                for index2, key2 in enumerate(self.__jDict[key].keys()):
                    # 確保跑到最後一個時，可以把數值取出來，做接下來的運算
                    if ((index2 == len(self.__jDict[key]) - 1) and flag[0]): flag[1] = True

                    for index3, (key3, value3) in enumerate(self.__jDict[key][key2].items()):
                        # 確保跑到最後一個時，可以把數值取出來，做接下來的運算
                        if ((index3 == len(self.__jDict[key][key2]) - 1) and flag[1]): flag[2] = True

                        rangeDays = self.__startDate - datetime.datetime.strptime(value3, self.__timeFormat).date()
                        if ((rangeDays.days <= 0 and self.__minDays == None) or (flag[0] and flag[1] and flag[2])) :
                            self.__minDays = rangeDays.days
                            VerTime = datetime.datetime.strptime(value3, self.__timeFormat).date()
                            VerName = [key, key2, key3]
                            allBreakFlag = True
                            break
                    if (allBreakFlag): break # 處理提前跳脫
            if (allBreakFlag): break # 處理提前跳脫

        self.__currVerName = VerName
        self.__currVerTime = VerTime

        if (self.__minDays > 0): # 成立代表沒有在 json 裡面找到相對應的時間
            self.__cantFindFlag = True
            self.__tryToFindVerTime()
        
    def __tryToFindVerTime(self): # 來到這代表無法靠 json 找到時間，只能用猜測的
        while(self.__minDays > 0):
            verSmallName = self.__currVerName[2]
            # verMiddleName = self.__currVerName[1]

            if (verSmallName == "upTime"): self.__minDays -= self.__CVTLst[0]
            elif (verSmallName == "downTime"): self.__minDays -= self.__CVTLst[1]
            # TODO 舊程式碼替換中，需要做測試
            # if (verSmallName == "upTime"):
            #     self.__minDays -= self.__CVTLst[0]

                # self.__currVerName[2] = "downTime"
                # self.__currVerTime = self.__currVerTime + timedelta(days=self.__CVTLst[0])
                # minDays = abs(minDays - self.__CVTLst[0])

            # TODO 舊程式碼替換中，需要做測試
            # elif (verSmallName == "downTime"):
            #     self.__minDays -= self.__CVTLst[1]

            
                # tempLst = verMiddleName.split(".")
                # self.__currVerName[1] = f"{tempLst[0]}.{int(tempLst[1]) + 1}"
                # if (not self.__subVersionKeysRe.match(verMiddleName)):
                #     self.__currVerName[1] = f"{int(tempLst[0]) + 1}.0"
                # self.__currVerName[2] = "upTime"
                # self.__currVerTime = self.__currVerTime + timedelta(days=self.__CVTLst[1])
                # minDays = abs(minDays - self.__CVTLst[1])

            # TODO 舊程式碼替換中，需要做測試
            # 需要先判斷，才能更換下版本名稱/時間，不然會出問題
            # nextVerName, nextVerTime = GITLib.tryChangeToNextVer(
            #     nextVerName, nextVerTime, CVTLst)
            # TODO 需要做測試
            # 需要先判斷，才能更換下版本名稱/時間，不然會出問題
            self.__tryChangeToNextVer()
        return


    def runPath(self):
        return self.__runPath
    
    @classmethod
    def getVersion(cls):
        return "1.0.0"
    
    @classmethod
    def getVersionTime(cls, currVerName: list = ["v3", "3.7", "upTime"], filePath: str = __file__):
        runPath = os.path.dirname(filePath) + "\\"
        GITimePath = runPath + "GenshinImpactTime.json"
        with open(GITimePath, "r", encoding="utf-8") as fp: # read GITime json file
            if (fp.readable()): jDict = json.load(fp)
        timeFormat = "%Y %m %d"
        for key, value in jDict.items(): # 先讀取 timeFormat and CVTLst 的值
            if (key == "time_format"):
                timeFormat = value
        try:
            return datetime.datetime.strptime(
                    jDict[currVerName[0]][currVerName[1]][currVerName[2]],
                        timeFormat).date()
        except:
            return None
    
    def __tryChangeToNextVer(self): # 用猜測的方式切換到下一個版本
        verSmallName = self.__currVerName[2]
        verMiddleName = self.__currVerName[1]

        if (verSmallName == "upTime"):
            self.__currVerName[2] = "downTime"
            self.__currVerTime = self.__currVerTime + timedelta(days=self.__CVTLst[0])

        elif (verSmallName == "downTime"):
            tempLst = verMiddleName.split(".")
            self.__currVerName[1] = f"{tempLst[0]}.{int(tempLst[1]) + 1}"
            if (not self.__subVersionKeysRe.match(verMiddleName)):
                self.__currVerName[1] = f"{int(tempLst[0]) + 1}.0"
            self.__currVerName[2] = "upTime"
            self.__currVerTime = self.__currVerTime + timedelta(days=self.__CVTLst[1])
        return