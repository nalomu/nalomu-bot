# Nalomu Bot

这是一个娱乐性质的QQ bot，本身只是一个与cq-http-api交互的web服务器，需要和[coolq](https://cqp.cc/)和[CoolQ HTTP API](https://cqhttp.cc/)配合才能使用  
基于 [nonebot](https://github.com/richardchien/nonebot) 开发  
需要 Python 3.7+ 及 CoolQ HTTP API 插件 v4.14+

## 安装

克隆项目到本地  
`git clone https://github.com/nalomu/nalomu-bot.git`

## 使用

安装依赖  
`pip install -r requirements.txt`  

复制配置文件并按需修改  
`cp ./nalomu/conf/config.example.toml ./nalomu/conf/config.toml`

查看帮助  
`./bot.py -h`  

直接运行  
`./bot.py --run`    

作为守护进程运行(linux)  
`./bot.py --start`  

停止运行(linux)  
`./bot.py --stop`  

重启(linux)  
`./bot.py -r`  

## 第三方依赖
[wkhtmltoimage](https://wkhtmltopdf.org/downloads.html)  
安装之后需要在配置中填上路径

## 目前的功能

打招呼  
对话（可以通过qq设置回答）  
bilibili直播提醒  
点歌（需要coolq pro）  
其他  
每日提醒  
备忘录  
翻译  
个人相关功能  
整点报时  
萌娘百科  
setu  
天气(背景图片需要创建./nalomu/data/images文件夹并添加一张weather-bg.jpg)  
反馈  
摇号  
搜图  

## 贡献

如果你在使用过程中发现任何问题或有什么建议，可以 [提交 issue](https://github.com/nalomu/nalomu-bot/issues/new) 或自行 fork 修改后提交 pull request。
