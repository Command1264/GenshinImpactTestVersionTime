import json, datetime, re, os
from datetime import date, timedelta
# TODO 可以用 list 先把有要加的事件存起來，最後再加一遍
# TODO 優化獲取版本名稱、時間的方式，不然 1.3 會出問題
class GIDateMoney:
    def __init__(self, # FINISH? TODO
                startDate: date = date.today(),
                endDate: date = (date.today() + datetime.timedelta(days = 1)),
                filePath: str = __file__):
        self.__runPath = os.path.dirname(filePath) + "\\" # __file__ 的資料夾路徑
        self.__GITimePath = self.__runPath + "GenshinImpactTime.json" # json 檔案絕對路徑
        self.__versionKeysRe = re.compile("v[1-7]") # 大版本的正則表達式(在幾年內應該沒問題)
        self.__subVersionKeysRe = re.compile("[1-7].[0-8]") # 小版本的正則表達式(在幾年內應該沒問題)
        self.__startDate = startDate # 起始天
        if (endDate >= startDate): # 如果結束天 >= 起始天
            self.__endDate = endDate # 普通結束天
        else:
            # 將結束天-起始天的絕對值，加到起始天
            self.__endDate = startDate + timedelta(days = abs((endDate - startDate).days))

        self.__diffDays = abs(self.__endDate - self.__startDate) # 計算差距
        self.__jDict = dict() # 將 json 讀進來這裡面
        self.__timeFormat = "%Y %m %d" # 時間格式解碼
        self.__CVTLst = [20, 22] # 上/下版本相差天數
        # self.__minDays = 0 # 當作計算從 startdate 到下一個版本的時間暫存器
        self.__cantFindFlag = False # 已經從 json 找不到對應的版本內容(True)

        self.__currVerTime = None # 目前版本時間
        self.__currVerName = None # 目前版本資訊
        self.__nextVerTime = None # 下個版本時間
        self.__nextVerName = None # 下個版本資訊

        # self.__nextVerTime = None
        # self.__nextVerName = None

        # self.__readBasic()
        self.readVerTime()
        return # end
    
    def getCurrTime(self): # FINISH
        return self.__currVerTime # end
    
    def getCurrName(self): # FINISH
        return self.__currVerName # end

    def __readBasic(self): # FINISH
        with open(self.__GITimePath, "r", encoding="utf-8") as fp: # read GITime json file
            if (fp.readable()): self.__jDict = json.load(fp)
        for key, value in self.__jDict.items(): # 先讀取 timeFormat and CVTLst 的值
            if (key == "time_format"):
                self.__timeFormat = value
            if (key == "changeVersionTime"):
                self.__CVTLst = list(self.__jDict[key].values())
                # CVTLst = [jDict[key]["up"], jDict[key]["down"]]
        return # end

    # 讀取版本時間
    def readVerTime(self): # FINISH
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
                        # if ((rangeDays.days <= 0 and self.__minDays <= 0) or (flag[0] and flag[1] and flag[2])):
                        # 判斷如果是找到了 startDate 最接近的未來日期，或是已經是最後一筆資料了
                        if ((rangeDays.days <= 0) or all(flag)):
                            # if ()
                            minDays = rangeDays.days
                            VerTime = datetime.datetime.strptime(value3, self.__timeFormat).date()
                            VerName = [key, key2, key3]
                            allBreakFlag = True
                            break
                    if (allBreakFlag): break # 處理提前跳脫
            if (allBreakFlag): break # 處理提前跳脫

        self.__currVerName = VerName
        self.__currVerTime = VerTime

        if (minDays > 0): # 成立代表沒有在 json 裡面找到相對應的時間
            self.__tryToFindVerTime(minDays)
        return # end
        
    def __tryToFindVerTime(self, minDays): # 來到這代表無法靠 json 找到時間，只能用猜測的 FINISH
        self.__cantFindFlag = True
        while(minDays > 0):
            if (self.__currVerName[2] == "upTime"): minDays -= self.__CVTLst[0]
            elif (self.__currVerName[2] == "downTime"): minDays -= self.__CVTLst[1]
            # 遇到例外狀況，嘗試修復
            # TODO 需要用另一種判斷方式，不然又出現像是 1.3 那樣會出問題 
            # else: self.readVerTime()

            # 需要先判斷，才能更換下版本名稱/時間，不然會出問題
            self.__tryChangeToNextVer()
        return # end


    def runPath(self): # FINISH
        return self.__runPath # end
    
    @classmethod
    def getVersion(cls): # FINISH
        return "0.1.0" # end
    
    # @classmethod
    # def getVersionTime(cls, currVerName: list = ["v3", "3.7", "upTime"], filePath: str = __file__):
    #     runPath = os.path.dirname(filePath) + "\\"
    #     GITimePath = runPath + "GenshinImpactTime.json"
    #     with open(GITimePath, "r", encoding="utf-8") as fp: # read GITime json file
    #         if (fp.readable()): jDict = json.load(fp)
    #     timeFormat = "%Y %m %d"
    #     for key, value in jDict.items(): # 先讀取 timeFormat and CVTLst 的值
    #         if (key == "time_format"):
    #             timeFormat = value
    #     try:
    #         return datetime.datetime.strptime(
    #                 jDict[currVerName[0]][currVerName[1]][currVerName[2]],
    #                     timeFormat).date()
    #     except:
    #         return None # end
    
    # 用猜測的方式切換到下一個版本 TODO
    # def __tryChangeToNextVer(self) -> tuple[list, datetime.date]:
    def __tryChangeToNextVer(self):
        verName = self.__currVerName
        verTime = self.__currVerTime
        if (verName[2] == "upTime"):
            verName[2] = "downTime"
            verTime = verTime + timedelta(days=self.__CVTLst[0])

        elif (verName[2] == "downTime"):
            tempLst = verName[1].split(".")
            verName[1] = f"{tempLst[0]}.{int(tempLst[1]) + 1}"
            # 如果小版本已經要跳大版本了
            if (not self.__subVersionKeysRe.match(verName[1])):
                verName[1] = f"{int(tempLst[0]) + 1}.0" # 將小版本改成 "(原本版本 + 1).0"
                # 將大版本改成 "v(原本版本 + 1)"
                verName[0] = "v" + str(int(str(verName[0]).replace("v", "")) + 1)
            verName[2] = "upTime"
            verTime = verTime + timedelta(days=self.__CVTLst[1])
        self.__currVerName = verName
        self.__currVerTime = verTime
        return # end
    
    # 用讀取的方式切換到下一個版本 TODO
    # def __changeToNextVer(self) -> tuple[list, datetime.date]:
    def __changeToNextVer(self):
        # __versionKeysRe = re.compile("v[1-4]")
        # __subVersionKeysRe = re.compile("[1-4].[0-8]")
        # cantFindFlag = False
        verBigName = self.__currVerName[0]
        verMiddleName = self.__currVerName[1]
        verSmallName = self.__currVerName[2]

        if (verSmallName == "upTime"):
            verSmallName = "downTime" # 更換小版本
            # self.__currVerTime = datetime.datetime.strptime(
            #         self.__jDict[self.__currVerName[0]][self.__currVerName[1]][self.__currVerName[2]],
            #             self.__timeFormat).date()

        elif(verSmallName == "downTime"):
            tempLst = verMiddleName.split(".")
            # 更換至下一個中版本
            verMiddleName = f"{tempLst[0]}.{int(tempLst[1]) + 1}"

            # 如果不符合預測的小版本號(加到超出.8)，就更換成下一個大版本
            if (not self.__subVersionKeysRe.match(verMiddleName)):
                verMiddleName = f"{int(tempLst[0]) + 1}.0" # 將小版本改成 "(原本版本 + 1).0"
                # 將大版本改成 "v(原本版本 + 1)"
                verBigName = "v" + str(int(str(verBigName).replace("v", "")) + 1)

            verSmallName = "upTime" # 更換小版本

        try: # 嘗試使用讀取的方式取得
            tempVerTime = datetime.datetime.strptime(
                self.__jDict[verBigName][verMiddleName][verSmallName],
                    self.__timeFormat).date()
            self.__currVerName = [verBigName, verMiddleName, verSmallName]
            self.__currVerTime = tempVerTime
        except KeyError: # 如果不行，就用猜測的方式
            # nextVerTime = nextVerTime + timedelta(days=self.__CVTLst[1])
            cantFindFlag = True # 將標籤設為使用猜測方式
            self.__tryChangeToNextVer() # 使用猜測方式
        return # end
    
    def getResult(self):
        result = 0
        haveVerPackCode = False
        # fo = open("testOP1.txt", "w", encoding="utf-8")
        # fo.write(f"currVerName: {self.__currVerName}")
        # fo.write(f" currVerTime: {self.__currVerTime}\n")
        for i in range(self.__diffDays.days + 1):
            printVer = False
            logLst = [[0, 0], [0, 0, 0, 0], [0, 0], 0]
            tempSum = 0
            diffT = timedelta(days = 0)
            tempDate = (self.__startDate + timedelta(days=i))

            # if (tempDate.month != (self.__startDate + timedelta(days=i - 1)).month and (i > 0)): fo.write("\n")
            # fo.write(f"tempTime: {tempDate}")

            # 計算非版本原石
            tempDateDay = tempDate.day
            tempSum += (60 + 90) # 每日的任務 + 月卡
            logLst[0] = [1, 1]
            # HoYoLab網頁簽到
            if (tempDateDay == 4 or tempDateDay == 11 or tempDateDay == 18):
                tempSum += 20
                logLst[2][0] = 1
            # 遊戲內商店每月1號可以買糾纏之緣 * 5，折合800原石(160 * 5)
            if (tempDateDay == 1):
                tempSum += (160 * 5)
                logLst[2][1] = 1
            # 深淵穩過 11-3， 12 層後面再說
            if (tempDateDay == 1 or tempDateDay == 16):
                tempSum += (150 * 3) + (50 * 0)
                logLst[3] = 1
            ###########################


            # 更換下個版本
            # 會放在版本原石預測的前面是因為，如果放在後面，版本維護會沒有判斷到，導致少了 300 原石
            # TODO 這裡要改成如果 json 有的化，要從 json 讀取，沒有再用預測的
            if (tempDate == (self.__currVerTime + 
                    timedelta(days = self.__CVTLst[0] if (self.__currVerName[2] == "upTime") else self.__CVTLst[1]))): 
                
                if (self.__cantFindFlag):
                    # 此處寫的是使用預測的寫法
                    self.__tryChangeToNextVer()
                else:
                    # 此處寫的是使用資料庫的寫法
                    self.__changeToNextVer()
                printVer = True


            # 計算版本原石
            if (tempDate >= self.__currVerTime):
                diffT = tempDate - self.__currVerTime
                if (self.__currVerName[2] == "upTime"):
                    if (haveVerPackCode): haveVerPackCode = False
                    if (diffT.days == 0):
                        tempSum += 300 # 猜測第 0 天可以拿完版本維護的 300 原石
                        logLst[1][2] = 1
                    elif (diffT.days == 7):
                        tempSum += 1000 # 猜測第 7 天可以拿完大活動的 1000 原石
                        logLst[1][0] = 1
                    elif (diffT.days == 14):
                        tempSum += 420 # 猜測第 14 天可以拿完小活動之 1 的 420 原石
                        logLst[1][1] = 1
                elif(self.__currVerName[2] == "downTime"):
                    if (diffT.days == 7 or diffT.days == 14):
                        tempSum += 420 # 猜測第 7 / 14 天可以拿完小活動之 2 / 3 的 420 原石
                        logLst[1][1] = 1
                    # 猜測在下半結束的前兩個禮拜的禮拜五會有兌換碼
                    if (tempDate >= (self.__currVerTime + timedelta(days= self.__CVTLst[1] - 14)) and (not haveVerPackCode)):
                        if (tempDate.isoweekday() == 5):
                            haveVerPackCode = True
                            tempSum += 300
                            logLst[1][3] = 1
                            # print(tempTime)
            ######################################
            result += tempSum

            # fo.write(f" week: {tempDate.isoweekday()}")
            # fo.write(" diffT: %2d" % diffT.days)
            # fo.write(f" logLst: {logLst}")
            # fo.write(" tempSum: %5d" % tempSum)
            # # fo.write(" result: %5d" % result)
            # if (printVer):
            #     fo.write(f" currVerName: {self.__currVerName}")
            #     fo.write(f" currVerTime: {self.__currVerTime}")
            #     printVer = False
            
            # fo.write("\n")
        return result
