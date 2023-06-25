from urllib import request
import time
import datetime
import pytz
import os
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, JavascriptException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from cnocr import CnOcr
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys
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
    ocr = CnOcr(det_model_name='naive_det', det_root='../.cnocr/det_models')
    text = ocr.ocr("./temp/" + name + ".png")
    return text


def show_noti(driver, noti):
    '''执行JavaScript代码，显示自定义内容的通知'''
    delete_noti(driver)
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
    '''执行JavaScript代码，删除通知'''
    try:
        driver.execute_script("var div = document.querySelector('#HWinZnieJ');div.remove();")
    except JavascriptException:
        pass


def write_exercise_to_csv(exercise, answer, index):
    '''将题目内容写入CSV文件，类型1'''
    type = exercise[0]['text'].split("题")[0]  # 题目类型
    optD = exercise[len(exercise) - 1]['text'][1:]  # 选项D
    exercise.pop()  # 删除选项D
    optC = exercise[len(exercise) - 1]['text'][1:]  # 选项C
    exercise.pop()  # 删除选项C
    optB = exercise[len(exercise) - 1]['text'][1:]  # 选项B
    exercise.pop()  # 删除选项B
    optA = exercise[len(exercise) - 1]['text'][1:]  # 选项A
    exercise.pop()  # 删除选项A

    exercise.pop(0)  # 删除题目类型

    title = ""
    # 拼接题目
    for i in range(len(exercise)):
        title += exercise[i]['text']
    title = title.replace("口", "", 1)  # 删除题目开头因干扰而识别出来的的“口”
    if answer == "评论":
        answer = "该题未公布正确答案"
    try:
        # 写入CSV文件
        with open('RainClass_Online_result.csv', 'a', encoding='gbk', errors='ignore') as writer:
            writer.write("(" + type + ") " + str(index) + "." + title + ",A." + optA + ",B." + optB + ",C." + optC + ",D." + optD + ",," + answer.replace("\n", "").replace(" ", ""))
            writer.write("\n")
    except IOError as e:
        print(e)


def write_title_to_csv(title):
    '''将题目标题写入CSV文件'''
    try:
        with open('RainClass_Online_result.csv', 'a', encoding='gbk', errors='ignore') as writer:
            writer.write("\n" + title + "\n")
    except IOError as e:
        print(e)


def write_exercise_to_csv1(type, question, opt, answer, index):
    '''将题目内容写入CSV文件，类型2'''
    try:
        with open('RainClass_Online_result.csv', 'a', encoding='gbk', errors='ignore') as writer:
            if type == "判断":
                # (题目类型)题号.题目正文，正确,错误,,,,答案
                writer.write("(" + type + ") " + str(index) + "." + question + ",正确,错误,,,," + answer.replace(",", "").split(" ")[0])
            else:
                # (题目类型)题号.题目正文，A.选项A,B.选项B,C.选项C,D.选项D,,,答案
                writer.write("(" + type + ") " + str(index) + "." + question)
                for i in range(0, len(opt)):
                    match i:
                        case 0:
                            writer.write(",A." + opt[i])
                        case 1:
                            writer.write(",B." + opt[i])
                        case 2:
                            writer.write(",C." + opt[i])
                        case 3:
                            writer.write(",D." + opt[i])
                writer.write(",," + answer.replace(",", "").split(" ")[0])
            writer.write("\n")  # 换行
    except IOError as e:
        print(e)


def read_config():
    '''读取配置文件'''
    try:
        with open('./config.cfg', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return ""


def save_config(content):
    '''保存配置文件'''
    with open('./config.cfg', 'a', encoding='utf-8') as file:
        file.write(content)


def delete_line_with_keyword(file_path, keyword):
    '''删除指定文件中包含关键词的行'''
    try:
        # 打开txt文件，并读取其中的内容
        with open(file_path, 'r') as f:
            content = f.readlines()

        # 遍历每一行，判断该行是否包含关键词
        new_content = []
        for line in content:
            if keyword not in line:
                new_content.append(line)

        # 将删除后的内容重新写入txt文件中
        with open(file_path, 'w') as f:
            f.writelines(new_content)

    except FileNotFoundError:
        pass


def get():
    '''获取题目'''
    if os.path.exists("RainClass_Online_result.csv"):
        del_file = input("\n需要删除上次生成结果文件RainClass_Online_result.csv才能继续\n删除吗？\nY/y：删除\n其他字符：退出\n请选择：").lower()
        if del_file == "y":
            os.remove("RainClass_Online_result.csv")
            print("已删除")
        else:
            print("您已取消练习题导出")
            return

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
    wait = WebDriverWait(driver, 120, 0.5)

    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/nav/div[2]/a[3]")))  # 等待登录按钮出现

    cookie_valid = False
    cookie_expired = False
    try:
        cookie = json.loads(read_config().split("RainClass#")[1])
        if cookie != "":
            if int(cookie['expiry']) < int(time.time()):
                delete_noti(driver)
                cookie_expired = True
            else:
                driver.add_cookie(cookie)
                cookie_valid = True
    except IndexError:
        print("未保存Cookie")

    driver.find_element(By.XPATH, "/html/body/nav/div[2]/a[3]").click()  # 点击登录按钮
    driver.switch_to.window(driver.window_handles[-1])

    if cookie_expired:
        print("保存的Cookie已过期，请重新进行登录操作")
        show_noti(driver, "保存的Cookie已过期，请重新进行登录操作")
    elif not cookie_valid:
        print("请登录雨课堂账号")
        show_noti(driver, "请登录雨课堂账号")

    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")))  # 等待登录成功
    # driver.find_element(By.XPATH, "/html/body/div[4]/div[1]/div[1]/div/span/div[1]/p[1]")
    if not cookie_expired and cookie_valid:
        print("使用Cookie登录成功")
    else:
        print("普通登录成功")

    if not cookie_valid:
        delete_line_with_keyword("./config.cfg", "RainClass#")
        save_config("\nRainClass#" + json.dumps(driver.get_cookie('sessionid')))
        cookie_timestamp = driver.get_cookie('sessionid')['expiry']
        cookie_timestamp = datetime.datetime.utcfromtimestamp(cookie_timestamp).replace(tzinfo=pytz.utc)
        cookie_timestamp = cookie_timestamp.astimezone(pytz.timezone('Asia/Shanghai'))
        print("Cookie已保存，" + cookie_timestamp.strftime("%Y-%m-%d") + "前可自动登录")
    delete_noti(driver)

    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[1]/div/div/div/div[3]").click()  # 点击我听的课

    show_noti(driver, "请选择您要导出的课程，<br>选择好后请回到Python确认")

    if input("输入Y/y后回车以继续").lower() != 'y':
        print("您已取消练习题导出")
        return

    delete_noti(driver)
    print("正在获取课程列表……")

    roll_to_bottom(driver)  # 主动滚动到底部，加载所有课程

    class_name = driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[1]/h1[1]/div[1]").text  # 获取课程名称
    teacher = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[1]/div/span[1]/div[2]/div[1]").text  # 获取老师名称
    list = len(driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]").find_elements(By.XPATH, "./*"))  # 获取课程日志列表
    print("您当前选择的课程为：" + teacher + "老师的" + class_name + "，该课程共有" + str(list) + "个日志")

    while True:
        try:
            progress = int(input("请选择：\n1：从头开始;\n任意正整数：从给定的位置开始\n其他字符：退出"))
            if progress % 1 != 0:
                print("请输入整数")
            else:
                break
        except ValueError:
            print("您已取消练习题导出")

    traversal_list(driver, wait, "", teacher, class_name, list, progress)

    print(teacher + "老师的 " + class_name + " 所有题目获取完毕\n")


def traversal_list(driver, wait, recursion, teacher, class_name, list, progress):
    '''递归遍历日志列表'''
    for i in range(int(progress), int(list) + 1):
        time.sleep(0.5)
        if recursion == "":
            type = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]").get_attribute("innerHTML")  # 获取日志类型
            xpath = "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div"
        else:
            type = driver.find_element(By.XPATH, recursion + "/section[" + str(i) + "]").get_attribute("innerHTML")  # 获取日志类型
            xpath = recursion
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
                if recursion == "":
                    print("\n第" + str(i) + "个日志类型为" + type + "，不包含题目，跳过")
                else:
                    print("\n\t\t第" + str(i) + "个子日志类型为" + type + "，不包含题目，跳过")
                continue

        try:
            if recursion == "":
                name = driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/div[2]/div[2]/section/div[1]/div/h2").text
                path = "div[2]/div[2]"
            else:
                name = driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/div[1]/div/h2").text
                path = "div[1]"

        except NoSuchElementException:
            if recursion == "":
                name = driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/div/div[2]/section/div[1]/div/h2").text
                path = "div/div[2]"
            else:
                name = driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/div[1]/div/h2").text
                path = "div[1]"

        if recursion == "":
            print("\n进入第" + str(i) + "个" + type + "日志：" + name)
        else:
            print("\n\t\t进入第" + str(i) + "个" + type + "子日志：" + name)

        if type != "批量":
            # time.sleep(1)
            # 进入日志
            target = driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/" + path)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
            time.sleep(0.5)
            driver.find_element(By.XPATH, xpath + "/section[" + str(i) + "]/" + path).click()

        match type:
            case "课堂":
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[1]/div[2]/div/div/div/div[2]/div")))
                if recursion != "":
                    print("\t\t", end="")
                extract_exercise_from_classroom(driver, wait, name, type)
                if recursion == "":
                    print("第" + str(i) + "个" + type + "日志：" + name + "获取完毕")

            case "考试":
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div/div")))  # 等待考试数据加载
                if recursion != "":
                    print("\t\t", end="")
                extract_exercise_from_examination(driver, wait, name, type)
                if recursion == "":
                    print("第" + str(i) + "个" + type + "日志：" + name + "获取完毕")

            case "讨论":
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div[1]/div/section[2]")))  # 等待讨论加载
                if recursion != "":
                    print("\t\t", end="")
                extract_exercise_from_discussion(driver, name, type)
                if recursion == "":
                    print("第" + str(i) + "个" + type + "日志：" + name + "获取完毕")

            case "作业":
                wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div")))  # 等待作业加载
                if recursion != "":
                    print("\t\t", end="")
                extract_exercise_from_homework(driver, wait, name, type)
                if recursion == "":
                    print("第" + str(i) + "个" + type + "日志：" + name + "获取完毕")

            case "批量":
                # 滚动到指定元素位置，避免被遮挡而报错
                target = driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/section[" + str(i) + "]/" + path + "/section[1]/div[1]/div/div/span/span")
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", target)
                time.sleep(0.5)
                # 展开批量日志
                driver.find_element(By.XPATH, "/html[1]/body[1]/div[4]/div[2]/div[1]/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div[1]/section[" + str(i) + "]/" + path + "/section[1]/div[1]/div/div/span/span").click()
                time.sleep(1)
                num = len(driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]/" + path + "/section[2]/div/div").find_elements(By.XPATH, "./section"))  # 获取批量日志中包含的日志数量
                print("\t该批量日志有" + str(num) + "个子日志，正在获取……")

                # 递归获取批量日志中的子日志
                traversal_list(driver, wait, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div/section[" + str(i) + "]/" + path + "/section[2]/div/div", teacher, class_name, num, 1)
                if recursion == "":
                    print("第" + str(i) + "个" + type + "日志：" + name + "获取完毕")
                driver.refresh()
                time.sleep(1)
                roll_to_bottom(driver)


def extract_exercise_from_classroom(driver, wait, name, type):
    '''从课堂日志中提取习题'''
    try:
        WebDriverWait(driver, 1, 0.3).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/section/main/div[2]/div/div/div[2]/div/div[1]/div/div")))  # 等待习题加载
        driver.refresh()
        time.sleep(1.5)
        # roll_to_bottom(driver)
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

        print("\t" + type + "日志:" + name + "习题获取完毕")
        driver.back()

    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        print("\t该日志无习题，跳过")
        driver.back()
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[1]/div[1]")))  # 等待日志列表加载


def extract_exercise_from_examination(driver, wait, name, type):
    '''从考试日志中提取习题'''
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div/div/div[4]/a")))
    driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div/div/div[4]/a").click()  # 点击查看试卷
    driver.switch_to.window(driver.window_handles[-1])  # 切换到新窗口
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div")))  # 等待试卷加载
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[1]")))  # 等待试卷加载
    time.sleep(1.5)

    write_title_to_csv(type + " " + name)

    # 获取题目数量
    num = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[1]/div/div[1]/div[2]").text.split("/")[1].split("题")[0]
    print("\t该日志有" + str(num) + "道习题，正在获取……")

    for j in range(1, int(num) + 1):
        print("\t\t获取第" + str(j) + "道，共" + str(num) + "道")
        typeEx = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[1]").text.split(".")[1].split("题")[0]  # 获取题目类型
        question = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[2]/h4").text  # 获取题目

        opt = []
        for k in range(1, 5):
            if typeEx == "判断":
                break
            opt.append(driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[2]/ul/li[" + str(k) + "]/label/span[2]/span[2]").text)  # 获取选项

        answer = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[3]/div[2]/div/span[2]").text  # 获取答案
        # driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[3]/div[3]/div[1]").click()  # 点击查看解析
        # explain = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[1]/div[2]/div/div[2]/div/div/div/div/div/div[" + str(j) + "]/div/div[3]/div[3]/div[2]").get_attribute("innerText")  # 获取解析
        # if explain == "None":
        #     explain = "本题暂无解析"

        write_exercise_to_csv1(typeEx, question, opt, answer, j)

    print("\t" + type + "日志:" + name + "习题获取完毕")
    driver.close()
    driver.switch_to.window(driver.window_handles[-1])  # 切换回原窗口
    driver.back()


def extract_exercise_from_discussion(driver, name, type):
    '''从讨论日志中提取习题'''
    time.sleep(0.5)
    # title = driver.find_element(By.XPATH,"/html/body/div[4]/div[2]/div/div[2]/div[1]/div/section[1]/div[1]/span").text
    text = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[2]/div[1]/div/section[2]/div").get_attribute("innerText")
    write_title_to_csv(type + " " + name + "\n" + text)

    print("\t" + type + "日志:" + name + "获取完毕")
    driver.back()


def extract_exercise_from_homework(driver, wait, name, type):
    '''从作业日志中提取习题'''
    wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div/div/div")))
    time.sleep(0.5)
    # 获取题目数量
    num = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[1]/div/div[2]/div[1]/div/div/div/div").text.split("/")[1].split("题")[0]
    print("\t该日志有" + str(num) + "道习题，正在获取……")
    write_title_to_csv(type + " " + name)

    for j in range(1, int(num) + 1):
        wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div")))
        print("\t\t获取第" + str(j) + "道，共" + str(num) + "道")
        typeEx = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/div/div[1]").text.split(".")[1].split("题")[0]  # 获取题目类型
        question = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/div").text  # 获取题目

        opt = []
        for k in range(1, 5):
            if typeEx == "判断":
                break
            try:
                opt.append(driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/div/div[2]/div/ul/li[" + str(k) + "]/label/span[2]/span[2]").text)  # 获取选项
            except NoSuchElementException:
                break

        answer = driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[1]/div[1]/div/div/div[3]/div[1]/div/div[2]/div").text.split("：")[1].split(" ")[1]  # 获取答案
        write_exercise_to_csv1(typeEx, question, opt, answer, j)
        if j < int(num):
            driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div/div[2]/div/div[2]/div[2]/div/div[3]/div/ul/li").click()  # 点击下一题

    print("\t" + type + "日志:" + name + "习题获取完毕")
    driver.back()


def roll_to_bottom(driver):
    '''滚动到网页真实的底部'''
    last_height = 0
    xpath = "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[2]/div[2]/div[2]/div[2]/div[1]/div"

    while True:
        # 滚动到网页底部
        driver.find_element(By.XPATH, "/html/body/div[4]/div[2]/div/div[1]/div[2]/div[1]/div/div/div/div[2]").click()
        driver.find_element(By.XPATH, "/html/body").send_keys(Keys.END)

        # 等待页面加载
        time.sleep(1)

        # 检查网页内容的高度是否发生变化
        element = driver.find_element(By.XPATH, xpath)
        new_height = driver.execute_script("return arguments[0].offsetHeight", element)
        if new_height == last_height:
            # 网页已经滚动到真实的底部
            break
        last_height = new_height
        # print(new_height)

    driver.find_element(By.XPATH, "/html/body").send_keys(Keys.END)
