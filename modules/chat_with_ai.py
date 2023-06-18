import requests
import socket
import threading
import time
import random
import re

ai_response = ""
ai_response_lock = threading.Lock()
ai_status = 0  # 0: 等待用户提问/思考中 1：AI回复中 2: AI回复完成

thread1_stop = False
thread2_stop = False


def send_user_message(message):
    url = "http://gptbot.hwinzniej.top:28234/v2/chat"
    headers = {'Content-Type': 'application/json'}
    data = {
        "session_id": f"LearningHelper-{socket.gethostname()}",
        "username": f"{socket.gethostname()}",
        "message": f"{message}"
    }
    response = requests.post(url, headers=headers, json=data)
    return response


def get_ai_status(msg_id):
    url = f"http://gptbot.hwinzniej.top:28234/v2/chat/response?request_id={msg_id}"
    while True:
        response = requests.get(url).json()
        try:
            result = response["message"][0]
            return result
        except IndexError:
            pass
        if response["result"] == "DONE":
            break
        time.sleep(1)


def get_ai_response(msg_id):
    global ai_response
    global ai_status
    global thread1_stop
    global thread2_stop
    url = f"http://gptbot.hwinzniej.top:28234/v2/chat/response?request_id={msg_id}"
    while True:
        if thread1_stop:
            break

        response = requests.get(url).json()

        try:
            with ai_response_lock:
                ai_response += response["message"][0]
        except IndexError:
            if ai_status == 0:
                print(".", end="")
            pass
        try:
            if str(response["message"][0]).__contains__("出现故障"):
                print(f"\n\n错误详情：{response['message'][0].split('错误详情：')[1]}", end="")
                response["result"] = "FAILED"
        except IndexError:
            pass

        if response["result"] == "DONE":
            print("后端已完成回复")
            ai_status = 2
            print("\n==========AI开始回复==========\n")
            break

        if response["result"] == "FAILED":
            thread1_stop = True
            thread2_stop = True
            break
        time.sleep(generate_random_number(3, 5))


def generate_random_number(start, end):
    # 生成指定范围内的随机整数
    if isinstance(start, int) and isinstance(end, int):
        return random.randint(start, end)
    # 生成指定范围内的随机小数
    elif isinstance(start, float) or isinstance(end, float):
        return random.uniform(start, end)


def print_ai_response():
    global ai_response
    global ai_status
    global thread2_stop
    while True:
        if thread2_stop:
            print("\n==========抱歉，出现错误，已停止回答，请稍后或切换模型再试==========")
            break

        num_to_print = generate_random_number(2, 5)

        if len(ai_response) > 0:
            if ai_status != 2:
                ai_status = 1

            print(ai_response[:num_to_print], end="")
            with ai_response_lock:
                ai_response = ai_response[num_to_print:]
        # print("ai_status:" + str(ai_status) + ", ai_response:" + ai_response)
        if ai_status == 2 and len(ai_response) == 0:
            print("\n\n==========AI回复完成==========")
            break
        time.sleep(generate_random_number(0.05, 0.2))


def show_help():
    print("""==========使用说明==========
目前支持下列命令：
1.切换AI xxx（注意空格）
如：切换AI bing-p
永久切换至另一个AI语言模型，直到AI后端重启。（默认使用的是chatgpt-api）
可用的语言模型，请给我发送“ping”命令来查看。

2. 重置会话
清空AI的记忆，重新开始聊天。

3. 回滚会话
相当于撤回消息，让AI忘记你最后一次发的内容。

4. 加载预设 xxx
如：加载预设 MOSS
让AI加载某个特定的预设。默认不加载任何预设。
目前支持的预设有：
正常，猫娘，高启强，MOSS，小黑子，丁真，张维为，疯子，怼我，一个还算可以的丁真，胡锡进，律师，答疑助手，室内设计师，小说家，诗人，必应
==========使用说明==========""")


def convert_eng_to_chinese(text):
    match text:
        case "chatgpt-web":
            return "OpenAI ChatGPT 网页版"
        case "chatgpt-api":
            return "OpenAI ChatGPT API版"
        case "bing-c":
            return "微软 新必应 (创造力)"
        case "bing-b":
            return "微软 新必应 (平衡)"
        case "bing-p":
            return "微软 新必应 (精确)"
        case "bard":
            return "Google Bard"
        case "yiyan":
            return "百度 文心一言模型"
        case "poe-sage":
            return "POE Sage 模型"
        case "poe-gpt4":
            return "POE ChatGPT4 模型"
        case "poe-claude":
            return "POE Claude 模型"
        case "poe-claude2":
            return "POE Claude+ 模型"
        case "poe-claude100k":
            return "POE Claude 100k 模型"
        case "poe-chatgpt":
            return "POE ChatGPT 模型"
        case "poe-dragonfly":
            return "POE Dragonfly 模型"
        case "poe-neevaai":
            return "POE Neeva AI 模型"
        case "slack-claude":
            return "Slack Claude 模型"
        case "xinghuo":
            return "讯飞 星火大模型"


def chat():
    global thread1_stop
    global thread2_stop
    global ai_status
    global ai_response

    print("正在连接AI服务器，请稍候……")

    test = send_user_message("文本模式").status_code
    if test != 200:
        print(f"AI服务器连接失败，错误代码：HTTP ERROR {test}，请检查您的网络状况并稍后再试。")
        return

    print("连接成功！正在初始化……")

    status = str(get_ai_status(send_user_message("ping").text))
    current_ai_model = status.split("当前AI：")[1].split(" /")[0]

    print("全部完成！\n可用命令：\nexit(): 返回主菜单\nhelp(): 获取使用说明")
    while True:
        input_message = input(f"\n当前模型：{convert_eng_to_chinese(current_ai_model)}\n请输入您要发送的消息或命令：")
        if input_message == "exit()":
            print("就聊到这里吧，下次再见！")
            time.sleep(1)
            return
        elif input_message == "help()":
            show_help()
            continue

        if input_message[:5] == "切换AI ":
            response = str(get_ai_status(send_user_message(input_message).text))
            print(response)
            if response.__contains__("现在开始和我聊天吧！"):
                current_ai_model = input_message[5:]
            continue

        if input_message[:4] == "ping" and len(input_message) == 4:
            print(str(get_ai_status(send_user_message(input_message).text)).split("\n\n可用语音：")[0])
            continue

        if re.search(r'重置会话|回滚会话', input_message) is not None and len(input_message) == 4:
            print(str(get_ai_status(send_user_message(input_message).text)))
            continue

        msg_id = send_user_message(input_message)
        if msg_id.status_code != 200:
            print(f"AI服务器连接失败，错误代码：HTTP ERROR {msg_id.status_code}，请检查您的网络状况并稍后再试。")
            continue

        thread1_stop = False
        thread2_stop = False
        ai_response = ""
        ai_status = 0

        print("AI正在思考，请稍候.", end="")
        # t1 = threading.Thread(target=get_ai_response(msg_id.text))
        t1 = threading.Thread(target=get_ai_response, args=(msg_id.text,))
        t2 = threading.Thread(target=print_ai_response)

        t1.start()
        t2.start()

        t1.join()
        t2.join()
