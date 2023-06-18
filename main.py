from modules import get_mooc_exercise
from modules import rain_class_ppt_to_excel
from modules import get_rain_class_online_exercise
from modules import chat_with_ai

if __name__ == '__main__':
    print("\n欢迎使用HWinZnieJ学习小助手")
    while True:
        print("""       主菜单
        1.导出雨课堂PPT中的练习到Excel表格
        2.导出中国大学慕课平台MOOC的练习题到Excel表格
        3.导出雨课堂的日志中包含的练习题到Excel表格
        4.与AI大语言模型聊天
        其他字符退出程序""")
        user_input = input("请选择您要进行的操作，回车确定：")
        if user_input == "1":
            rain_class_ppt_to_excel.run()
        elif user_input == "2":
            get_mooc_exercise.get()
        elif user_input == "3":
            get_rain_class_online_exercise.get()
        elif user_input == "4":
            chat_with_ai.chat()
        else:
            print("\n感谢您的使用，再见！")
            exit(0)
