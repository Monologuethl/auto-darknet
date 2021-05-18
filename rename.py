import os

i_path = r"/home/techik/tong/code/auto-darknet/project/test/data/VOCdevkit/VOC2007/JPEGImages"
l_path = r"/home/techik/tong/code/auto-darknet/project/test/data/VOCdevkit/VOC2007/Annotations"

i_path_list = os.listdir(i_path)
l_path_list = os.listdir(l_path)

for i in range(len(i_path_list)):
    # if i_path_list[i].find("(2)") > 0:
    print(i_path_list[i])
    i_name = os.path.join(i_path, i_path_list[i])
    # new_name = os.path.join(i_path, i_path_list[i].replace("(2)", ""))
    new_name = os.path.join(i_path, i_path_list[i].replace(" ", ""))
    os.rename(i_name, new_name)

for i in range(len(l_path_list)):
    # if i_path_list[i].find("(2)") > 0:
    print(i_path_list[i])
    l_name = os.path.join(l_path, l_path_list[i])
    # new_name = os.path.join(l_path, l_path_list[i].replace("(2)", ""))
    new_name = os.path.join(l_path, l_path_list[i].replace(" ", ""))

    os.rename(l_name, new_name)
