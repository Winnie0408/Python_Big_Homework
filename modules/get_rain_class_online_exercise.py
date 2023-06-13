import requests
import io
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from cnocr import CnOcr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains


# 使用cnocr进行雨课堂PPT题目识别
def get_pic(url):
    response = requests.get(url)
    return response.content


def ocr_from_pic(image_data):
    ocr = CnOcr(det_model_name='db_resnet34', det_model_backend='pytorch', rec_model_name='densenet_lite_136-fc',
                rec_model_backend='onnx')
    text = ocr.ocr(image_data)
    return text


def get():
    print("正在启动浏览器,请稍等……")

    options = webdriver.EdgeOptions()
    options.use_chromium = True
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-new-tab")

    driver = webdriver.Edge(service=Service(EdgeChromiumDriverManager().install()), options=options)
    print("浏览器启动成功")
    driver.maximize_window()
    driver.get("https://www.yuketang.cn/")
    wait = WebDriverWait(driver, 20, 0.5)

    if os.path.exists("RainClass_result.csv"):
        os.remove("RainClass_result.csv")

    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div[2]/a[3]")))
    driver.find_element(By.XPATH, "/html/body/nav/div[2]/a[3]").click()
    print("请登录雨课堂账号")
    driver.switch_to.window(driver.window_handles[-1])
    show_noti(driver, "请登录雨课堂账号")
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")))
    driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")
    print("登录成功")

    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[1]/div/div/div/div[3]").click()

    show_noti(driver, "请选择您要导出的课程")

    # size = len(driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[3]/div[2]/div").find_elements(By.XPATH, "./*"))
    # for i in range(1, size):
    #     driver.execute_script("window.scrollBy(0,100)")


def show_noti(driver, noti):
    driver.execute_script(f"""
        var div = document.createElement('div');
        div.innerHTML = '来自小助手的提醒：{noti}';
        div.style.position = 'fixed';
        div.style.top = '0';
        div.style.left = '50%';
        div.style.transform = 'translate(-50%)';
        div.style.zIndex = 9999;
        div.style.fontSize = '26px';
        div.style.fontFamily = '微软雅黑';
        div.style.color = 'red';
        document.body.appendChild(div);
            """)


def delete_noti(driver):
    driver.execute_script("var div = document.querySelector('div');div.parentNode.removeChild(div);")


def hide_noti(driver):
    driver.execute_script("var div = document.querySelector('div');div.style.display = 'none';")
