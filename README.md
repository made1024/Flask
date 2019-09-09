# Flask

## version 1.0

1. 实现程序初始化
2. 实现程序的路由和视图函数
3. 实现程序的启动
4. 实现动态路由的flask程序

## version 1.1

1. 集成bootstrap模板
2. 实现用户错误页面定义
3. 添加静态文件
4. 本地化日期和时间

## version 1.2

1. 实现表单模板
2. 实现重定向和用户会话
3. 实现flash消息提醒

## version 1.3

1. 实现flask与数据库的对接
+  配置数据库连接信息
+  定义数据表模型
+  建立数据库表间关系
+  视图函数中实现数据库操作

2. 集成命令行运行及执行其他程序
3. 实现数据库迁移,升级、回退

## version 1.4

1. 实现邮件功能

## version 1.5

1. 实现结构化管理
+  配置类结构化
+  结构化模板、静态文件、视图函数等，生成app包
+  生成蓝图，并注册到app程序中
+  修改视图函数及异常处理函数
+  增加启动脚本，实现命令地启动及数据库升级、回退操作
+  增加单元测试

## version 2.0

1. 新增用户密码功能
+  密码散列
+  增加密码散列存储的单元测试

2. 创建用户认证蓝图
3. 登录用户认证

## version 2.1

1. 新增用户注册功能
2. 新增用户确认功能
3. 修改用户密码功能
4. 重置用户密码功能
5. 修改用户邮箱地址功能

## version 2.2
1. 新增用户角色管理
+   用户角色管理

    |角色类型|操作权限|
    |:----|:----|
    |管理员|关注、评论、写作、审查、管理|
    |审查员|关注、评论、写作、审查|
    |普通用户|关注、评论、写作|

+   用户角色权限验证
+   单元测试

## version 2.3
1. 新增用户资料浏览、编辑功能
+   普通用户浏览、编辑
+   管理员用户浏览、编辑

## version 2.4
1. 新增用户博客文章浏览、编辑功能