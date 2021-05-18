# coding:utf-8

import webbrowser
import sys
import os

# 准备相关变量

txt_file = "./results"
txt_file_list = os.listdir(txt_file)
data = [i for i in txt_file_list]

res_list = []
for j, i in enumerate(data):
    new_name = os.path.join("./results", i)
    if j % 4 == 0:
        res_list.append("<img src=" + new_name + "><br>")
    else:
        res_list.append("<img src=" + new_name + ">")

img_str = ""
for i in res_list:
    img_str += i

# 命名生成的html
GEN_HTML = "test_result.html"
# 打开文件，准备写入
f = open(GEN_HTML, 'w')

message = """
<!DOCTYPE html>
<html>
<head>    
    <link rel="stylesheet" type="text/css" href="task001.css">
    <meta charset="utf-8">
    <title>test</title>
    <style type="text/css">
    *{margin: 0; padding: 0;}
    .clearfix:after {
          clear: both;
          content: ".";
          display: block;
          height: 0;
          visibility: hidden;
        }
      .wrap {
        /* 可无需设置高度，靠图片高度 或者 文字的上下padding撑开高度 */
            border: 1px solid;
            width: 600px;
            text-align: center; margin: 0 auto;
        }
        .wrap span{
            display: inline-block;
            vertical-align: middle;
            padding: 20px 0; /* 撑开高度 */
        }
        .wrap img{
            width: auto;
            height: auto;
            vertical-align: middle;
        }
    </style>
</head>
<body>    
    <div class="wrap">
        %s
    </div>
</body>
</html>""" % (img_str)

# 写入文件
f.write(message)
# 关闭文件
f.close()

# 运行完自动在网页中显示
webbrowser.open(GEN_HTML, new=0)
'''
webbrowser.open(url, new=0, autoraise=True) 
Display url using the default browser. If new is 0, the url is opened in the same browser window if possible. If new is 1, a new browser window is opened if possible. If new is 2, a new browser page (“tab”) is opened if possible. If autoraise is True, the window is raised if possible (note that under many window managers this will occur regardless of the setting of this variable).
'''
