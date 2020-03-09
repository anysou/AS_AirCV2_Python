#---- TB_USER \ TB_SMSINFO \ TB_TRADE --------
import pymysql                  #python连接数据库 安装方式 pip install pymysql
from Server_G import *      #引用共用配置文件
import datetime

#-连接MySQL数据库 ---------------
def is_Conn():
    conn = ''
    try:
        conn = pymysql.connect(host=S_GV.conn_ip,port=S_GV.conn_port,user=S_GV.conn_user,password=S_GV.conn_pass,db=S_GV.conn_db,charset=S_GV.conn_char) #连接MySQL数据库            
    except Exception as e:
        #print(e)
        S_GV.conn_isok = False
        S_GV.HB_Loger.error('连接数据库异常: '+str(e))
    return (conn)
#print(is_Conn())

if False:
    #--------------------- 产生注册密钥 -----------------------------
    _letter_cases = "abcdefghjkmnpqrstuvwxy" # 小写字母，去除可能干扰的i，l，o，z
    _upper_cases = _letter_cases.upper() # 大写字母
    _numbers = ''.join(map(str, range(1, 10))) # 数字
    field = ''.join((_upper_cases, _numbers))

    def getRandom(size):
        return "".join(random.sample(field,size))

    def generate(group,size):
        return "-".join([getRandom(size) for i in range(group)])


    # -----生成注册密钥请求 -----------------------
    def FN_MakeKey(post_dict,USER_IP,modkey):
        re_dict={} 
        on_post_data = True #提交数据格式是否正确

        if type(post_dict) != dict:
            on_post_data = False
        else:
            L = int(post_dict.get('L',0))
            USER_PHONE = post_dict.get('USER_PHONE','')
            USER_PASS  = post_dict.get('USER_PASS','')
            KEY_ANUM  = post_dict.get('KEY_ANUM',0) 
            MODE  = post_dict.get('MODE',0)
            K_MODE  = post_dict.get('K_MODE','A')
            POST_PHONE = post_dict.get('POST_PHONE','')
            USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密       
            if len(USER_PHONE)!=11 or len(USER_PASS)!=32:
                on_post_data = False          
          
        if on_post_data == False:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '1'
            re_dict['err-msg'] = ['提交参数有误','Parameters are mistaken'][L]
            return (re_dict) 

        if S_GV.FN_MD5(USER_PHONE[:3]+'|anysou|'+USER_PHONE[7:11])==USER_PASS or S_GV.FN_MD5(USER_PHONE[:3]+'|123456|'+USER_PHONE[7:11])==USER_PASS: #不是管理员密码
            pass
        else:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '1'
            re_dict['err-msg'] = ['密钥请求权限有误','Key request permissions are mistaken'][L]
            return (re_dict)     

        conn = is_Conn()        
        if S_GV.conn_isok == False:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '0'
            re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
            return (re_dict)
        else:    
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型
            
        if MODE==0:
            sql = "select K_KEY,K_MODE from TB_REG_KEY where K_REG_PHONE='' and  K_PHONE='%s' " % (USER_PHONE)
            #print(sql)
            try:
                cur.execute(sql)
                result = cur.fetchall()
            except Exception as e:
                conn.rollback() #错误回滚
                print('查询出错：',e)
            
            re_dict['status'] = 'ok'
            if not result:            
                re_dict['data'] = ''
            else:        
                re_dict['data'] = result
                
        elif MODE==-1: 
            sql = "select K_MODE,K_KEY,DATE_FORMAT(K_PUT_TIME,'%%Y-%%m-%%d %%T') as K_PUT_TIME,K_REG_PHONE,K_USER_NAME,DATE_FORMAT(K_REG_TIME,'%%Y-%%m-%%d %%T') as K_REG_TIME  from TB_REG_KEY where K_REG_PHONE<>'' and  K_PHONE='%s' " % (USER_PHONE)
            #print(sql)
            try:
                cur.execute(sql)
                result = cur.fetchall()
            except Exception as e:
                conn.rollback() #错误回滚
                print('查询出错：',e)
            #print(result)
            re_dict['status'] = 'ok'
            if not result:            
                re_dict['data'] = ''
            else:        
                re_dict['data'] = result
        
        elif MODE==1:
            #-- 处理相关数据 - 
            keys=[]
            i = 1
            while i<=KEY_ANUM:  
                key_temp = generate(4,5)
                #print(key_temp)
                #如果这可以KEY不在本列表中、也不在数据库里，
                if keys.count(key_temp)==0:            
                    S_TIME = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    sql ="insert into TB_REG_KEY (K_KEY,K_PHONE,K_PUT_TIME,K_REG_PHONE,K_REG_TIME,K_MODE) "
                    sql = sql +" values ('%s','%s','%s','%s','%s','%s')" % (key_temp,USER_PHONE,S_TIME,'','0000-00-00 00:00:00',K_MODE)
                    try:
                        cur.execute(sql)  #像sql语句传递参数              
                        conn.commit()     #提交
                        keys.append(key_temp) 
                        i +=1
                    except Exception as e:
                        conn.rollback() #错误回滚 
                        #print(e)
            re_dict['status'] = 'ok'
            re_dict['data'] = keys
            
        elif MODE==100:
            sql = "select count(*) as NUMER from TB_REG_KEY where K_REG_PHONE='' and  K_PHONE='%s' " % (USER_PHONE)
            #print(sql)
            try:
                cur.execute(sql)
                result = cur.fetchone()
            except Exception as e:
                conn.rollback() #错误回滚
                print('查询出错：',e)
            
            re_dict['status'] = 'ok'
            if not result:            
                re_dict['data'] = 0
            else:        
                re_dict['data'] = result
                
        elif MODE==200:
            if KEY_ANUM<=0 or len(POST_PHONE)!=11:
                re_dict['status'] = 'error'
                re_dict['err-code'] = '-1'
            else:   
                sql = "select K_KEY,K_MODE from TB_REG_KEY where K_REG_PHONE='' and  K_PHONE='%s' " % (USER_PHONE)
                #print(sql)
                try:
                    cur.execute(sql)
                    result = cur.fetchmany(KEY_ANUM)
                    #print(result)
                    for item in result:
                        s_key = eval(str(item))['K_KEY']
                        sql = "update TB_REG_KEY set K_PHONE='%s' where K_KEY='%s'" % (POST_PHONE,s_key)
                        #print(sql)
                        cur.execute(sql)               
                        conn.commit()
                    re_dict['status'] = 'ok'
                    re_dict['data'] = result
                except Exception as e:
                    conn.rollback() #错误回滚
                    print('查询出错：',e)
                    re_dict['status'] = 'error'
                    re_dict['err-code'] = '-2'        
        
        cur.close()   #关闭指针对象       
        conn.close()  #关闭数据库    
        return(re_dict) 


    # -----激活注册密钥请求 -----------------------
    def FN_RegKey(post_dict,USER_IP,modkey):
        re_dict={} 
        on_post_data = True #提交数据格式是否正确

        if type(post_dict) != dict:
            on_post_data = False
        else:
            L = int(post_dict.get('L',0))
            USER_PHONE = post_dict.get('USER_PHONE','')
            K_KEY  = post_dict.get('K_KEY','')
            K_MODE = post_dict.get('K_MODE','')
            MODE  = post_dict.get('MODE','')
            K_USER_NAME = post_dict.get('K_USER_NAME','')
            USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密 
            K_KEY = S_GV.FN_decrypt(K_KEY,modkey)        
            if len(USER_PHONE)!=11 or len(K_KEY)!=23 or len(MODE)!=1:
                on_post_data = False          
          
        if on_post_data == False:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '1'
            re_dict['err-msg'] = ['提交参数有误','Parameters are mistaken'][L]
            return (re_dict)   

        conn = is_Conn()        
        if S_GV.conn_isok == False:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '0'
            re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
            return (re_dict)
        else:    
            cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型

        if MODE=='0':
            sql = "select * from TB_REG_KEY where K_KEY='%s' " % (K_KEY)
            #print(sql)
            try:
                cur.execute(sql)
                result = cur.fetchone()
            except Exception as e:
                conn.rollback() #错误回滚
                print('查询出错：',e)        
            
            re_dict['status'] = 'ok'
            if not result:            
                re_dict['PHONE'] = '0'
            else:   
                if result['K_REG_PHONE']!='':
                    re_dict['PHONE'] = '-1'
                else:
                    re_dict['PHONE'] = result['K_PHONE']                
                    re_dict['K_MODE'] = result['K_MODE']
                
        else:        

            S_TIME = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            try:            
                sql = "select * from TB_USER where USER_PHONE='%s' " % (USER_PHONE)
                cur.execute(sql)
                result = cur.fetchone()
                SMS_NUM = int(result['SMS_NUM'])
                
                if result['USER_TYPE']=='0':
                    TEST_TIME = str((datetime.datetime.now() + datetime.timedelta(days =90)).strftime("%Y-%m-%d %H:%M:%S")) # 当前时间+90天
                    sql = "update TB_USER set USER_TYPE='1',USER_MODE='%s',SMS_NUM=250,FIRST_TIME='%s',TEST_TIME='%s' where USER_PHONE='%s'" % (K_MODE,S_TIME,TEST_TIME,USER_PHONE)
                    SMS_NUM = 250
                else:   
                    T_TIME = datetime.datetime.strptime(str(result['TEST_TIME']), "%Y-%m-%d %H:%M:%S")
                    TEST_TIME = str(( T_TIME + datetime.timedelta(days =90)).strftime("%Y-%m-%d %H:%M:%S")) # 当前时间+90天
                    sql = "update TB_USER set USER_MODE='%s',SMS_NUM=SMS_NUM+250,TEST_TIME='%s' where USER_PHONE='%s'" % (K_MODE,TEST_TIME,USER_PHONE)
                    SMS_NUM = SMS_NUM + 250
                #print(sql)   
                cur.execute(sql)  #像sql语句传递参数              
                conn.commit()  #提交
                sql ="update TB_REG_KEY set K_REG_PHONE='%s',K_REG_TIME='%s',K_USER_NAME='%s' where K_KEY='%s'" % (USER_PHONE,S_TIME,K_USER_NAME,K_KEY)
                cur.execute(sql)  #像sql语句传递参数              
                conn.commit()  #提交
                
                re_dict['status'] = 'ok' 
                re_dict['TEST_TIME'] = TEST_TIME
                re_dict['SMS_NUM'] = str(SMS_NUM)
            except Exception as e:
                conn.rollback() #错误回滚 
                re_dict['status'] = 'error'
                re_dict['err-msg'] = ['更新注册码数据库异常','Update the registration code database exception'][L]
        
        cur.close()   #关闭指针对象       
        conn.close()  #关闭数据库    
        return(re_dict) 

        
# --------根据用户的注册手机号码和登陆密码，记录登陆信息,获取用户的相关信息-------
#---POST的数据字典、用户的IP地址，加密修正值---
def FN_UserInfo(post_dict,USER_IP,modkey):
    re_dict={} 
    re_dict['status'] = 'error'
    on_post_data = True
    if type(post_dict) != dict:
        on_post_data = False
    else:
        L = int(post_dict.get('L',0))                   #语言代号
        W = int(post_dict.get('W',0))                   #当前已运行的软件数量
        LOGIN = int(post_dict.get('LOGIN',0))           #登陆   
        USER_PHONE = post_dict.get('USER_PHONE','')        
        USER_PASS  = post_dict.get('USER_PASS','')
        CODE = post_dict.get('CODE','')
        USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密
        CODE = S_GV.FN_decrypt(CODE,modkey)              # 机器码解密        
        #if len(USER_PHONE)!=11 or len(USER_PASS)!=32:
        if len(USER_PASS)!=32 or len(CODE)<6:
            on_post_data = False
            
    if on_post_data == False:
        re_dict['err-code'] = '1'
        re_dict['err-msg'] = ['提交参数有误','Parameters are mistaken'][L]
        return (re_dict)
        
    #------ 生成返回机器验证码 -------------
    rekey = random.randint(1,9)  # 产生1位数字的随机加密修正值
    re_dict['num'] = rekey       # 返回CODE的加密数
    re_dict['code'] = S_GV.FN_encrypt(CODE[0:modkey],rekey) #产生返回CODE
    
        
    conn = is_Conn()        # 连接数据库
    if S_GV.conn_isok == False:
        re_dict['err-code'] = '0'
        re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
        return (re_dict)
    else:    
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型     
    
    #--- 用户名+密码：查询用户所有信息 -------
    sql = "select * from TB_USER where USER_PHONE='%s' and USER_PASS='%s'"  % (USER_PHONE,USER_PASS)  
    try:
        cur.execute(sql)
        result = cur.fetchone()
    except Exception as e:
        conn.rollback() #错误回滚
        print('查询出错：',e)
    
    if not result: #不存在，用户名查
        sql = "select * from TB_USER where USER_PHONE='%s'"  % (USER_PHONE)
        try:
            cur.execute(sql)
            result = cur.fetchone()
        except Exception as e:
            conn.rollback() #错误回滚
            print('查询出错：',e)        
        if result:
            re_dict['err-code'] = '2'
            re_dict['err-msg'] = ['提交用户密码错误','Submitting a user password error'][L] 
        else:
            re_dict['err-code'] = '3'
            re_dict['err-msg'] = ['提交用户名'+USER_PHONE+'不存在','The "'+USER_PHONE+'" does not exist'][L]
            
    else: #用户和密码有效
    
        #====1) 用户是否失效 =================
        if result['IS_OK']=='0': #用户已经失效
            re_dict['err-code'] = '4'
            re_dict['err-msg'] = ['用户已失效！','用户已失效！'][L] 
            
        else: # 有效
        
            #=== 2) 是否为测试用户，且过期
            if result['IS_TEST']=='1': #测试用户
                #-- 用户是不是测试，且已过期
                sql = "select * from TB_USER where USER_PHONE='%s' and TEST_TIME<=NOW() "  % (USER_PHONE)
                #print(sql)
                try:
                    cur.execute(sql)
                    result_O = cur.fetchone()
                except Exception as e:
                    conn.rollback() #错误回滚
                    print('查询出错：',e)
                
                if result_O:     #是测试用户,到测试时间
                    re_dict['err-code'] = '5'
                    re_dict['err-msg'] = ['测试用户已到期！','测试用户已到期！'][L] 
                else:
                    re_dict['status'] = 'ok'
                    
            else: #=== 3) 不是测试用户
            
                #====4) 原来,没记录，则记录，OK -----------
                if result['PC_CODE']=='': #原来没有机器码，则添加
                    re_dict['status'] = 'ok'
                    sql = "update TB_USER set PC_CODE='%s' where USER_PHONE='%s'" % (CODE,USER_PHONE) 
                    try:
                        cur.execute(sql)
                        result_U = cur.fetchone()
                    except Exception as e:
                        conn.rollback() #错误回滚
                        print('查询出错：',e) 
                
                else: #==== 5) 有记录，看是否要核对
                    if result['IS_PC']=='1':
                        if result['PC_CODE']==CODE:
                            re_dict['status'] = 'ok'                    
                        else:
                            re_dict['err-code'] = '6'
                            re_dict['err-msg'] = ['用户机身码不对！','用户机身码不对！'][L] 
                    else:
                        re_dict['status'] = 'ok'
                    
            #--- 合法登陆，返回相关信息 --------------------
            if re_dict['status'] == 'ok':
                if W > result['MAX_W']:
                    re_dict['status'] = 'error'
                    re_dict['err-code'] = '7'
                    re_dict['err-msg'] = ['已超过该账户最大启动量'+str(result['MAX_W'])+'！','已超过该账户最大启动量'+str(result['MAX_W'])+'！'][L] 
                else:
                    re_data = {}
                    re_data['IS_TEST'] = result['IS_TEST']
                    re_data['TEST_TIME'] = S_GV.FN_DATATIME(result['TEST_TIME'])
                    re_data['LOG_INFO'] = result['LOG_INFO']                              #是否记录日志
                    re_data['GAME_INFO'] = result['GAME_INFO']                            #是否记录游戏过程       
                    re_dict['data'] = re_data        
                                
                    #---- 记录登陆信息 ----
                    L_TIME = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    sql ="insert into TB_LOGIN (USER_PHONE,L_TIME,USER_IP) values ('%s','%s','%s')" % (USER_PHONE,L_TIME,USER_IP)
                    try:  
                        cur.execute(sql)  #像sql语句传递参数              
                        conn.commit()  #提交
                    except Exception as e:              
                        conn.rollback() #错误回滚 
                        S_GV.HB_Loger.error('记录登陆信息异常: '+str(e))
                        
            
    cur.close()  #关闭指针对象       
    conn.close()  #关闭数据库
    return(re_dict)
    

# -------- 是否为合法用户 -------
def FN_IsUser(post_dict,USER_IP,modkey):
    re_dict={} 
    on_post_data = True
    if type(post_dict) != dict:
        on_post_data = False
    else:
        L = int(post_dict.get('L',0))                   #语言代号
        USER_PHONE = post_dict.get('USER_PHONE','')        
        USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密
        
    conn = is_Conn()        # 连接数据库
    if S_GV.conn_isok == False:
        re_dict['status'] = 'error'
        re_dict['err-code'] = '0'
        re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
        return (re_dict)
    else:    
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型     
    
    sql = "select * from TB_USER where USER_PHONE='%s' and IS_OK='1'"  % (USER_PHONE)  
    try:
        cur.execute(sql)
        result = cur.fetchone()
    except Exception as e:
        conn.rollback() #错误回滚
        print('查询出错：',e)
    
    if not result:
        re_dict['status'] = 'error'
        re_dict['err-code'] = '1'
        re_dict['err-msg'] = ['用户已失效！','用户已失效！'][L]
    else:
        if result['IS_TEST']=='1': #如果是测试用户
            sql = "select * from TB_USER where USER_PHONE='%s' and TEST_TIME<=NOW() "  % (USER_PHONE)
            try:
                cur.execute(sql)
                result = cur.fetchone()
            except Exception as e:
                conn.rollback() #错误回滚
                print('查询出错：',e)                
            if result:
                re_dict['status'] = 'error'
                re_dict['err-code'] = '2'
                re_dict['err-msg'] = ['用户试用期已到！','用户试用期已到！'][L] 
            else:
                re_dict['status'] = 'ok'             
            
    cur.close()  #关闭指针对象       
    conn.close()  #关闭数据库
    return(re_dict)
   
# -----修改、重置用户的密码 -------
#---用户的登陆手机号码、用户原密码、用户新密码、用户的IP地址，加密修正值---
# 1）用户修改密码：用户提交手机号码、原密码MD5、新密码MD5  
def FN_ModiPass(post_dict,USER_IP,modkey):
    re_dict={} 
    on_post_data = True  #提交数据格式是否正确
    is_modi = False      #是否需要更新密码
    is_reset = False     #是不是重置密码   
    if type(post_dict) != dict:
        on_post_data = False
    else:
        L = int(post_dict.get('L',0))
        USER_PHONE = post_dict.get('USER_PHONE','')
        USER_PASS  = post_dict.get('USER_PASS','')
        NEW_PASS  = post_dict.get('NEW_PASS','')         
        USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密       
        if len(USER_PASS)!=32 or len(NEW_PASS)!=32:
            on_post_data = False          
            
    if on_post_data == False:
        re_dict['status'] = 'error'
        re_dict['err-code'] = '1'
        re_dict['err-msg'] = ['提交参数有误','Parameters are mistaken'][L]
        return (re_dict)        

    conn = is_Conn()        
    if S_GV.conn_isok == False:
        re_dict['status'] = 'error'
        re_dict['err-code'] = '0'
        re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
        return (re_dict)
    else:    
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型 
    
    #--处理相关数据 -  
    sql = "select * from TB_USER where USER_PHONE='%s'"  % (USER_PHONE)
    try:
        cur.execute(sql)
        result = cur.fetchone()
    except Exception as e:
        conn.rollback() #错误回滚
        print('查询出错：',e)
        
    if not result:
        re_dict['status'] = 'error'
        re_dict['err-code'] = '3'
        re_dict['err-msg'] = ['提交用户名'+USER_PHONE+'不存在！','submission username '+USER_PHONE+' does not exist! '][L]
    else:        
        old_pass = result['USER_PASS']  #获取旧密码
        
        if USER_PASS!=NEW_PASS and USER_PASS!=old_pass:
            re_dict['status'] = 'error'
            re_dict['err-code'] = '2'
            re_dict['err-msg'] = ['提交原始密码错误！','Submission of the original password error!'][L]
            is_modi = False
        elif USER_PASS!=NEW_PASS and USER_PASS==old_pass: #是修改密码
            is_modi = True
        elif USER_PASS==NEW_PASS: #是重置密码，产生随机6位数字密码
            if S_GV.FN_MD5(USER_PHONE[:3]+'|anysou|'+USER_PHONE[7:11])==USER_PASS or S_GV.FN_MD5(USER_PHONE[:3]+'reset'+USER_PHONE[7:11])==USER_PASS:                
                is_modi = True
                is_reset = True
                USER_PASS = S_GV.FN_6D()
                NEW_PASS = S_GV.FN_MD5(USER_PASS)                    
            else:
                re_dict['status'] = 'error'
                re_dict['err-code'] = '1'
                re_dict['err-msg'] = ['提交参数有误！','Submission parameters are mistaken!'][L]
                is_modi = False
            
        if is_modi==True:  #是修改密码
            sql ="update TB_USER set USER_PASS='%s' where USER_PHONE='%s'" % (NEW_PASS,USER_PHONE)            
            try:  
                cur.execute(sql)  #像sql语句传递参数              
                conn.commit()  #提交
                re_dict['status'] = 'ok'
                re_dict['data'] = ['修改保存用户密码信息成功！','Modify and save user password information successfully!'][L]                 
            except Exception as e:              
                conn.rollback() #错误回滚  
                print('修改保存用户密码时发生错误',e)
                S_GV.HB_Loger.error('修改保存用户密码时发生错误: '+str(e))
                re_dict['status'] = 'error'
                re_dict['err-code'] = '4'
                re_dict['err-msg'] = ['修改保存用户密码时发生错误','An error occurred when modifying the password to save the user'][L]
                is_reset = False
                
            if is_reset == True:
                re_dict['data'] = ['用户密码重置成功，请注意接收新密码短信！','User password reset successfully, please pay attention to receive new password SMS!'][L]
                #--发信息通知 USER_PASS ------
                # --------------发短信-----------------------
                template_id = 91490  # 尊敬的用户，您的登陆重置密码为{1}。登陆系统后，可修改为方便您记忆的密码。{2}
                params = [USER_PASS]
                smstemp = ''
                if SMS_NUM < 50:
                    smstemp = '短信余'+ str(SMS_NUM-1)+'条'
                params.append(smstemp)      # 重置密码短信发给注册手机
                try:
                    Log_info = S_GV.FN_SMS_SEND(S_GV.sms_appid,S_GV.sms_appkey,USER_PHONE,template_id,params,S_GV.sms_sign,'')
                except Exception as e:
                    print('发短信错误',e)
                    Log_info = False
                
                if Log_info != True:
                    print('发密码重置短信错误: '+str(Log_info))
                    re_dict={}
                    re_dict['status'] = 'error'
                    re_dict['err-code'] = '5'
                    re_dict['err-msg'] = '用户密码重置成功，发送密码短信时发生错误！' 
                else: #--修改短信数量 -                       
                    sql ="update TB_USER set SMS_NUM=SMS_NUM-1 where USER_PHONE='%s'" % (USER_PHONE)
                    try:  
                        cur.execute(sql)  #像sql语句传递参数              
                        conn.commit()  #提交
                    except Exception as e:              
                        conn.rollback() #错误回滚  
                        print('重置密码修改用户短信量时发生错误',e)
                        S_GV.HB_Loger.error('重置密码修改用户短信量时发生错误: '+str(e))
            
    cur.close()   #关闭指针对象       
    conn.close()  #关闭数据库    
    return(re_dict)

# -------- 记录提交的游戏结果 -------
#---POST的数据字典、用户的IP地址，加密修正值---
def FN_PostData(post_dict,USER_IP,modkey):
    re_dict={} 
    re_dict['status'] = 'error'
    on_post_data = True
    if type(post_dict) != dict:
        on_post_data = False
    else:
        L = int(post_dict.get('L',0))                   #语言代号
        USER_PHONE = post_dict.get('USER_PHONE','')        
        DATA  = post_dict.get('DATA','')        
        USER_PHONE = S_GV.FN_decrypt(USER_PHONE,modkey)  # 用户手机号码解密
        if not isinstance(DATA,list):
            on_post_data = False
            
    if on_post_data == False:        
        re_dict['err-code'] = '1'
        re_dict['err-msg'] = ['提交数据有误,不是LIST','Parameters are mistaken'][L]
        return (re_dict)        
        
    conn = is_Conn()        # 连接数据库
    if S_GV.conn_isok == False:
        re_dict['err-code'] = '0'
        re_dict['err-msg'] = ['连接数据库异常','Connection database exception'][L]
        return (re_dict)
    else:    
        cur = conn.cursor(cursor=pymysql.cursors.DictCursor) #设游标类型为字典类型     
    
    
    for info in DATA:    
        sql ="insert into TB_INFO (USER_PHONE,T_TIME,T_NO,T_STAKE,T_SEAT,T_YK,T_LS,T_S,T_E,T_MODE,T_OVER) "
        sql = sql +"values ('%s','%s','%s','%s','%s','%f','%f','%f','%f','%s','%s')" \
              % (USER_PHONE,info['T_TIME'],info['T_NO'],info['T_STAKE'],info['T_SEAT'],info['T_YK'],info['T_LS'],info['T_S'],info['T_E'],info['T_MODE'],'0')
        try:  
            cur.execute(sql)  #像sql语句传递参数              
            conn.commit()     #提交
            re_dict['status'] = 'ok'
        except Exception as e:              
            conn.rollback() #错误回滚 
            S_GV.HB_Loger.error('记录游戏结果异常: '+str(e))
            re_dict['err-msg'] = '记录游戏结果异常'
            cur.close()  #关闭指针对象       
            conn.close()  #关闭数据库
            return(re_dict)
            
    cur.close()  #关闭指针对象       
    conn.close()  #关闭数据库
    return(re_dict)
    
    