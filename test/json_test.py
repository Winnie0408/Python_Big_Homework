import json
import cnocr

if __name__ == '__main__':
    ocr = cnocr.CnOcr(det_model_name='naive_det',det_root='../.cnocr/det_models')
    text = ocr.ocr("../temp/pic1.png")
    print(text)
