import aircv2_p3 as ac
import platform                     # 判断操作系统 str(platform.system()) = 'Windows' 'Linux'


def main():
    sysname = platform.system()
    
    while True:
        mode = input("\n请选择结果：1、图片查找和显示；2、查找红包；3、SIFT查找红包；4、拖动滑块；") 
        try: 
            mode = int(mode)
        except Exception as e:
            mode = 0        
        if mode<1 or mode>4:
            mode = input("\n请选择结果：1、图片查找和显示；2、查找红包；3、SIFT查找红包；4、拖动滑块；") 
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
                print("\n所有结果中心位置:\n",pts)
                print("\n所有结果中心位置排序结果：\n",sorted(pts, key=lambda p: p[0]))
            elif(mode==2):  
                if(sysname=='Windows'):
                    imsrc = ac.imread('testdata\\temp.png')
                    imsch = ac.imread('testdata\\HB.png')  
                else:
                    imsrc = ac.imread('testdata/temp.png')
                    imsch = ac.imread('testdata/HB.png')
                
                print('\n=====在一个图片中查找另一个图片的所有结果 find_all ====')
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

if __name__ == '__main__':
    main()