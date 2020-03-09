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

import cv2            #pip3 install opencv-python 
import numpy as np    #pip3 install numpy 

DEBUG = False

def crop(img, xy, end=(0, 0), rect=(0, 0)):
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
def mark_point(img,xy):
   ''' 调试用的: 标记一个点 '''
   # cv2.rectangle(img, (x, y), (x+10, y+10), 255, 1, lineType=cv2.CV_AA)
   radius = 20   
   cv2.circle(img, (int(xy[0]),int(xy[1])), radius, (0,0,255), thickness=2)
   cv2.line(img, (int(xy[0]-radius), int(xy[1])), (int(xy[0]+radius), int(xy[1])), 255) # x line
   cv2.line(img, (int(xy[0]), int(xy[1]-radius)), (int(xy[0]), int(xy[1]+radius)), 255) # y line
   return img
 
# 在图片内画出方框范围     
def mark_size(img,xy,width,height,wide=3):
    cv2.line(img,(int(xy[0]),int(xy[1])),(int(xy[0]+width),int(xy[1])),(0,255,0),wide)
    cv2.line(img,(int(xy[0]),int(xy[1])+height),(int(xy[0]+width),int(xy[1])+height),(0,255,0),wide)
    cv2.line(img,(int(xy[0]),int(xy[1])),(int(xy[0]),int(xy[1])+height),(0,255,0),wide)
    cv2.line(img,(int(xy[0]+width),int(xy[1])),(int(xy[0]+width),int(xy[1])+height),(0,255,0),wide)
    return img
    
 # 在图片内根据四个值画方框。 x_min=lift x_max=right y_min=top y_max=bottom    
def mark_size_4d(img,x_min,x_max,y_min,y_max,wide=3):
    cv2.line(img,(int(x_min),int(y_min)),(int(x_max),int(y_min)),(0,255,0),wide)
    cv2.line(img,(int(x_min),int(y_max)),(int(x_max),int(y_max)),(0,255,0),wide)
    cv2.line(img,(int(x_min),int(y_min)),(int(x_min),int(y_max)),(0,255,0),wide)
    cv2.line(img,(int(x_max),int(y_min)),(int(x_max),int(y_max)),(0,255,0),wide)
    return img
    
# 在图片内画出一条线     
def mark_line(img,xy1,xy2,wide=5):
    cv2.line(img,(int(xy1[0]),int(xy1[1])),(int(xy2[0]),int(xy2[1])),255,wide)
    return img
    
    
# 显示一个图片
def show(img):
    ''' 显示一个图片 '''
    try:
        cv2.imshow('image', img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except:
        print('非WINDOWS不支持图片显示')
        
        
# 显示一个图片
def show_byplt(img):
    ''' 显示一个图片 
    图像为什么跟原始图像的色彩不一样，或者说像是颜色被翻转了似的，
    因为cv2与matplotlib的显示模式不一致,opencv读取的彩色图像是 BGR 格式，Matplotlib显示彩色图像是 RGB 格式
    '''
    import matplotlib.pyplot as plt   #pip3 install matplotlib
    plt.title('show img')
    plt.imshow(img)
    plt.show()

def imread(filename,flags=cv2.IMREAD_UNCHANGED):
    ''' 
    类似 cv2.imread
    此函数将确保图片文件名存在 
    '''
    im = cv2.imdecode(np.fromfile(filename, dtype=np.uint8),flags)
    if im is None:
        raise RuntimeError("file: '%s' not exists" % filename)
    return im
    
def imwrite(filename,image):
    ''' 
    写图片 类似 cv2.imwrite
    '''
    return cv2.imwrite(filename,image)

def find_template(im_source, im_search, threshold=0.5, rgb=False, bgremove=False):
    '''
    在im_source里查找im_search图片，返回找到图片的位置；没有找到返回None
    @return find location
    if not found; return None
    '''
    result = find_all_template(im_source, im_search, threshold, 1, rgb, bgremove)
    return result[0] if result else None

def find_all_template(im_source, im_search, threshold=0.5, maxcnt=0, rgb=False, bgremove=False):
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
        if DEBUG: 
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



# -------sift 图像特征--------------------
def _sift_instance(edge_threshold=100):
    try:
        if hasattr(cv2, 'SIFT'):
            return cv2.SIFT(edgeThreshold=edge_threshold)
        return cv2.xfeatures2d.SIFT_create(edgeThreshold=edge_threshold)
    except:
        print('安装的CV2版本 对 cv2.xfeatures2d.SIFT_create 不支持')
        return False


def sift_count(img):
    sift = _sift_instance()
    kp, des = sift.detectAndCompute(img, None)
    return len(kp)

def find_sift(im_source, im_search, min_match_count=4):
    '''
    SIFT特征点匹配
    '''
    res = find_all_sift(im_source, im_search, min_match_count, maxcnt=1)
    if not res:
        return None
    return res[0]
    

FLANN_INDEX_KDTREE = 0

def find_all_sift(im_source, im_search, min_match_count=4, maxcnt=0):
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
    sift = _sift_instance()
    if(not sift):
        return []
    flann = cv2.FlannBasedMatcher({'algorithm': FLANN_INDEX_KDTREE, 'trees': 5}, dict(checks=50))

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

def find_all(im_source, im_search,threshold=0.8, maxcnt=0):
    '''
    优先Template，之后Sift
    @ return [(x,y), ...]
    '''
    result = find_all_template(im_source, im_search,maxcnt=maxcnt,threshold=threshold)
    if(not result and self._sift_instance()):
        result = find_all_sift(im_source, im_search, maxcnt=maxcnt)
    if not result:
        return []
    return [match["result"] for match in result]

def find(im_source, im_search,threshold=0.8):
    '''
    最多只能找到一个对象
    '''
    r = find_all(im_source, im_search, maxcnt=1,threshold=threshold)
    return r[0] if r else None

def brightness(im):
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

def main():
    import os
    d = os.path.dirname(__file__)  #返回当前文件所在的目录   # __file__ 为当前文件     
    parent_path = os.path.dirname(d)            #获得d所在的目录,即d的父级目录  
    #parent_path  = os.path.dirname(parent_path) ##获得parent_path所在的目录即parent_path的父级目录

    print('\n==== 显示图片颜色常量 ===')
    print(cv2.IMREAD_COLOR)
    print(cv2.IMREAD_GRAYSCALE)
    print(cv2.IMREAD_UNCHANGED)
    print(cv2.COLOR_BGR2HSV)
    print(cv2.COLOR_BGR2GRAY)
    
    print('\n=====显示图片的平均亮度；find 并在一个图片中查找另一个图片。找到：返回第一个位置的中点坐标；没找到，返回None ====')
    imsrc = imread(os.path.join(parent_path,'testdata\\1s.png'))
    imsch = imread(os.path.join(parent_path,'testdata\\1t.png'))
    print('被查找图片平均亮度；',brightness(imsrc))
    print('要查找图片平均亮度；',brightness(imsch))
    pt = find(imsrc, imsch)
    print('查找返回结果',pt)
    mark_point(imsrc, pt)
    show(imsrc)
    

    print('\n=====在一个图片中查找另一个图片的所有结果 ====')
    imsrc = imread(os.path.join(parent_path,'testdata\\2s.png'))
    imsch = imread(os.path.join(parent_path,'testdata\\2t.png'))
    result = find_all_template(imsrc, imsch)
    print("\n找到的所有结果LIST:\n",result)
    pts = []
    for match in result:
        pt = match["result"]
        mark_point(imsrc, pt)
        pts.append(pt)
    pts.sort()
    show(imsrc)
    print("\n所有结果中心位置:\n",pts)
    print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
    
    print('\n==== 下面使用 图像特征 SIFT 的方法未成功 ====')
    
    # imsrc = imread('yl\\bg_half.png')
    # imsch = imread('yl\\q_small.png')
    # print(result)
    print('SIFT count=', sift_count(imsch))
    print(find_sift(imsrc, imsch))
    print(find_all_sift(imsrc, imsch))
    print(find_all_template(imsrc, imsch))
    print(find_all(imsrc, imsch))


if __name__ == '__main__':
    main()