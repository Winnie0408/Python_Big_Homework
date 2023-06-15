import requests
from urllib import request
import io
import os
import re
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from cnocr import CnOcr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from PIL import Image, ImageDraw


# 获取题目图片
def get_pic(url, name):
    if os.path.exists("./temp/" + name + ".png"):
        os.remove("./temp/" + name + ".png")
    request.urlretrieve(url, "./temp/" + name + ".png")


# 优化图片,去除干扰
def optimize_pic(name):
    image = Image.open("./temp/" + name + ".png")

    # # 在选项处添加一个白色矩形
    # draw = ImageDraw.Draw(image)
    # x, y = 80, 145
    # width, height = 50, 185

    # 在左上角添加一个白色矩形
    draw = ImageDraw.Draw(image)
    x, y = 570, 30
    width, height = 70, 20

    draw.rectangle((x, y, x + width, y + height), fill='white')
    image.save("./temp/" + name + ".png")


# 使用cnocr识别图片中的文字
def ocr_from_pic(name):
    # ocr = CnOcr(det_model_name='db_resnet34', det_model_backend='pytorch', rec_model_name='densenet_lite_136-fc', rec_model_backend='onnx')
    ocr = CnOcr(det_model_name='naive_det',det_root='../.cnocr/det_models')
    text = ocr.ocr("./temp/" + name + ".png")
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

    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div[2]/a[3]")))  # 等待登录按钮出现
    driver.add_cookie(
        {'name': 'sessionid',
         'value': '',
         'domain': 'www.yuketang.cn'})

    if os.path.exists("RainClass_Online_result.csv"):
        os.remove("RainClass_Online_result.csv")

    driver.find_element(By.XPATH, "/html/body/nav/div[2]/a[3]").click()  # 点击登录按钮
    print("请登录雨课堂账号")
    driver.switch_to.window(driver.window_handles[-1])
    show_noti(driver, "请登录雨课堂账号")
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")))  # 等待登录成功
    # driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")
    print("登录成功")
    delete_noti(driver)

    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[1]/div/div/div/div[3]").click()  # 点击我听的课

    show_noti(driver, "请选择您要导出的课程，<br>选择好后请回到Python确认")

    input("输入Y/y后回车以继续")

    delete_noti(driver)
    print("正在获取课程列表……")
    name = driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[1]/h1[1]/div[1]")  # 获取课程名称
    teacher = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[1]/div/span[1]/div[2]/div[1]").text  # 获取老师名称
    list = driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]")  # 获取课程日志列表

    print("您当前选择的课程为：" + teacher + "老师的" + name.text + "，该课程共有" + str(
        len(list.find_elements(By.XPATH, "./*"))) + "个日志")

    for i in range(1, len(list.find_elements(By.XPATH, "./*")) + 1):
        type = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]").get_attribute("innerHTML")  # 获取日志类型
        type = type.split("#icon-")[1].split("\"")[0]
        match type:
            case "ketang":
                type = "课堂"
            case "kaoshi":
                type = "考试"
            case "taolun":
                type = "讨论"
            case "zuoye":
                type = "作业"
            case "piliang":
                type = "批量"
            case _:
                print("其他类型日志，跳过")
                continue

        try:
            name = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]/div[2]/div[2]/section/div[1]/div/h2").text
        except NoSuchElementException:
            name = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]/div/div[2]/section/div[1]/div/h2").text

        print("进入第" + str(i) + "个" + type + "日志：" + name)
        match type:
            case "课堂":
                # 进入课堂日志
                driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/section[" + str(i) + "]/div[2]/div[2]/section[1]").click()
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[1]/div[2]/div/div/div/div[2]/div")))

                # if driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[1]/div[2]/div/div/div").get_attribute("innerHTML").__contains__("本次授课无习题"):
                #     print("\t该日志无习题，跳过")
                #     driver.back()
                #     wait.until(EC.presence_of_element_located(
                #         (By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]")))
                #     continue
                # else:
                try:
                    WebDriverWait(driver, 1, 0.3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div/div/div[2]/div/div[1]/div/div")))  # 等待习题加载
                    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div/div/div[2]/div/div[1]/div/div/div[1]").click()  # 点击第一道习题，进入习题列表
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]")))  # 等待习题列表加载
                    num = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[1]/div/div[1]/div/div/div/div[3]/span/span").text.split("(")[1].split(")")[0]  # 获取习题数量
                    print("\t该日志有" + str(num) + "道习题，正在获取……")
                    write_title_to_csv(type + " " + name)

                    for j in range(1, int(num) + 1):
                        print("\t\t获取第" + str(j) + "道，共" + str(num) + "道")
                        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[1]/div[2]/div[1]/div[" + str(j) + "]").click()  # 点击第j道习题
                        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[3]/div/div/div[1]/div/div/img")))  # 等待习题大图加载
                        img_src = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[3]/div/div/div[" + str(j) + "]/div/div/img").get_attribute("src")  # 获取习题大图链接
                        get_pic(img_src, "pic" + str(j))
                        optimize_pic("pic" + str(j))
                        result = ocr_from_pic("pic" + str(j))
                        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div/div/div[1]/div")))
                        answer = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div[2]/div/div[1]/div/div[2]/div/div[2]/div[4]/div[2]/div[2]/div[1]/div/div/div[1]/div/div[1]/div").get_attribute("innerText")
                        write_exercise_to_csv(json.loads(json.dumps(result)), answer, j)

                    driver.back()

                except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
                    print("\t该日志无习题，跳过")
                    driver.back()
                    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]")))  # 等待日志列表加载
                    continue


def show_noti(driver, noti):
    driver.execute_script(f"""
        var div = document.createElement('div');
        div.setAttribute('id', 'HWinZnieJ');
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
    driver.execute_script("var div = document.querySelector('#HWinZnieJ');div.remove();")


def hide_noti(driver):
    driver.execute_script("var div = document.querySelector('#HWinZnieJ');div.style.display = 'none';")


def write_exercise_to_csv(exercise, answer, index):
    type = exercise[0]['text'].split("题")[0]
    optD = exercise[len(exercise) - 1]['text'][1:]
    exercise.pop()
    optC = exercise[len(exercise) - 1]['text'][1:]
    exercise.pop()
    optB = exercise[len(exercise) - 1]['text'][1:]
    exercise.pop()
    optA = exercise[len(exercise) - 1]['text'][1:]
    exercise.pop()

    exercise.pop(0)

    title = ""
    for i in range(len(exercise)):
        title += exercise[i]['text']
    title = title.replace("口", "", 1)
    if answer == "评论":
        answer = "该题未公布正确答案"
    try:
        with open('RainClass_Online_result.csv', 'a', encoding='gbk', errors='ignore') as writer:
            writer.write("(" + type + ") " + str(index) + "." + title + ",A." + optA + ",B." + optB + ",C." + optC + ",D." + optD + ",," + answer.replace("\n", "").replace(" ", ""))
            writer.write("\n")
    except IOError as e:
        print(e)


def write_title_to_csv(title):
    try:
        with open('RainClass_Online_result.csv', 'a', encoding='gbk', errors='ignore') as writer:
            writer.write(title + "\n")
    except IOError as e:
        print(e)
