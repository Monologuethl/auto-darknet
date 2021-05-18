import platform
import shutil
import configparser
import argparse
import webbrowser
import sys
import os

def get_new_project(project_name, project_path, template_project):
    target_path = os.path.join(project_path, project_name)
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    source_path = os.path.abspath(template_project)
    target_path = os.path.abspath(target_path)

    print(source_path, target_path)

    if platform.system().lower() == 'windows':
        print("windows")
        os.system("xcopy  /e /c /y {} {}".format(source_path, target_path))
    elif platform.system().lower() == 'linux':
        print("linux")
        os.system("cp -r {}/. {}/".format(source_path, target_path))

    print("done !")


def prepare_train_data(src_data, project_name,project_path):
    source_path = os.path.abspath(project_path)
    xml = []
    bmp_img = []
    png_img = []
    det_path = os.path.join(source_path, project_name+r"/data/VOCdevkit/VOC2007")
    # print(det_path)
    for r, d, f in os.walk(src_data,project_name,project_path):

        for i in f:
            if "xml" in i:
                # print(r, i)
                xml.append(os.path.join(r, i))
            if "bmp" in i:
                # print(r, i)
                bmp_img.append(os.path.join(r, i))
            if "png" in i:
                # print(r, i)
                png_img.append(os.path.join(r, i))
    # print(xml)
    # print(bmp_img)

    for i in xml:
        shutil.copy(i,det_path+"/Annotations/")

    for i in bmp_img:
        shutil.copy(i,det_path+"/JPEGImages/")

    xml_path=det_path+"/Annotations/"
    xml_path_list=os.listdir(xml_path)
    img_path=det_path+"/JPEGImages/"
    img_path_list=os.listdir(img_path)


    def rename(xml_path,xml_path_list):
        for i in range(len(xml_path_list)):
            i_name = os.path.join(xml_path, xml_path_list[i])
            new_name = os.path.join(xml_path, xml_path_list[i].replace(" ", ""))
            os.rename(i_name, new_name)

    rename(xml_path,xml_path_list)
    rename(img_path,img_path_list)

    # cmd_path=os.path.join(source_path, project_name+r"/data/maketxt.py")
    os.chdir(os.path.join(source_path, project_name+r"/data"))
    os.system("python maketxt.py")
    os.system("python voc_label.py")

    print(" prepare train data done!")


def set_data(project_path,project_name,class_nums,height,width):
    root_path = os.path.abspath(project_path+"/"+project_name)
    data_file = os.path.join(root_path,'data/voc.data')
    cfg_file = os.path.join(root_path,"cfg/yolov4-tiny-3l-spp.cfg")
    print(data_file)
    print(cfg_file)

    with open(data_file,mode="w") as f:
        f.write("classes= {}".format(class_nums)+"\n")
        f.write(r"train  = {}/data/train.all.txt".format(root_path)+"\n")
        f.write(r"valid  = {}/data/2007_val.txt".format(root_path) + "\n")
        f.write(r"names = data/candou.names" + "\n")
        f.write(r"backup = backup/" + "\n")
        f.write(r"eval=voc")
        f.close()


    os.chdir(root_path)

    os.system("./darknet detector calc_anchors data/voc.data -num_of_clusters 9 -width {} -height {}".format(width, height))


def set_config(project_path, project_name, class_nums,height,width,batch,subdivisions):
    root_path = os.path.abspath(project_path + "/" + project_name)
    cfg_file = os.path.join(root_path, "cfg/yolov4-tiny-3l-spp.cfg")
    cfg_val= {}

    i = 0
    with open(cfg_file,"r") as fr:
       for line in fr:
           if len(line.replace("\n",""))>0:
               cfg_val[i]=line.replace("\n","")
               i+=1
       fr.close()

    with open(root_path+"/anchors.txt","r") as af:
        anchors=af.readline()
        af.close()
    # print(anchors)
    for k in cfg_val:
        if cfg_val[k]=="[yolo]":
            cfg_val[k-2]="filters={}".format((class_nums+5)*3)
        if "anchors" in cfg_val[k] :
            cfg_val[k]="anchors = {}".format(anchors)
        if "classes" in cfg_val[k] :
            cfg_val[k]="classes = {}".format(class_nums)
        if "height" in cfg_val[k]:
            cfg_val[k]="height = {}".format(height)
        if "width" in cfg_val[k]:
            cfg_val[k] = "width = {}".format(width)
        if "batch" in cfg_val[k].split("="):
            cfg_val[k] = "batch = {}".format(batch)
        if "subdivisions" in cfg_val[k]:
            cfg_val[k] = "subdivisions = {}".format(subdivisions)

    new_cfg_file=os.path.join(root_path,"cfg/yolov4-tiny-3l-spp_{}.cfg".format(project_name))
    with open(new_cfg_file, "w") as fr:
        for k in cfg_val:
            fr.write(cfg_val[k]+"\n")
        fr.close()

    print(new_cfg_file,"|config cfg_file done!|")


def train(project_name,project_path,resume=False,gpus=0):

    root_path=os.path.abspath(project_path+"/"+project_name)
    cfg_file=root_path+"/"+"cfg/yolov4-tiny-3l-spp_{}.cfg".format(project_name)

    if resume:
        weights=root_path+"/backup/yolov4-tiny-3l-spp_{}_last.weights".format(project_name)
    else:
        weights=root_path+"/yolov4.conv.137"
    os.chdir(root_path)
    cmd=r"./darknet detector train data/voc.data  {} -gpus {} {} -clear".format(cfg_file,gpus,weights)
    os.system(cmd)


def test(project_name,project_path,weights="",gpus=0):

    root_path = os.path.abspath(project_path + "/" + project_name)

    cfg_file = root_path + "/" + "cfg/yolov4-tiny-3l-spp_{}.cfg".format(project_name)
    weights=root_path+"/backup/yolov4-tiny-3l-spp_{}_last.weights".format(project_name)
    thresh=0.5
    test_path=root_path+"/data/train.all.txt"

    with open(test_path, mode="r") as f:
        data = f.readlines()
        f.close()
    data = [i.split("\n")[0] for i in data]

    os.chdir(root_path)
    cmd=r"./darknet detector test data/voc.data {} -dont_show -gpus {} {} -i 0 -thresh {}  <{}".format(cfg_file,gpus,weights,thresh,test_path)

    os.system(cmd)


def vis_res(project_name,project_path):
    root_path=os.path.abspath(project_path+"/{}".format(project_name))
    os.chdir(root_path)
    txt_file = root_path+"/results"
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
    Display url using the default browser. If new is 0, 
    the url is opened in the same browser window if possible. 
    If new is 1, a new browser window is opened if possible. 
    If new is 2, a new browser page (“tab”) is opened if possible. 
    If autoraise is True, the window is raised if possible 
    (note that under many window managers this will occur regardless of the setting of this variable).
    '''


if __name__ == '__main__':

    parser=argparse.ArgumentParser()
    parser.add_argument("--name", default="test",type=str)
    parser.add_argument("--src_data", default="", type=str)
    parser.add_argument("--class_nums", default=2, type=int)
    parser.add_argument("--gpus", default=0, type=int)
    parser.add_argument("--height", default=128, type=int)
    parser.add_argument("--width", default=128, type=int)
    parser.add_argument("--batch", default=400, type=int)
    parser.add_argument("--subdivisions", default=4, type=int)

    parser.add_argument("--new",action="store_true",default=False)
    parser.add_argument("--get_data", action="store_true",default=False)
    parser.add_argument("--set_data", action="store_true",default=False)
    parser.add_argument("--set_config", action="store_true",default=False)
    parser.add_argument("--train", action="store_true",default=False)
    parser.add_argument("--test", action="store_true",default=False)
    parser.add_argument("--vis", action="store_true",default=False)

    args=parser.parse_args()

    src_data=r"./dataset/dazao"

    project_name = args.name
    project_path = r"./project"
    template_project = r"./darknet"
    class_nums=args.class_nums
    height=args.height
    width=args.width
    gpus=args.gpus
    batch=args.batch
    subdivisions=args.subdivisions

    if args.new:
        get_new_project(project_name=project_name,
                        project_path=project_path,
                        template_project=template_project)
    if args.get_data:
        prepare_train_data(src_data=src_data,
                           project_name=project_name,
                           project_path=project_path)
    if args.set_data:
        set_data(project_path=project_path,
                 project_name=project_name,
                 class_nums=2,
                 height=height,
                 width=width)
    if args.set_config:
        set_config(project_path=project_path,
                   project_name=project_name,
                   class_nums=2,
                   height=height,
                   width=width,
                   batch=batch,
                   subdivisions=subdivisions)
    if args.train:
        train(project_name=project_name,project_path=project_path,gpus=gpus)
    if args.test:
        test(project_name=project_name,project_path=project_path)
    if args.vis:
        vis_res(project_name,project_path)