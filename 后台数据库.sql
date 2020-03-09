-- 后台： MYSQL

/*
#数据库存在就删除
*/
drop database if exists bjk;  
create DATABASE bjk;
use bjk; 

/*
#utf-8编码4个字节的字符
*/
SET NAMES utf8mb4;

/*
取消外键约束
*/
SET FOREIGN_KEY_CHECKS = 0;

/*
数据库名：anysou_huobi

用户信息表：TB_USER
用户ID                  USER_ID        smallint      NOT NULL AUTO_INCREMENT,  -- 自增   主键
用户身份手机号码        USER_PHONE     char(11)      NOT NULL unique,  -- 唯一性约束 唯一，也作为推荐码用,也作为登陆用户名
用户密码                USER_PASS      char(32) 
用户名字                USER_NAME      varchar(8)     
推荐手机号码            SALE_PHONE     char(11)
推荐名字                SALE_NAME      varchar(8) 
注册时间                REG_TIME       timestamp     CURRENT_TIMESTAMP 
试用截止时间            TEST_TIME      timestamp
用户机身码              PC_CODE        varchar(100)
是否写日志              LOG_INFO       char(1) （0不记录，1全记录，2只记录亏损）
是否显示下注过程        GAME_INFO      char(1)
是否为测试用户          IS_TEST        char(1)
是否有效                IS_OK          char(1)
是否固定IP              IS_IP          char(1)
允许同时开几个          MAX_W          tinyint
*/
DROP TABLE IF EXISTS `TB_USER`;
CREATE TABLE `TB_USER` (
  `USER_ID` smallint(6) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `USER_PHONE` char(11) NOT NULL COMMENT '用户名或手机号码',
  `USER_PASS` char(32) NOT NULL DEFAULT '123456' COMMENT '用户密码',
  `USER_NAME` varchar(8) NOT NULL COMMENT '用户名字或昵称',
  `SALE_PHONE` varchar(11) NOT NULL COMMENT '推荐手机号码',
  `SALE_NAME` varchar(8) NOT NULL COMMENT '推荐名字',
  `REG_TIME` timestamp NOT NULL DEFAULT NOW() COMMENT '注册时间',  
  `TEST_TIME` timestamp NOT NULL DEFAULT NOW() COMMENT '试用截止时间',
  `PC_CODE` varchar(100) NOT NULL DEFAULT '' COMMENT '用户机身码',
  `LOG_INFO` char(1) NOT NULL DEFAULT '0' COMMENT '是否写日志（0不记录，1全记录，2只记录亏损）',
  `GAME_INFO` char(1) NOT NULL DEFAULT '1' COMMENT '是否显示下注过程',
  `IS_TEST` char(1) NOT NULL DEFAULT '1' COMMENT '是否为测试用户',
  `IS_OK` char(1) NOT NULL DEFAULT '1' COMMENT '是否有效',
  `IS_PC` char(1) NOT NULL DEFAULT '1' COMMENT '是否固定PC',
  `MAX_W` tinyint(2) NOT NULL  DEFAULT 10 COMMENT '允许同时开几个',
  
  PRIMARY KEY (`USER_ID`),
  UNIQUE KEY `INDEX_PHONE` (`USER_PHONE`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户信息表';

/*
批量插入表
*/
use bjk; 
BEGIN;
INSERT INTO `TB_USER` VALUES (1, 'istest', 'e10adc3949ba59abbe56e057f20f883e', 'test', 'istest', 'istest', NOW(), NOW(),'','1','1','1','1','0','10');
INSERT INTO `TB_USER` VALUES (2, 'ismyhd', 'e10adc3949ba59abbe56e057f20f883e', 'test', 'ismy', 'istest',NOW(),NOW(),'','1','0','1','1','0','10');
COMMIT;

/*
用户登陆信息表 TB_LOGIN

登陆ID                  L_ID           int
用户身份手机号码        USER_PHONE     char(11)      NOT NULL unique,  -- 唯一性约束 唯一，也作为推荐码用,也作为登陆用户名
登陆时间                L_TIME         timestamp
用户IP地址              USER_IP        varchar(20)
*/

DROP TABLE IF EXISTS `TB_LOGIN`;
CREATE TABLE `TB_LOGIN` (
  `L_ID` int(11) NOT NULL AUTO_INCREMENT COMMENT '登陆ID',
  `USER_PHONE` char(11) NOT NULL COMMENT '用户身份手机号码',
  `L_TIME` timestamp NOT NULL DEFAULT NOW() COMMENT '登陆时间', 
  `USER_IP` varchar(20) NOT NULL COMMENT '用户IP地址',
  PRIMARY KEY (`L_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户登陆信息表';


/*
用户交易信息表 TB_INFO
*/

DROP TABLE IF EXISTS `TB_INFO`;
CREATE TABLE `TB_INFO` (
  `T_ID` int(11) NOT NULL AUTO_INCREMENT COMMENT '交易ID',
  `USER_PHONE` char(11) NOT NULL COMMENT '用户身份手机号码',
  `T_TIME` timestamp NOT NULL DEFAULT NOW() COMMENT '交易时间',
  `T_NO` varchar(20) NOT NULL COMMENT '交易备注',
  `T_STAKE` varchar(2) NOT NULL COMMENT '下注额',
  `T_SEAT` char(1) NOT NULL COMMENT '台数',
  `T_YK` float NOT NULL COMMENT '盈亏额',
  `T_LS` float NOT NULL COMMENT '流水',
  `T_S` float NOT NULL COMMENT '初始资金',
  `T_E` float NOT NULL COMMENT '结束资金',
  `T_MODE` char(1) NOT NULL COMMENT '结束方式Y止盈K止损S流水L人工',
  `T_OVER` char(1) NOT NULL COMMENT '是否结算',
  PRIMARY KEY (`T_ID`),
  KEY `INDEX_PHONE` (`USER_PHONE`),
  KEY `INDEX_TIME` (`T_TIME`)  
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='用户成交信息表';
