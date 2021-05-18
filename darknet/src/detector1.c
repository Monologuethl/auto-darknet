void test_detector(char *datacfg, char *cfgfile, char *weightfile, char *filename, float thresh,
    float hier_thresh, int dont_show, int ext_output, int save_labels, char *outfile, int letter_box)
{
    list *options = read_data_cfg(datacfg);
    char *name_list = option_find_str(options, "names", "data/names.list");
    int names_size = 0;
    char **names = get_labels_custom(name_list, &names_size); //get_labels(name_list);

    image **alphabet = load_alphabet();
    network net = parse_network_cfg_custom(cfgfile, 1, 1); // set batch=1
    if (weightfile) {
        load_weights(&net, weightfile);
    }
    fuse_conv_batchnorm(net);
    calculate_binary_weights(net);
    if (net.layers[net.n - 1].classes != names_size) {
        printf(" Error: in the file %s number of names %d that isn't equal to classes=%d in the file %s \n",
            name_list, names_size, net.layers[net.n - 1].classes, cfgfile);
        if (net.layers[net.n - 1].classes > names_size) getchar();
    }
    srand(2222222);
    double time;
    char buff[256];
    char *input = buff;
    char *json_buf = NULL;
    int json_image_id = 0;
    FILE* json_file = NULL;
    if (outfile) {
        json_file = fopen(outfile, "wb");
        char *tmp = "[\n";
        fwrite(tmp, sizeof(char), strlen(tmp), json_file);
    }
    int j, i;
    float nms = .45;    // 0.4F
    if (filename) {
        strncpy(input, filename, 256);
        list *plist = get_paths(input);
        char **paths = (char **)list_to_array(plist);
        printf("Start Testing!\n");
        int m = plist->size;

        for (i = 0; i < m; ++i) {
            char *path = paths[i];
            image im = load_image(path, 0, 0, net.c);
            int letterbox = 0;
            image sized = resize_image(im, net.w, net.h);
            //image sized = letterbox_image(im, net.w, net.h); letterbox = 1;
            layer l = net.layers[net.n - 1];
            float *X = sized.data;
            double time = get_time_point();
            network_predict(net, X);
            printf("%s: Predicted in %lf milli-seconds.\n", input, ((double)get_time_point() - time) / 1000);
            printf("Try Very Hard:");
            printf("%s: Predicted in %lf milli-seconds.\n", path, ((double)get_time_point() - time) / 1000);
            int nboxes = 0;
            detection *dets = get_network_boxes(&net, im.w, im.h, thresh, hier_thresh, 0, 1, &nboxes, letterbox);
            if (nms) do_nms_sort(dets, nboxes, l.classes, nms);
            // draw_detections_v3(basecfg(input), im, dets, nboxes, thresh, names, alphabet, l.classes, ext_output);
            draw_detections_v3(im, dets, nboxes, thresh, names, alphabet, l.classes, ext_output);

            char b[2048];
            sprintf(b, "data/output/%d", i);     //   data/output/ 改成保存文件夹的路径
            save_image(im, b);
            printf("save %s successfully!\n", b);

            if (save_labels)
            {
                char labelpath[4096];
                replace_image_to_label(input, labelpath);
                FILE* fw = fopen(labelpath, "wb");
                int i;
                for (i = 0; i < nboxes; ++i) {
                    char buff[1024];
                    int class_id = -1;
                    float prob = 0;
                    for (j = 0; j < l.classes; ++j) {
                        if (dets[i].prob[j] > thresh && dets[i].prob[j] > prob) {
                            prob = dets[i].prob[j];
                            class_id = j;
                        }
                    }
                    if (class_id >= 0) {
                        sprintf(buff, "%d %2.4f %2.4f %2.4f %2.4f\n", class_id, dets[i].bbox.x, dets[i].bbox.y, dets[i].bbox.w, dets[i].bbox.h);
                        fwrite(buff, sizeof(char), strlen(buff), fw);
                    }
                }
                fclose(fw);
            }

            free_detections(dets, nboxes);
            free_image(im);
            free_image(sized);
        }
    }
    printf("All Done!\n");
    exit(0);
    free_ptrs(names, net.layers[net.n - 1].classes);
    free_list_contents_kvp(options);
    free_list(options);

    const int nsize = 8;
    for (j = 0; j < nsize; ++j) {
        for (i = 32; i < 127; ++i) {
            free_image(alphabet[j][i]);
        }
        free(alphabet[j]);
    }
    free(alphabet);
    free_network(net);
    printf("All Done!\n");
}
