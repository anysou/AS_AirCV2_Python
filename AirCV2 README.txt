
AirCV2: 用CV2 实现图片比较识别功能。（可部署到远程服务器上为手机提供服务，目前手机滑块处理采用此方法）

两种使用方法：

1、将此文件夹名aircv3 全复制到 python3 的 Lib/site_packages 目录下。 

   使用： import aircv2_p3 as ac
   
2、将 AnyCV2.py 复制到你要用的项目文件夹里。

   使用： form AnyCV2 import AnyCV2
   
          ac = AnyCV2()
          
3、针对手机无法安装CV2，采用提交到服务器处理。
    AnyCV2_PostServer.py 是 python的WEB服务器,默认8080端口
    sudo ufw allow 8080; sudo ufw allow 8888
    sudo ufw status
    