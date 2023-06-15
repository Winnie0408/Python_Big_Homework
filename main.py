from modules import get_mooc_exercise
from modules import rain_class_ppt_to_excel
from modules import get_rain_class_online_exercise

if __name__ == '__main__':
    print("欢迎使用HWinZnieJ学习小助手")
    while True:
        print("1.导出雨课堂PPT中的练习到Excel表格\n2.导出中国大学慕课平台MOOC的练习题到Excel表格\n其他字符退出程序")
        user_input = input("请选择您要进行的操作，回车确定：")
        if user_input == "1":
            rain_class_ppt_to_excel.run()
        elif user_input == "2":
            get_mooc_exercise.get()
        elif user_input == "3":
            get_rain_class_online_exercise.get()
        else:
            print("\n感谢您的使用，再见！")
            exit(0)
