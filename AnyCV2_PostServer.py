#-*- coding:utf-8 -*-
# 本案例是调用WEB.PY的方法。
# python AnyCV2_PostServer.py    # 默认是8080端口  cd F:\PycharmProjects\huobi\WORK\web.py
# python AnyCV2_PostServer.py 8081
# sudo ufw enable
# sudo ufw allow 8080
# sudo ufw status

import web                     # 安装方式 pip3 install web.py==0.40.dev0
import json                    # JSON
from AnyCV2 import AnyCV2      # 引入

web.config.debug = False       #关闭调试功能

R_Dict={}  # 全局
R_Dict['status'] = 'error'
R_Dict['err-code'] = '-1'

# 定义url路由,按顺序下面查找,匹配到就返回
# 第一部分是匹配URL的正则表达式，像/、/help/faq、/item/(\d+)等(\d+将匹配数字)。圆括号表示捕捉对应的数据以便后面使用。
# 第二部分是接受请求的类名称，
urls= (  
    '/AnyCV2/(.*)','Any_CV2',                    # AnyCV2 图像查找
    # '/userinfo/(.*)','UserInfo',                # 用户登陆
    # '/userinfo/(.*)','UserInfo',                # 用户登陆
    # '/isuser/(.*)','IsUser',                    # 是不是用户
    # '/modipass/(.*)','ModiPass',                # 修改重置用户密码    
    # '/postdata/(.*)','PostData',                # 记录交易信息和AT    
    # '/getreport/(.*)','GetReport',              # 获取用户报表 
    # '/gethistory/(.*)','GetHistory',            # 获取用户历史记录    
    # '/downfile/','DownFile',                    # 下载文件 /downfile/?filename=
    # '/(.*)','AnyCV2_PostServer',
    )
    
app= web.application(urls,globals())

#base为基础模板页, 所有模板页存放在 templates 目录下面。
render = web.template.render('templates/',base="base")

# web.input() 获取url参数，用于GET;post请求包。返回web.utils.Storage格式，可以直接.参数名来获取参数值
# web.data() 获取实体正文，用POST请求包， 返回bytes格式.

class Any_CV2:    
    def POST(self,name):
        Strm = '用户登陆'
        print('\nAny_CV2 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP =  web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        #modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        
        #params = {"mode":"find","source":pickle.dumps(source_bit),"search":pickle.dumps(search_bit),"threshold":threshold,"maxcnt":0,"rgb":rgb,"bgremove":bgremove}
        post_data = web.input(mode='',source=None,search=None,threshold=0.8,maxcnt=0,rgb=False,bgremove=False)
        mode =  post_data.mode
        source =  post_data.source
        search = post_data.search
        threshold =  float(post_data.threshold)
        maxcnt =  int(post_data.maxcnt)
        rgb =  post_data.rgb
        bgremove = post_data.bgremove
        if(rgb=='False'):
            rgb = False
        else:
            rgb = True
        if(bgremove=='False'):
            bgremove = False
        else:
            bgremove = True
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        try:
            if(mode=='find'):
                ac = AnyCV2()
                im_source = ac.imread_frombit(source)
                #ac.show(im_source)
                im_search = ac.imread_frombit(search)
                result = ac.find_all_template(im_source, im_search, threshold, maxcnt, rgb, bgremove)                
                R_Dict['err-code'] = '0'
                R_Dict['status'] = 'ok'
                R_Dict['data'] = result
                #print(R_Dict)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('UserInfo 返回 '+Strm,R_Dict)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 


class UserInfo:    
    def POST(self,name):
        Strm = '用户登陆'
        print('UserInfo 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP =  web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        # R_Dict = FN_UserInfo(post_dict,USER_IP,modkey)
        # print(R_Dict)
        try:
            R_Dict = FN_UserInfo(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('UserInfo 返回 '+Strm,R_Dict)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 
   
class IsUser:    
    def POST(self,name):
        Strm = '用户是否有效'
        print('IsUser 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP =  web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        try:
            R_Dict = FN_IsUser(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('IsUser 返回 '+Strm)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 
   
class ModiPass:
    def POST(self,name): 
        Strm = '修改/重置用户密码请求'
        print('ModiPass 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP = web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        try:
            R_Dict = FN_ModiPass(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('ModiPass 返回 '+Strm)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式

class PostData:
    def POST(self,name):
        Strm = '记录交易信息'
        print('PostData 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP = web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------
        global R_Dict
        try:
            R_Dict = FN_PostData(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))           
        print('PostData 返回 '+Strm)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 
     
class GetReport:
    def POST(self,name):
        Strm = '获取用户报表数据'
        print('GetReport 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP =  web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        try:
            R_Dict = FN_GetReport(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('GetReport 返回 '+Strm)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 

class GetHistory:
    def POST(self,name):
        Strm = '获取用户历史记录'
        print('GetHistory 收到 '+Strm)         
        #------- 获取HTTP的相关数据----------------------------        
        USER_IP =  web.ctx.env['REMOTE_ADDR']
        http_time= web.ctx.env.get('HTTP_TIME','')
        modkey = int(http_time[len(http_time)-1:len(http_time)])         
        #------- POST 数据解析，并将输入数据转为DICT------------
        post_data = web.data()  # 获得POST内容二进制文件格式
        post_str=str(post_data, encoding='utf-8')  # 转换为字符串模式
        post_dict= json.loads(post_str) # 将字符串转为DICT
        # -----采用 text/json 格式回复-------------------------
        web.header('Content-Type','text/json;charset=UTF-8') 
        #-------------------------------------------------------        
        #--------- 调用相关处理函数-----------------------------------
        global R_Dict
        try:
            R_Dict = FN_GetHistory(post_dict,USER_IP,modkey)
        except Exception as e:
            R_Dict['err-msg'] = '--- '+USER_IP+' '+Strm+' ---'
            print(R_Dict['err-msg'])
            S_GV.HB_Loger.error(str(R_Dict['err-msg']))             
        print('GetHistory 返回 '+Strm)        
        return json.dumps(R_Dict)  #dumps 是将dict转化成str格式 
        
class DownFile:  
    def GET(self): 
        BUF_SIZE = 1024
        get_data = web.input(filename='',filemode='')
        filemode =  get_data.filemode  # 文件名模式        
        file_name = get_data.filename  # 文件名 
        if file_name == '':
            if filemode == 'WG':
                file_name = 'W'+S_GV.W_SYS_VER+'.exe'
            elif filemode == 'WGPDF':
                file_name = 'M'+S_GV.M_SYS_VER+'.pdf'
            elif filemode == 'BEA':
                file_name = 'BEA'+S_GV.BEA_SYS_VER+'.exe'
            elif filemode == 'MD':
                file_name = 'M'+S_GV.M_SYS_VER+'.exe'
            elif filemode == 'MDPDF':
                file_name = 'M'+S_GV.M_SYS_VER+'.pdf'
            elif filemode == 'ZC':
                file_name = 'BEA-R.exe'
            elif filemode == 'ZCPDF':
                file_name = 'BEA-R.pdf'
            else:
                file_name = 'BEA.RAR'                
        file_path = os.path.join('DownFiles', file_name)   #给文件加路径名        
        #file_path = os.getcwd()+'\\DownFiles\\'+ file_name  #效果一样

        try:
            file_size = os.path.getsize(file_path)
        except Exception as e:
            file_size = -1

        f = None  
        try:               
            web.header('Content-Type','application/octet-stream')  
            web.header('Content-disposition', 'attachment;filename=%s' % file_name)  #文件名
            web.header('Content-Length',str(file_size)) #文件大小，关键
            if file_size == -1:
                return
                
            f = open(file_path, "rb")
            while True:  
                c = f.read(BUF_SIZE)  
                if c:  
                    yield c
                else:  
                    break  
        except Exception as e:  
            print (e)  
            yield 'Error'  
        finally:  
            if f:  
                f.close() 

class AnyCV2_PostServer:
    #get请求方法,name为请求的路径
    def GET(self,name):
        return render.index()  # 跳转到 index.html
    #post请求
    def POST(self,name):
        return render.index()  # 跳转到 index.html     

if __name__== "__main__":

    #----- web.py 0.36---------------------------
    # from web.wsgiserver import CherryPyWSGIServer  
    # from web.wsgiserver.ssl_builtin import BuiltinSSLAdapter 
    # ssl_cert = '/ssl/caimouse.crt'
    # ssl_key = '/ssl/caimouse.key'      
    # CherryPyWSGIServer.ssl_adapter = BuiltinSSLAdapter(ssl_cert,ssl_key,None) 
    
    #----- web.py 0.37---------------------------
    # from cherrypy import CherryPyWSGIServer  # SSL  pip3 install cherrypy
    # ssl_cert = 'ssl/caimouse.crt'
    # ssl_key = 'ssl/caimouse.key'
    # CherryPyWSGIServer.ssl_certificate = ssl_cert
    # CherryPyWSGIServer.ssl_private_key = ssl_key
    
    #----- web.py 0.4---------------------------
    # from cheroot.server import HTTPServer    # pip3 install cheroot
    # from cheroot.ssl.builtin import BuiltinSSLAdapter
    # HTTPServer.ssl_adapter = BuiltinSSLAdapter(
            # certificate='ssl/server.crt', 
            # private_key='ssl/server.key') 
            
    app.run()    
