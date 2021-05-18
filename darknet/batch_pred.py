import os
import sys
import shutil

import webbrowser
arg = sys.argv

txt_file = arg[1]
with open(txt_file, mode="r") as f:
    data = f.readlines()
    f.close()
data = [i.split("\n")[0] for i in data]
# print(data)

cmd = r"./darkneta/binglang_big.data cfg/yolov4-tiny-binglang-big-test.cfg -dont_show -gpus 1 backup/big/yolov4-tiny-binglang-big_last.weights -i 0 -thresh 0.5 </home/techik/Project/binglang_2021_03_29/data/VOCdevkit/VOC2007/ImageSets/Main/2007_train.txt"
i = 0



while True:
    if i < len(data):
        new_name = "results/{}.jpg".format(data[i].split("/")[-1][:-4])
        try:
            shutil.move("predictions.jpg", new_name)

            print(i, end="\r")
            i += 1
        except Exception as e:
            pass

