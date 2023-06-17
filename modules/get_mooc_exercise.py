import io
import os
import time
import json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, JavascriptException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def show_noti(driver, noti):
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
    try:
        driver.execute_script("var div = document.querySelector('#HWinZnieJ');div.remove();")
    except JavascriptException:
        pass


def read_config():
    try:
        with open('./config.cfg', encoding='utf-8') as file:
            content = file.read()
            return content
    except FileNotFoundError:
        return ""


def save_config(content):
    with open('./config.cfg', 'a', encoding='utf-8') as file:
        file.write(content)


def delete_line_with_keyword(file_path, keyword):
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


def remove_non_gbk_chars(text: str) -> str:
    result = ""
    for char in text:
        try:
            char.encode("gbk")
            result += char
        except UnicodeEncodeError:
            continue
    return result


def get():
    if os.path.exists("MOOC_result.csv"):
        del_file = input("\n需要删除上次生成结果文件才能继续，删除吗？\nY/y：删除\n其他字符：退出\n请选择：").lower()
        if del_file == "y":
            os.remove("MOOC_result.csv")
            print("已删除")
        else:
            print("您已取消练习题导出")
            return

    print("\n请输入需要导出的练习章节数，（非零整数）", end="")
    try:
        exercise = int(input(""))
    except TypeError:
        print("输入数据错误")
        return

    if exercise <= 0:
        print("输入数据错误")
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
    driver.get("https://www.icourse163.org/")
    # driver.add_cookie(
    #     {'name': 'STUDY_SESS',
    #      'value': '',
    #      'domain': '.icourse163.org'})

    cookie_valid = False
    cookie_expired = False
    try:
        cookie_config = read_config()
        cookie = json.loads(cookie_config.split("MOOC#")[1].split("#")[0])
        cookie1 = json.loads(cookie_config.split("MOOC#")[2].split("#")[0])
        if cookie != "":
            if int(cookie_config.split("MOOC#")[1].split("#")[1]) < int(time.time()):
                cookie_expired = True
            else:
                driver.add_cookie(cookie)
                driver.add_cookie(cookie1)
                cookie_valid = True
                driver.refresh()
                print("使用Cookie登录成功")
                show_noti(driver, "请返回Python查看使用说明")
    except IndexError:
        print("未保存Cookie")

    # driver.get(
    #     "file://C:/Users/11969/OneDrive/桌面/毛泽东思想和中国特色社会主义理论体系概论（曾丽萍）_中国大学MOOC(慕课).html")
    i = 0

    while True:
        if i == exercise:
            print("已完成")
            break

        if cookie_expired:
            print("保存的Cookie已过期，请重新进行登录操作")
            show_noti(driver, "<br>保存的Cookie已过期，请重新进行登录操作，然后返回Python查看使用说明")
        elif not cookie_valid:
            print("请登录MOOC账号")
            show_noti(driver, "<br>请登录MOOC账号，然后返回Python查看使用说明")

        print(
            "点击到您需要导出的练习页面,若当前练习公布了正确答案请输入Y继续,未公布正确答案,请输入y继续,输入其他任意字符退出")
        option = input()
        if option != "Y" and option != "y":
            print("已退出")
            exit(0)

        if not cookie_valid:
            delete_line_with_keyword("./config.cfg", "MOOC#")
            cookie_timestamp = int(time.time()) + 86400 * 3
            cookie_timestamp1 = time.gmtime(cookie_timestamp)
            cookie_timestamp1 = time.strftime("%Y-%m-%d", cookie_timestamp1)
            save_config("\nMOOC#" + json.dumps(driver.get_cookie('STUDY_SESS')) + "#" + str(cookie_timestamp))
            save_config("\nMOOC#" + json.dumps(driver.get_cookie('STUDY_INFO')) + "#" + str(cookie_timestamp))
            print("Cookie已保存，" + cookie_timestamp1 + "前可自动登录")
        delete_noti(driver)

        driver.switch_to.window(driver.window_handles[-1])  # 切换到新窗口

        for i2 in range(0, len(driver.window_handles) - 1):
            try:
                div = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]")
                break
            except NoSuchElementException:
                driver.switch_to.window(driver.window_handles[i2])

        children = div.find_elements(By.XPATH, "./*")
        count = len(children)
        print(f"当前页面练习题个数为:{count}")
        print("开始获取......")
        title = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[1]/h2").text
        question = [""] * count
        options1 = [[""] * 5 for i in range(count)]
        answer = [""] * count
        type = [""] * count
        tips = ""
        q = 0

        if option == "Y":
            for temp in range(1, count + 1):
                try:
                    print(f"正在获取第{temp}题")
                    question[temp - 1] = driver.find_element(By.XPATH,
                                                             f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[1]/div[2]/div[3]/p").text
                    type[temp - 1] = driver.find_element(By.XPATH,
                                                         f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[1]/div[2]/div[2]/span").text
                    div = driver.find_element(By.XPATH,
                                              f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/div/ul")
                    children = div.find_elements(By.XPATH, "./*")
                    optionCount = len(children)
                    for t in range(1, optionCount + 1):
                        try:
                            options1[temp - 1][t - 1] = chr(ord('A') + t - 1) + "." + driver.find_element(By.XPATH,
                                                                                                          f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/div/ul/li[{t}]/label/div[2]/p/span").text
                        except NoSuchElementException:
                            options1[temp - 1][t - 1] = chr(ord('A') + t - 1) + "." + driver.find_element(By.XPATH,
                                                                                                          f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/div/ul/li[{t}]/label/div[2]/p[1]").text
                    answer[temp - 1] = driver.find_element(By.XPATH,
                                                           f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/div/div/div/span[2]").text
                    q += 1
                except:
                    print(f"第{temp}题获取失败")
            if q == count:
                print(f"{title}获取成功")
                i += 1
        else:
            tips = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[2]").text
            for temp in range(1, count + 1):
                try:
                    print(f"正在获取第{temp}题")
                    question[temp - 1] = driver.find_element(By.XPATH,
                                                             f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[1]/div[2]/div[3]/p").text
                    type[temp - 1] = driver.find_element(By.XPATH,
                                                         f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[1]/div[2]/div[2]/span").text
                    div = driver.find_element(By.XPATH,
                                              f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/ul")
                    children = div.find_elements(By.XPATH, "./*")
                    optionCount = len(children)
                    answerOption = [""] * count
                    for t in range(1, optionCount + 1):
                        try:
                            options1[temp - 1][t - 1] = chr(ord('A') + t - 1) + "." + driver.find_element(By.XPATH,
                                                                                                          f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/ul/li[{t}]/label/div[2]/p/span").text
                            answerOption[temp - 1] = driver.find_element(By.XPATH,
                                                                         f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/ul/li[{t}]/input").get_attribute(
                                "checked")
                            if answerOption[temp - 1] != None:
                                answer[temp - 1] += chr(ord('A') + t - 1)
                        except NoSuchElementException:
                            options1[temp - 1][t - 1] = chr(ord('A') + t - 1) + "." + driver.find_element(By.XPATH,
                                                                                                          f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/ul/li[{t}]/label/div[2]/p[1]").text
                            answerOption[temp - 1] = driver.find_element(By.XPATH,
                                                                         f"/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]/div[{temp}]/div[2]/ul/li[{t}]/input").get_attribute(
                                "checked")
                            if answerOption[temp - 1] != None:
                                answer[temp - 1] += chr(ord('A') + t - 1)
                    q += 1
                except:
                    print(f"第{temp}题获取失败")
            if q == count:
                print(f"{title} 获取成功")
                i += 1

        try:
            with open('MOOC_result.csv', 'a', encoding='gbk', errors='ignore') as file:
                writer = io.TextIOWrapper(file.buffer, write_through=True)
                writer.write(remove_non_gbk_chars(title))
                writer.write("\n")
                for a in range(count):
                    if tips != "":
                        writer.write(remove_non_gbk_chars(tips))
                        writer.write("\n")
                    writer.write(
                        "(" + remove_non_gbk_chars(type[a]) + ") " + str(a + 1) + "." + remove_non_gbk_chars(question[a]) + ","
                        + remove_non_gbk_chars(str(options1[a])).replace(" ", "").split("[")[1].split("]")[0].replace("'", "")
                        + ",," + remove_non_gbk_chars(answer[a]).replace("、", ""))
                    writer.write("\n")
                writer.close()
        except IOError as e:
            print(e)

    print("结果已写入MOOC_result.csv\n")
