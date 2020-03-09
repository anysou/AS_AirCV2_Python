# coding: utf-8
'''
基于 opencv2 

## 调整图片大小
参考: <http://docs.opencv.org/modules/imgproc/doc/geometric_transformations.html#void 
resize(InputArray src, OutputArray dst, Size dsize, double fx, double fy, int interpolation)>
    # 缩小一半：半宽半搞
    small = cv2.resize(image, (0, 0), fx=0.5, fy=0.5)
    # 调整到 固定尺寸
    small = cv2.resize(image, (100, 50))
## 常数
    1: cv2.IMREAD_COLOR       颜色
    0: cv2.IMREAD_GRAYSCALE   灰度
    -1: cv2.IMREAD_UNCHANGED  不变
## 显示图片
    cv2.imshow('image title',img)  
    cv2.waitKey(0)
    cv2.destroyAllWindows()
## 生成空白图像
    size = (height, width, channels) = (512, 256, 3)
    img = np.zeros(size, np.uint8)
## 排序点
    pts = [(0, 7), (3, 5), (2, 6)]
    
    sorted(pts, key=lambda p: p[0]) # sort by point x row, expect [(0, 7), (2, 6), (3, 5)]
## 裁剪图像
    croped = img[y0:y1, x0:x1]
## 查找效果控制： threshold
    
SIFT 是用于图像处理领域的一种描述。这种描述具有尺度不变性，可在图像中检测出关键点，是一种局部特征描述子
运行cv2.xfeatures2d.SIFT_create()时报错,解决方案:
卸载之前的opencv-python和opencv-contrib-python 版本。但这样做视乎没效果，反而影响
最有效方法参见： http://ddrv.cn/a/378607
pip3 uninstall opencv-python -y
pip3 uninstall opencv-contrib-python -y
pip3 install opencv-python==3.4.2.16
pip3 install opencv-contrib-python==3.4.2.16

我选择：pip3 install opencv-contrib-python  安装最新版本，放弃SIFT
1）测试SIFT在图片查找比较中效果不是很理想，慢且不是要的效果。（估计主要用于在人脸识别方面）
2）为了要兼容SIFT而牺牲版本升级的优化，无意义。
'''

__author__ = 'Hongdao <anysou@126.com>'
__copyright__ = 'Copyright (c) 2020, AS Inc.'
__license__ = 'Version 1.0.0'

import numpy as np    #pip3 install numpy 
from PIL import Image #pip3 install pillow
import requests       #pip3 install requests
from requests_toolbelt import MultipartEncoder  #pip3 install requests_toolbelt
import pickle         #相当于java的序列化和反序列化操作，此用于将图片网络传输 dump() 和 load()
import io
import json

try:
    import cv2                      #pip3 install opencv-contrib-python
    print('CV2 版本：'+cv2.__version__)
except ImportError:
    print("cv2 没有安装，请设置cv2_http远程处理") 
 
class AnyCV2:

    def __init__(self):
        self.ver = 'AnyCV2 ver: 1.0.0'
        print(self.ver)
        self.DEBUG = False
        self.FLANN_INDEX_KDTREE = 0
        self.cv2_http = None
        try:
            self.cv2 = cv2.__version__            
        except:
            self.cv2 = None
            self.Aslog('CV2没有安装，如果需要使用，请配置 cv2_http ！')
        
    #====== PIL , CV2 图片 互转 ============    
    def opencv_pil(self,filename):
        img = self.imread(filename)
        return Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
        
    def pil_opencv(self,filename):
        image = Image.open(filename)
        return cv2.cvtColor(np.asarray(image),cv2.COLOR_RGB2BGR)
           
    # 将读取图片为二进制
    def imread_bit(self,filename):
        """
        本地图片读取为二进制
        :param filename: 图片本地地址
        """
        r_file = open(filename,"rb")
        bit = r_file.read()
        r_file.close()
        return bit
           

    # 读取图片
    def imread(self,filename,flags=cv2.IMREAD_UNCHANGED):
        ''' 
        从二进制文件到图片, 图片转为二进制 im.tobytes()
        此函数将确保图片文件名存在 
        '''        
        if(self.cv2):
            im = cv2.imdecode(np.fromfile(filename, dtype=np.uint8),flags)
            if im is None:
                raise RuntimeError("file: '%s' not exists" % filename)
            return im
        elif(self.cv2_http):
            return self.imread_bit(filename)
        else:
            return False
     
     
    # 读取网络图片
    def imread_url(self,url_filename,flags=cv2.IMREAD_UNCHANGED):
        ''' 
        从二进制文件到图片, 图片转为二进制 im.tobytes()
        此函数将确保图片文件名存在 
        '''
        file = requests.get(url_filename)
        im = cv2.imdecode(np.fromstring(file.content, dtype=np.uint8),flags)    #file.content 是读取的远程文件的字节流
        if im is None:
            raise RuntimeError("url_file: '%s' not exists" % url_filename)
        return im
    
    
    # 图片转为二进制流并序列化（用于网络传输）
    def getimg_bit(self,filename):
        fd = open(filename,'rb')
        content = pickle.dumps(fd.read())
        fd.close()
        return content

    # 将读到的二进制流反序列化，转为图片
    def imread_frombit(self,content,flags=cv2.IMREAD_UNCHANGED):
        #fd = pickle.load(io.BytesIO(content))
        fd = pickle.load(io.BytesIO(content))
        im = cv2.imdecode(np.frombuffer(fd, dtype=np.uint8),flags)
        if im is None:
            raise RuntimeError("读取数据流图片失败")
        return im
     
        
    # 写图片
    def imwrite(self,filename,image):
        ''' 
        类似 cv2.imwrite
        '''
        return cv2.imwrite(filename,image)

    # 复制一个图片
    def crop(self,img, xy, end=(0, 0), rect=(0, 0)):
       ''' 复制图片 '''
       (h, w) = img.shape[:2]
       (x1, y1) = (w, h)
       if end != (0, 0):
           (x1, y1) = end
       if rect != (0, 0):
           (x1, y1) = (xy[0]+rect[0], xy[1]+rect[1])
       (x1, y1) = min(max(xy[0], x1), w), min(max(xy[1], y1), h)
       return img[xy[1]:y1, xy[0]:x1]

    # 在图片指定位置做标记
    def mark_point(self,img,xy):
       ''' 调试用的: 标记一个点 '''
       # cv2.rectangle(img, (x, y), (x+10, y+10), 255, 1, lineType=cv2.CV_AA)
       radius = 20   
       cv2.circle(img, (int(xy[0]),int(xy[1])), radius, (0,0,255), thickness=2)
       cv2.line(img, (int(xy[0]-radius), int(xy[1])), (int(xy[0]+radius), int(xy[1])), 255) # x line
       cv2.line(img, (int(xy[0]), int(xy[1]-radius)), (int(xy[0]), int(xy[1]+radius)), 255) # y line
       return img
     
    # 在图片内画出方框范围     
    def mark_size(self,img,xy,width,height,wide=3):
        cv2.line(img,(int(xy[0]),int(xy[1])),(int(xy[0]+width),int(xy[1])),(0,255,0),wide)
        cv2.line(img,(int(xy[0]),int(xy[1])+height),(int(xy[0]+width),int(xy[1])+height),(0,255,0),wide)
        cv2.line(img,(int(xy[0]),int(xy[1])),(int(xy[0]),int(xy[1])+height),(0,255,0),wide)
        cv2.line(img,(int(xy[0]+width),int(xy[1])),(int(xy[0]+width),int(xy[1])+height),(0,255,0),wide)
        return img
    
    # 在图片内根据四个值画方框。 x_min=lift x_max=right y_min=top y_max=bottom   
    def mark_size_4d(self,img,x_min,x_max,y_min,y_max,wide=3):
        cv2.line(img,(int(x_min),int(y_min)),(int(x_max),int(y_min)),(0,255,0),wide)
        cv2.line(img,(int(x_min),int(y_max)),(int(x_max),int(y_max)),(0,255,0),wide)
        cv2.line(img,(int(x_min),int(y_min)),(int(x_min),int(y_max)),(0,255,0),wide)
        cv2.line(img,(int(x_max),int(y_min)),(int(x_max),int(y_max)),(0,255,0),wide)
        return img
        
    # 在图片内画出一条线     
    def mark_line(self,img,xy1,xy2,wide=5):
        cv2.line(img,(int(xy1[0]),int(xy1[1])),(int(xy2[0]),int(xy2[1])),255,wide)
        return img

    # 显示一个图片
    def show(self,img):
        ''' 显示一个图片 '''
        try:
            cv2.imshow('image', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except:
            print('非WINDOWS不支持图片显示')
            
    # 显示一个图片
    def show_byplt(self,img):
        ''' 显示一个图片 
        图像为什么跟原始图像的色彩不一样，或者说像是颜色被翻转了似的，
        因为cv2与matplotlib的显示模式不一致,opencv读取的彩色图像是 BGR 格式，Matplotlib显示彩色图像是 RGB 格式
        '''
        import matplotlib.pyplot as plt   #pip3 install matplotlib
        plt.title('show img')
        plt.imshow(img)
        plt.show()


    # 查找图片位置
    def find_template(self,im_source, im_search, threshold=0.5, rgb=False, bgremove=False):
        '''
        在im_source里查找im_search图片，返回找到图片的位置；没有找到返回None
        @return find location
        if not found; return None
        '''
        result = self.find_all_template(im_source, im_search, threshold, 1, rgb, bgremove)
        return result[0] if result else None


    # 查找所有图片位置
    def find_all_template(self,im_source, im_search, threshold=0.5, maxcnt=0, rgb=False, bgremove=False):
        '''
        使用cv2.templateFind定位图像位置;使用像素匹配查找图片
        Args:
            im_source(string): 图像、素材
            im_search(string): 需要查找的图片
            threshold: 阈值，当相识度小于该阈值的时候，就忽略掉
        Returns:
            A tuple of found [(point, score), ...]
        Raises:
            IOError: when file read error
        '''
        # method = cv2.TM_CCORR_NORMED
        # method = cv2.TM_SQDIFF_NORMED
        method = cv2.TM_CCOEFF_NORMED

        if rgb:
            s_bgr = cv2.split(im_search) # Blue Green Red
            i_bgr = cv2.split(im_source)
            weight = (0.3, 0.3, 0.4)
            resbgr = [0, 0, 0]
            for i in range(3): # bgr
                resbgr[i] = cv2.matchTemplate(i_bgr[i], s_bgr[i], method)
            res = resbgr[0]*weight[0] + resbgr[1]*weight[1] + resbgr[2]*weight[2]
        else:
            s_gray = cv2.cvtColor(im_search, cv2.COLOR_BGR2GRAY)
            i_gray = cv2.cvtColor(im_source, cv2.COLOR_BGR2GRAY)
            # 边界提取(来实现背景去除的功能)
            if bgremove:
                s_gray = cv2.Canny(s_gray, 100, 200)
                i_gray = cv2.Canny(i_gray, 100, 200)

            res = cv2.matchTemplate(i_gray, s_gray, method)
        w, h = im_search.shape[1], im_search.shape[0]

        result = []
        while True:
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
                top_left = min_loc
            else:
                top_left = max_loc
            if self.DEBUG: 
                print('templmatch_value(thresh:%.1f) = %.3f' %(threshold, max_val)) # not show debug
            if max_val < threshold:
                break
            # 计算器中点  calculator middle point
            middle_point = (top_left[0]+w/2, top_left[1]+h/2)
            result.append(dict(
                result=middle_point,
                rectangle=(top_left, (top_left[0], top_left[1] + h), (top_left[0] + w, top_left[1]), (top_left[0] + w, top_left[1] + h)),
                confidence=max_val
            ))
            if maxcnt and len(result) >= maxcnt:
                break
            # 把已发现的区域填平 floodfill the already found area
            cv2.floodFill(res, None, max_loc, (-1000,), max_val-threshold+0.1, 1, flags=cv2.FLOODFILL_FIXED_RANGE)
        return result


    # 查找图片位置；传输给后台服务器处理
    def find_all_template_http_cv2(self,source_bit,search_bit, threshold=0.5,  maxcnt=0, rgb=False, bgremove=False):
        """
        查找图片位置 网络处理
        """
        # 因为POST是混合数据，图片为二进制才有 "source":('source.bit',pickle.dumps(source_bit),'text/plain') 方式
        m = MultipartEncoder(
            fields = {"mode":"find","threshold":str(threshold),"maxcnt":str(maxcnt),"rgb":str(rgb),"bgremove":str(bgremove),
                      "source":('source.bit',pickle.dumps(source_bit),'text/plain'),"search":('search.bit',pickle.dumps(search_bit),'text/plain')
                    }
            )
        try:
            response = requests.post(self.cv2_http, data=m, headers={'Content-Type': m.content_type}, timeout=10)
            
            if response.status_code == 200: 
                rejson =  response.json()
                #rejson = self.http_post(self.cv2_http, params)
                if(rejson and rejson['status']=='ok'):
                    return rejson['data']
                else:
                    return []
            else:
                print(response.status_code)
                return []  
        except Exception as e:
            print('网络异常',e)
            return []


    # -------sift 图像特征--------------------
    def _sift_instance(self,edge_threshold=100):
        try:
            if hasattr(cv2, 'SIFT'):
                return cv2.SIFT(edgeThreshold=edge_threshold)
            return cv2.xfeatures2d.SIFT_create(edgeThreshold=edge_threshold)
        except:
            print('安装的CV2版本 对 cv2.xfeatures2d.SIFT_create 不支持')
            return False

    def sift_count(self,img):
        sift = self._sift_instance()        
        kp, des = sift.detectAndCompute(img, None)
        return len(kp)

    def find_sift(self,im_source, im_search, min_match_count=4):
        '''
        SIFT特征点匹配
        '''
        res = self.find_all_sift(im_source, im_search, min_match_count, maxcnt=1)
        if not res:
            return None
        return res[0]   

    
    def find_all_sift(self,im_source, im_search, min_match_count=4, maxcnt=0):
        '''
            使用sift算法进行多个相同元素的查找
        Args:
            im_source(string): 图像、素材
            im_search(string): 需要查找的图片
            threshold: 阈值，当相识度小于该阈值的时候，就忽略掉
            maxcnt: 限制匹配的数量
        Returns:
            A tuple of found [(point, rectangle), ...]
            A tuple of found [{"point": point, "rectangle": rectangle, "confidence": 0.76}, ...]
            rectangle is a 4 points list
        '''
        sift = self._sift_instance()
        if(not sift):
            return []
        flann = cv2.FlannBasedMatcher({'algorithm': self.FLANN_INDEX_KDTREE, 'trees': 5}, dict(checks=50))

        kp_sch, des_sch = sift.detectAndCompute(im_search, None)
        if len(kp_sch) < min_match_count:
            return None

        kp_src, des_src = sift.detectAndCompute(im_source, None)
        if len(kp_src) < min_match_count:
            return None

        h, w = im_search.shape[1:]

        result = []
        while True:
            # 匹配两个图片中的特征点，k=2表示每个特征点取2个最匹配的点
            matches = flann.knnMatch(des_sch, des_src, k=2)
            good = []
            for m, n in matches:
                # 剔除掉跟第二匹配太接近的特征点
                if m.distance < 0.9 * n.distance:
                    good.append(m)

            if len(good) < min_match_count:
                break

            sch_pts = np.float32([kp_sch[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            img_pts = np.float32([kp_src[m.trainIdx].pt for m in good]).reshape(-1, 1, 2) 

            # M是转化矩阵
            M, mask = cv2.findHomography(sch_pts, img_pts, cv2.RANSAC, 5.0)
            matches_mask = mask.ravel().tolist()

            # 计算四个角矩阵变换后的坐标，也就是在大图中的坐标
            h, w = im_search.shape[:2]
            pts = np.float32([[0, 0], [0, h-1], [w-1, h-1], [w-1, 0]]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)

            # trans numpy arrary to python list
            # [(a, b), (a1, b1), ...]
            pypts = []
            for npt in dst.astype(int).tolist():
                pypts.append(tuple(npt[0]))

            lt, br = pypts[0], pypts[2]
            middle_point = (lt[0] + br[0]) / 2, (lt[1] + br[1]) / 2

            result.append(dict(
                result=middle_point,
                rectangle=pypts,
                confidence=(matches_mask.count(1), len(good)) #min(1.0 * matches_mask.count(1) / 10, 1.0)
            ))

            if maxcnt and len(result) >= maxcnt:
                break
            
            # 从特征点中删掉那些已经匹配过的, 用于寻找多个目标
            qindexes, tindexes = [], []
            for m in good:
                qindexes.append(m.queryIdx) # need to remove from kp_sch
                tindexes.append(m.trainIdx) # need to remove from kp_img

            def filter_index(indexes, arr):
                r = np.ndarray(0, np.float32)
                for i, item in enumerate(arr):
                    if i not in qindexes:
                        r = np.append(r, item)
                return r
            kp_src = filter_index(tindexes, kp_src)
            des_src = filter_index(tindexes, des_src)

        return result

#-------------------------

    # 显示图片的平均亮度
    def brightness(self,im):
        '''
        显示图片的平均亮度
        Args:
            im(numpy): image
        Returns:
            float, average brightness of an image
        '''
        im_hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(im_hsv) 
        height, weight = v.shape[:2]
        total_bright = 0
        for i in v:
            total_bright = total_bright+sum(i)
        return float(total_bright)/(height*weight)
        
    # 查找所有   
    def find_all(self,im_source, im_search,threshold=0.8, maxcnt=0):
        '''
        优先Template，之后Sift
        @ return [(x,y), ...]
        '''           
        if(self.cv2):
            result = self.find_all_template(im_source, im_search, maxcnt=maxcnt,threshold=threshold)
        elif(self.cv2_http):
            result = self.find_all_template_http_cv2(im_source, im_search, maxcnt=maxcnt,threshold=threshold)
            
        if(not result and self._sift_instance()):
            result = self.find_all_sift(im_source, im_search, maxcnt=maxcnt)
            
        if not result:
            return []
        return [match["result"] for match in result]
        
    # 查找一个
    def find(self,im_source, im_search,threshold=0.8):
        '''
        最多只能找到一个对象
        '''
        r = self.find_all(im_source, im_search, maxcnt=1,threshold=threshold)
        return r[0] if r else None


    #================== POST, GET   ==============
    if True:
    
        #----- 字符串MD5加密 -----
        def FN_MD5(self,str):
            ha_md5 = hashlib.md5()  # 创建md5对象
            ha_md5.update(str.encode(encoding='utf-8')) # 此处必须声明encode
            return(ha_md5.hexdigest())

        #=====================POST========================
        # params 要发送的内容（dict格式） add_to_headers 用来添加动态的 headers :例如：Referer:
        def http_post(self,url, params, add_to_headers=None,proxies=None):
            headers = {
                "Accept": "application/json, text/javascript, */*; q=0.01",
                'Content-Type': 'binary',
                'Sec-Fetch-Mode': 'cors',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
            }
            if add_to_headers:
                headers.update(add_to_headers)
                        
            postdata = json.dumps(params) # dumps是将dict转化成str格式,loads是将str转化成dict格式; 
            postdata = params
            try:
                if proxies and proxies!='': #启动代理
                    response = requests.post(url, data=postdata, headers=headers, proxies=proxies, timeout=10)
                else:
                    response = requests.post(url, data=postdata, headers=headers, timeout=10)
                if response.status_code == 200: 
                    return response.json()
                else:
                    print(response.status_code)
                    return False
            except Exception as e:
                print('网络异常',e)
                return False
                    
                    
        def http_get(url, params, add_to_headers=None):
            headers = {
                'Content-type': 'text/html;charset=utf-8',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
            }
            if add_to_headers:
                headers.update(add_to_headers)
                
            if isinstance(params,dict):
                getdata = urllib.parse.urlencode(params)  #将字典形式的数据转化成查询字符串
            else:
                getdata = params
            try:
                response = requests.get(url,headers=headers,timeout=10)        
                if response.status_code == 200:
                    for key,value in response.cookies.items():
                        print(key + '=' + value)
                    return response.json()
                else:
                    return None
            except BaseException as e:
                print("httpGet failed, detail is: "+response.text+" At：",e)
                return None


if __name__ == '__main__':
    import platform                     # 判断操作系统 str(platform.system()) = 'Windows' 'Linux'
    ac = AnyCV2()
    sysname = platform.system()   

  
    while True:
        mode = input("\n请选择结果：1、图片查找和显示；2、查找红包；3、SIFT查找红包；4、拖动滑块；5、图片转为二进制传输再读取；6、调用服务器进行图片查找：") 
        try: 
            mode = int(mode)
        except Exception as e:
            mode = 0        
        if mode<1 or mode>6:
            mode = input("\n请选择结果：1、图片查找和显示；2、查找红包；3、SIFT查找红包；4、拖动滑块；5、图片转为二进制传输再读取；6、调用服务器进行图片查找：") 
        else:
            if(mode==1):
            
                print('\n=====显示图片的平均亮度；find 并在一个图片中查找另一个图片。找到：返回第一个位置的中点坐标；没找到，返回None ====')
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\1s.png')
                    imsch = ac.imread('testdata\\1t.png')    
                else:
                    imsrc = ac.imread('testdata/1s.png')
                    imsch = ac.imread('testdata/1t.png')
                print('被查找图片平均亮度；',ac.brightness(imsrc))
                print('要查找图片平均亮度；',ac.brightness(imsch))
                pt = ac.find(imsrc, imsch)
                print('查找返回结果',pt)
                ac.mark_point(imsrc, pt)
                if(sysname=='Windows'): 
                    ac.show(imsrc)
                else:
                    ac.imwrite('testdata/1s_ok.jpg', imsrc)
                ac.show_byplt(imsrc)
                
                print('\n=====在一个图片中查找另一个图片的所有结果 find_all_template ====')
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\2s.png')
                    imsch = ac.imread('testdata\\2t.png')   
                else:
                    imsrc = ac.imread('testdata/2s.png')
                    imsch = ac.imread('testdata/2t.png') 

                result = ac.find_all_template(imsrc, imsch)
                print("\n找到的所有结果LIST:\n",result)
                pts = []
                for match in result:
                    pt = match["result"]
                    ac.mark_point(imsrc, pt)
                    pts.append(pt)
                pts.sort()
                if(sysname=='Windows'): 
                    ac.show(imsrc)
                else:
                    ac.imwrite('testdata/2s_ok.jpg', imsrc)
                ac.show_byplt(imsrc)
                print("\n所有结果中心位置:\n",pts)
                print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
            elif(mode==2):  
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\temp.png')
                    imsch = ac.imread('testdata\\HB.png')  
                else:
                    imsrc = ac.imread('testdata/temp.png')
                    imsch = ac.imread('testdata/HB.png')
                
                print('\n=====查找红包:在一个图片中查找另一个图片的所有结果 find_all ====')
                result = ac.find_all(imsrc, imsch,0.9)
                print("\n找到的所有结果LIST:\n",result)
                pts = []
                print('\n一共 '+str(len(result)))
                for match in result:
                    ac.mark_point(imsrc, match)
                    pts.append(match)
                pts.sort()
                #ac.show(imsrc)
                if(sysname=='Windows'):
                    ac.imwrite('testdata\\temp_ok.jpg', imsrc)
                else:
                    ac.imwrite('testdata/temp_ok.jpg', imsrc)
                print("\n所有结果中心位置:\n",pts)
                print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
            elif(mode==3):  
                print(ac._sift_instance())
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\temp.png')
                    imsch = ac.imread('testdata\\HB.png')  
                else:
                    imsrc = ac.imread('testdata/temp.png')
                    imsch = ac.imread('testdata/HB.png')
                
                print('\n===== SIFT 在一个图片中查找另一个图片的所有结果 find_all_sift ====')
                result = ac.find_all_sift(imsrc, imsch)
                print("\n找到的所有结果LIST:\n",result)
                if(result!=[]):
                    # [{'result': (604.0, 1039.5), 'rectangle': [(592, 1021), (583, 1054), (616, 1058), (612, 1020)], 'confidence': (4, 4)}]
                    pts = []
                    print('\n一共 '+str(len(result[0]['rectangle'])))
                    for match in result[0]['rectangle']:
                        ac.mark_point(imsrc, match)
                        pts.append(match)
                    pts.sort()
                    #ac.show(imsrc)
                    if(sysname=='Windows'):
                        ac.imwrite('testdata\\temp_ok.jpg', imsrc)
                    else:
                        ac.imwrite('testdata/temp_ok.jpg', imsrc)
                    print("\n所有结果中心位置:\n",pts)
                    print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
            elif(mode==4):
                if(sysname=='Windows'):
                    imsch = ac.imread('testdata\\HK.png')
                else:
                    imsch = ac.imread('testdata/HK.png')
                XY = (44,237)
                width = 995
                height = 580
                x_min = XY[0]+width/6
                x_max = XY[0]+width
                y_min = XY[1]+height/6
                y_max = XY[1]+height/6*5
                
                HK_XY = (82,924)
                HK_width = 72
                HK_height = 72
                HK_ZX = (HK_XY[0]+HK_width/2,HK_XY[1]+HK_height/2)
                
                print('\n=====在一个图片中查找另一个图片的所有结果 find_all ====')
                
                for i in [1,2,3,4,5,6]:
                    print('\n'+str(i)+'：')
                    if(sysname=='Windows'):
                        imsrc = ac.imread('testdata\\HK'+str(i)+'.png')
                    else:
                        imsrc = ac.imread('testdata/HK'+str(i)+'.png')
                    
                    for j in [0.3]: #0.9,0.85,0.8,0.79,0.78,0.76,0.75,0.7,0.65,0.6           
                        result = ac.find_all(imsrc, imsch,j)
                        if(len(result)>=1):
                            match = result[0]
                            for match in result:
                                if(match[0]>x_min and match[0]<x_max and match[1]>y_min and match[1]<y_max):
                                    print('YES ',match)
                                    ac.mark_point(imsrc, match)
                                    ac.mark_size(imsrc, XY,width,height)
                                    ac.mark_size_4d(imsrc,x_min,x_max,y_min,y_max)
                                    ac.mark_line(imsrc,HK_ZX,(match[0],HK_ZX[1]),wide=5)
                                    break
                    if(sysname=='Windows'):       
                        ac.imwrite('testdata\\Z'+str(i)+'_ok.jpg', imsrc)
                    else:
                        ac.imwrite('testdata/Z'+str(i)+'_ok.jpg', imsrc)
            elif(mode==5):
                print('\n读取图片为二进制，再进行序列化（可用于网络传输）')
                
                if(sysname=='Windows'):
                    http_bit = ac.getimg_bit('testdata\\1s.png')
                else:
                    http_bit = ac.getimg_bit('testdata/1s.png')
                
                print('模拟读到网络传来的数据')
                if(sysname=='Windows'):
                    ac.show(ac.imread_frombit(http_bit))
                else:
                    ac.show_byplt(ac.imread_frombit(http_bit))
                    
                print('\n下面读取网上图片 https://www.baidu.com/img/bd_logo1.png 的方法')
                img = ac.imread_url('https://www.baidu.com/img/bd_logo1.png')

                if(sysname=='Windows'):
                    ac.show(img)
                else:
                    ac.show_byplt(img)
            elif(mode==6):
                temp = ac.cv2
                ac.cv2 = None
                #ac.cv2_http = 'http://127.0.0.1:8080/AnyCV2/' 
                ac.cv2_http = 'http://139.162.110.93:8888/AnyCV2/'                
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\2s.png')
                    imsch = ac.imread('testdata\\2t.png')   
                else:
                    imsrc = ac.imread('testdata/2s.png')
                    imsch = ac.imread('testdata/2t.png') 

                result = ac.find_all(imsrc, imsch)
                ac.cv2 = temp
                pts = []
                print('\n一共 '+str(len(result)))
                for match in result:
                    pts.append(match)
                pts.sort()
                print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
   

    


