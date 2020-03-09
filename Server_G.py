import hashlib  #---- md5--
import random   #产生随机数

import logging.config  #写日志用上的三个模块
import os
import time
import json 
import datetime


# -------------腾讯云短信SDK----------------
from qcloudsms_py import SmsSingleSender    # pip install qcloudsms_py
from qcloudsms_py.httpclient import HTTPError
import ssl
ssl._create_default_https_context = ssl._create_unverified_context  #全局取消证书验证
#-------------------------------------------

class S_GV():  # 将全局变量放在S_GV命名空间里

 
    # 连接MySQL数据库 , 如果连接不上， 百度 “ 开启mysql的远程访问权限”
    # 登陆服务器，打开MYSQL COMMAD:  use mysql;  select host,user,password from user; update user set host = '%' where user = 'root' and host = 'localhost';
    # 修改回来： update user set host = 'localhost' where user = 'root' and host = '%';
    conn_ip =  '139.162.124.76' #'119.23.201.106'
    conn_port = 3306
    conn_user = 'root'
    conn_pass = '123456' #'ANYSOU_mysql'
    conn_db = 'bjk'
    conn_char = 'utf8'
    conn_isok = True  
     
    #------ 数据库的默认空时间----
    def FN_DATATIME(istime):
        istime = str(istime)
        if istime=='0000-00-00 00:00:00':
            return ('')
        else:
            return (istime)
    
    #----- 字符串MD5加密 -----
    def FN_MD5(str):
        ha_md5 = hashlib.md5()  # 创建md5对象
        ha_md5.update(str.encode(encoding='utf-8')) # 此处必须声明encode
        return(ha_md5.hexdigest())
    
    #------ 产生6位随机数--------
    def FN_6D():
        PASS = ''
        for i in range(6):
            PASS = PASS + str(random.randint(1,9))
        return(PASS)
    #print(FN_6D())
    
    #----------------------------  腾讯云配置信息 -----------------------------
    # 短信应用SDK AppID
    sms_appid = 1400067318  # SDK AppID是1400开头
    # 短信应用SDK AppKey
    sms_appkey = "d366f543d7d2fa9271089a2c7f2d6198"
    # 签名
    sms_sign = "宏道实业"     
    # ----------------------- 腾讯云短信函数------------------------------------
    def FN_SMS_SEND(sms_appid,sms_appkey,phone,template_id,params,sms_sign,ext=''):
        ssender = SmsSingleSender(sms_appid, sms_appkey)
        result=''
        try:
            result = ssender.send_with_param(86, phone,template_id, params, sign=sms_sign, extend="", ext="")  # 签名参数未提供或者为空时，会使用默认签名发送短信
        except HTTPError as e:        
            return(str(e))
        except Exception as e:
            return(str(e))        
        if result['result']==0:
            return True
        else:
            return(result)  
    #-----------------------------------------------------------------------------------

    # ------------加密 jmkey字符串加密KEY---------------------------
    def FN_encrypt(s,modkey=0,jmkey=168):
        jmkey = jmkey + modkey
        b = bytearray(str(s).encode("gbk"))
        n = len(b) # 求出 b 的字节数
        c = bytearray(n*2)
        j = 0
        for i in range(0, n):
            b1 = b[i]
            b2 = b1 ^ jmkey # b1 = b2^ jmkey
            c1 = b2 % 16
            c2 = b2 // 16 # b2 = c2*16 + c1
            c1 = c1 + 65
            c2 = c2 + 65 # c1,c2都是0~15之间的数,加上65就变成了A-P 的字符的编码
            c[j] = c1
            c[j+1] = c2
            j = j+2
        return c.decode("gbk")

    # --------------解密----------------------------------------
    def FN_decrypt(s,modkey=0,jmkey=168):
        jmkey = jmkey + modkey
        c = bytearray(str(s).encode("gbk"))
        n = len(c) # 计算 b 的字节数
        if n % 2 != 0 :
            return ""
        n = n // 2
        b = bytearray(n)
        j = 0
        for i in range(0, n):
            c1 = c[j]
            c2 = c[j+1]
            j = j+2
            c1 = c1 - 65
            c2 = c2 - 65
            b2 = c2*16 + c1
            b1 = b2^ jmkey 
            b[i]= b1
        try:
            return b.decode("gbk")
        except:
            return "failed"
            
            
    
        
    #--------------------------------------- 定义一个日志--------------------------------------------------------

    #=====================================================================================
    # logging框架中主要由四个部分组成：
        # Loggers: 可供程序直接调用的接口
        # Handlers: 决定将日志记录分配至正确的目的地
        # Filters: 提供更细粒度的日志是否输出的判断
        # Formatters: 制定最终记录打印的格式布局
    # 级别 NOTSET=0 DEBUG=10 INFO=20 WARNING=30 ERROR=40 CRITICAL=50
    
    # basicConfig()会做以下两件事：1)添加默认的处理器 2)添加默认的格式化器（formatter）
    

#------------------------ 日志文件夹和文件名处理 ----------------------------------------------------
    # 获取当前文件路径,并在下面加一个LOGS目录
    logfile_dir = os.getcwd()+'\\logs'    
    #logfile_dir = os.path.dirname(os.path.abspath(__file__))+'\\logs'  # 这个方法效果同上

    # 如果不存在定义的日志目录就创建一个
    if not os.path.isdir(logfile_dir):
        os.mkdir(logfile_dir)

    # log文件的全路径
    # logfile_name = 'test.log'  # log文件名
    # logfile_path = os.path.join(logfile_dir, logfile_name)
    #print(logfile_path)

    #------------------------ 日志配置字典 ---------------------------------------------------------------
    LOGGING_DIC = {
        'version': 1,
        'disable_existing_loggers': False,
        
        #产生日志的对象
        #负责产生日志，然后交给Filter过滤，然后交给不同的Handler输出
        # 级别 NOTSET=0 DEBUG=10 INFO=20 WARNING=30 ERROR=40 CRITICAL=50
        'loggers': {
        
            #Root 定义一个空的key  logging.getLogger(__name__)拿到的logger配置
            '': {
                'handlers': ['TO_Screen', 'TO_File', 'TO_ErrorFile','TO_CriticalFile'],
                'level': 'DEBUG',
                
            },
            
            #WorkLogger1  logging.getLogger('WorkLogger1')拿到的logger配置
            'WorkLogger1': {
                'handlers': ['TO_Screen', 'TO_File1', 'TO_ErrorFile1','TO_CriticalFile'],
                'level': 'INFO',
                'propagate': False,  # 不会传给''Root
            },
            
            #SimpleLogger  logging.getLogger('SimpleLogger')拿到的logger配置 
            # 'SimpleLogger': {
                # 'handlers': ['TO_Screen', 'TO_SimpleFile'],
                # 'level': 'INFO',
                # 'propagate': True,  # 向上（更高level的logger）会传给''Root
            # },
            
            #Screen  logging.getLogger('ScreenLoger')拿到的logger配置 
            'ScreenLoger': {
                'handlers': ['TO_Screen'],
                'level': 'DEBUG',
                'propagate': False,  
            }
        },
        
        #过滤日志的对象，不常用，略
        'filters': {},
        
        
        #可以定制不同的日志格式对象，然后绑定给不同的Handler对象使用，以此来控制不同的Handler的日志格式
        'formatters': {
            'form_file': { #格式输出到文件
                'format': '[%(asctime)s][%(filename)-10s] line=%(lineno)d：%(levelname)-9s = %(message)s \n'
                #'format': '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d][%(levelname)s][%(message)s]'
            },
            'form_file1': { #格式输出到文件
                'format': '[%(asctime)s] [%(threadName)s:%(thread)d] [task_id:%(name)s][%(filename)-10s] line=%(lineno)d：%(levelname)-9s = %(message)s \n'
            },
            'form_screen': { #格式输出到终端屏幕
                #'format': '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
                'format': '[%(asctime)s] [%(filename)-10s] line=%(lineno)d：%(levelname)-9s = %(message)s \n'
            },
            'form_SimpleFile': { #格式出到文件上的简单模式
                'format': '[%(asctime)s] %(message)s'
            }
        },

        
        #接收日志然后控制打印到不同的地方，FileHandler用来打印到文件中，StreamHandler用来打印到终端
        'handlers': {
            #打印到终端的日志
            'TO_Screen': {
                'level': 'WARNING',
                'class': 'logging.StreamHandler',
                'formatter': 'form_screen'
            },

            #打印到文件的日志,收集info及以上的日志
            'TO_File': {
                'level': 'WARNING',
                'class': 'logging.handlers.TimedRotatingFileHandler',  # 保存到文件，自动按时间切
                'filename': os.path.join(logfile_dir, "HB_MainInfo.log"),  # 日志文件
                'when': 'midnight', # when 参数可设置为S（按秒），M（按分钟），H（按小时），D（按天分割）W0-W6（星期） midnight (子夜)
                'interval' :1,
                'backupCount': 30,
                'formatter': 'form_file',
                'encoding': 'utf-8',
            },
            #打印到文件的日志:收集错误及以上的日志
            'TO_ErrorFile': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
                'filename': os.path.join(logfile_dir, "HB_MainError.log"),  # 日志文件
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 10,
                'formatter': 'form_file',
                'encoding': 'utf-8',
            },
            #打印到文件的日志:收集重要信息，比如什么时候下单，什么时候盈利了，将对接短信通知
            'TO_CriticalFile': {
                'level': 'CRITICAL',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
                'filename': os.path.join(logfile_dir, "HB_MainCritical.log"),  # 日志文件
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 10,
                'formatter': 'form_file',
                'encoding': 'utf-8',
            },
            #打印到文件的日志,收集info及以上的日志
            'TO_File1': {
                'level': 'WARNING',
                'class': 'logging.handlers.TimedRotatingFileHandler',  # 保存到文件，自动按时间切
                'filename': os.path.join(logfile_dir, "Get_GRID.log"),  # 日志文件
                'when': 'midnight', # when 参数可设置为S（按秒），M（按分钟），H（按小时），D（按天分割）W0-W6（星期） midnight (子夜)
                'interval' :1,
                'backupCount': 30,
                'formatter': 'form_file1',
                'encoding': 'utf-8',
            },
            #打印到文件的日志:收集错误及以上的日志
            'TO_ErrorFile1': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
                'filename': os.path.join(logfile_dir, "Get_GRID_Error.log"),  # 日志文件
                'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                'backupCount': 10,
                'formatter': 'form_file',
                'encoding': 'utf-8',
            }
            #,
            #打印到文件的日志
            # 'TO_SimpleFile': {
                # 'level': 'INFO',
                # 'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
                # 'filename': os.path.join(logfile_dir, "simple.log"),
                # 'maxBytes': 1024 * 1024 * 5,  # 日志大小 5M
                # 'backupCount': 10,
                # 'formatter': 'form_SimpleFile',
                # 'encoding': "utf-8"
            # }
        },
        
        
    }

    #==== 调用该配置===============================
    logging.config.dictConfig(LOGGING_DIC)
   
    HB_Loger = logging.getLogger(__name__)
    
    # HB_Loger.debug('This is debug message')
    # HB_Loger.info('This is info message')
    # HB_Loger.warning('This is warning message')
    # HB_Loger.error('This is error message')
    # HB_Loger.critical('This is critical 关键 message')
    
    #HBS_Loger = logging.getLogger('ScreenLoger')
    #HBS_Loger.critical('This is info message')

#==============  下例子是用多线程来调用日志 ============================================================
# 方法：从Thread继承，并重写run()
# import threading
# import time

# class MyThread(threading.Thread):
    # def __init__(self,threadName,istime): #定义初始化， self自己（固定），线程名字，其他参数
        # threading.Thread.__init__(self,name = threadName) #父类初始化
        ###super(MyThread, self).__init__() #注意：一定要显式的调用父类的初始化函数。这句与上句效果一样
        # self.istime = istime      #参数
        # self.ScreenLoger = logging.getLogger('ScreenLoger')  #专用来输出到屏蔽
        # self.WorkLoger = logging.getLogger('WorkLogger1')    #专用来记录日志         
        #####print ('self.logger = %s' % self.ScreenLoger) #看日志者是谁
        
    # def run(self): #定义每个线程要运行的函数
        # i = 0 
        # self.WorkLoger.info('--- 线程日志开始 ----')
        # while True:
            # self.ScreenLoger.info('此日志者，只显示在终端，不写文件 '+str(i))
            # i += 1
            # print (i)
            # if i> 10:
                # break            
            # time.sleep(self.istime)
        # self.WorkLoger.info('--- 线程日志结束 ----')
        
# p1 = MyThread('test',1)
# p1.start()

#======================================================================================


 