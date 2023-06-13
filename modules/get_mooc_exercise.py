import io
import os
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.microsoft import EdgeChromiumDriverManager


def get():
    print("请输入需要导出的练习章节数，（非零整数）", end="")
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
    driver.add_cookie(
        {'name': 'STUDY_SESS',
         'value': '\"p8soX2V3gOna1kDAp9N1bYqRowqWAOJktczrfmeGCtf9KEToTikkD0AGnQy+THlIb3ZiO9t4i38s59iq+MfRmrk4Woz3hBDxRvRmEVVfqSP4+1YL+yzPCJQdocnvuj4hmJnvgKc3JNMUCExy8lx+Y11kjYuHGa5uocfKWdGVlpYLhur2Nm2wEb9HcEikV+3FTI8+lZKyHhiycNQo+g+/oA==\"',
         'domain': '.icourse163.org'})
    # driver.get(
    #     "file://C:/Users/11969/OneDrive/桌面/毛泽东思想和中国特色社会主义理论体系概论（曾丽萍）_中国大学MOOC(慕课).html")
    driver.refresh()
    i = 0

    if os.path.exists("MOOC_result.csv"):
        os.remove("MOOC_result.csv")

    while True:
        if i == exercise:
            # print("已完成")
            break
        print(
            "请登录MOOC账号,并点击到您需要导出的练习页面,若当前练习公布了正确答案请输入Y继续,未公布正确答案,请输入y继续,输入其他任意字符退出")
        option = input()
        if option != "Y" and option != "y":
            print("已退出")
            exit(0)

        div = driver.find_element(By.XPATH,
                                  "/html/body/div[5]/div[2]/div[4]/div[2]/div/div[1]/div/div[4]/div/div[1]/div[1]")
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
            with open('result.csv', 'a', encoding='utf-8', errors='ignore') as file:
                writer = io.TextIOWrapper(file.buffer, write_through=True)
                writer.write(title.encode('utf-8').decode('utf-8'))
                writer.write("\n")
                for a in range(count):
                    if tips != "":
                        writer.write(tips.encode('utf-8').decode('utf-8'))
                        writer.write("\n")
                    writer.write(
                        "(" + type[a] + ") " + str(a + 1) + "." + question[a].replace("\u200c", "").replace("\u200d",
                                                                                                            "") + ","
                        + str(options1[a]).replace(" ", "").split("[")[1].split("]")[0].replace("'", "")
                        + ",," + answer[a].replace("、", ""))
                    writer.write("\n")
                writer.close()
        except IOError as e:
            print(e)

    print("结果已写入MOOC_result.csv\n")
