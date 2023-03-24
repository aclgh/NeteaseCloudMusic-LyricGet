import tkinter as tk
from tkinter import ttk
from pykakasi import kakasi
import requests
import re
import xmltodict
import json


# 函数
def Remove_chars(string):
    # 定义一个包含windows文件名不能出现的字符的集合
    invalid_chars = set(r'<>:"/\|?*')
    # 创建一个空字符串用于存储结果
    result = ""
    # 遍历输入字符串中的每个字符
    for char in string:
        # 如果字符不在无效字符集合中，就添加到结果字符串中
        if char not in invalid_chars:
            result += char
    return result


def search_s(keywords):
    # 搜索歌曲
    url = f"https://cmapi.aclgh.xyz/search?keywords={keywords}&type=1"
    response = requests.get(url)
    global data
    data = response.json()
    for i in range(0, 30):
        try:
            name = data["result"]["songs"][i]["name"]
            s_name = data["result"]["songs"][i]["artists"][0]["name"]
            id_value = data["result"]["songs"][i]["id"]
            listbox.insert(i, f"{i+1}.{name}-{s_name} id:{id_value}")
        except:
            break
    # sn = int(input("Please enter the S/N:"))
    # return int(data["result"]["songs"][sn-1]["id"])


def Getinf(id_value):
    url = f"https://cmapi.aclgh.xyz/song/detail?ids={id_value}"
    response = requests.get(url)
    data = response.json()
    s_name = data["songs"][0]["name"]
    try:  # 尝试获取歌曲译名
        s_name_tns = data["songs"][0]["tns"]
        song_name = f"{s_name}({s_name_tns[0]})"
    except:
        song_name = f"{s_name}"
    singer_name = data["songs"][0]["ar"][0]["name"]
    inf = f"{song_name}--{singer_name}"
    return inf


def Getid(id_url):
    if id_url[0] == 'h':
        pattern = r"id=(\d+)"  # 匹配数字
        match = re.search(pattern, id_url)
        if match:
            return match.group(1)  # 第一个分组
    else:
        return id_url


def GetLyric(id_value):
    # id_value = 460528
    url = f"http://music.163.com/api/song/lyric?id={id_value}&lv=1&kv=1&tv=-1"
    response = requests.get(url)
    data = response.json()
    global lyric_orig
    lyric_orig = data['lrc']['lyric']
    lyric = data['lrc']['lyric'].split("\n")
    tlyric = data['tlyric']['lyric'].split("\n")
    return lyric, tlyric


def Combination(lyric, tlyric):
    global lyric_orig
    rlyric = Hatsuon(lyric_orig).split("\n")
    com_lrc = ""
    pattern = "\[\d{2}:\d{2}\.\d{2,3}\]"  # 匹配时间
    for lrc in lyric:
        # 循环判断读取歌曲信息
        if "作词" in lrc or "作曲" in lrc or "编曲" in lrc:
            result = re.search(pattern, lrc)
            com_lrc += lrc.replace(result.group(), '').strip() + '\n'
    if (mode.get() == 1):
        for rlrc in rlyric:
            rlrc_match = re.search(pattern, rlrc)
            rlrc.replace('\n', '')
            for tlrc in tlyric:
                tlrc_match = re.search(pattern, tlrc)
                tlrc.replace('\n', '')
                for lrc in lyric:
                    # 遍历原文译文列表
                    lrc.replace('\n', '')
                    lrc_match = re.search(pattern, lrc)
                    if lrc_match != None and tlrc_match != None and rlrc_match != None:  # 防止有空字符
                        if lrc_match.group() == tlrc_match.group() == rlrc_match.group():  # 比较时间的数值

                            com_lrc += lrc.replace(lrc_match.group(), '') + '\n' + \
                                rlrc.replace(rlrc_match.group(),
                                             '')+'\n'  # 罗马音
                            # 译文
                            com_lrc += tlrc.replace(tlrc_match.group(),
                                                    '')+'\n\n'
    elif (mode.get() == 0):

        for tlrc in tlyric:
            tlrc_match = re.search(pattern, tlrc)
            tlrc.replace('\n', '')
            for lrc in lyric:
                # 遍历原文译文列表
                lrc.replace('\n', '')
                lrc_match = re.search(pattern, lrc)
                if lrc_match != None and tlrc_match != None:  # 防止有空字符
                    if lrc_match.group() == tlrc_match.group():  # 比较时间的数值

                        hats = Hatsuon(lrc.replace(lrc_match.group(), ''))
                        com_lrc += lrc.replace(lrc_match.group(),
                                               '') + '\n' + hats + '\n'
                        # 译文
                        com_lrc += tlrc.replace(tlrc_match.group(),
                                                '')+'\n\n'
    return com_lrc.strip().replace("\n\n\n", "\n\n")   # 处理没有译文时的无意义空白输出


def Hatsuon(text):  # 传入非列表
    if (mode.get() == 1):
        url = "http://www.kawa.net/works/ajax/romanize/romanize.cgi"
        # 设置消息头
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        # 设置消息体
        data = {"mode": "japanese", "ie": "UTF-8", "q": f"{text}"}
        # 发送POST请求，并获取响应对象
        response = requests.post(url, headers=headers, data=data)
        # 将xml转换为字典
        if (response.text != ''):
            data = xmltodict.parse(response.text)
        # with open("lyric_rom.json", 'w', encoding="utf-8") as file:
        hatsuon = ''
        # with open("data.json", 'w', encoding="utf-8") as file:
        #     file.write(str(json.dumps(data)))
        for lis in data['ul']['li']:

            if lis["span"][0] != '[':
                hatsuon += '\n'
                try:
                    hatsuon += lis["span"][0]
                except:
                    continue
                for spans in lis["span"]:
                    try:
                        hatsuon += spans['@title']
                        hatsuon += ' '
                        print(hatsuon)
                    except:
                        continue
    elif (mode.get() == 0):
        print(text)
        result = kakasi.convert(text)
        hatsuon = ""
        for item in result:
            hatsuon += (item["hepburn"]+' ')
    return hatsuon


def search_song():
    value = input_entry.get()
    if search.get() == 1:
        id_value = Getid(value)
        Gene_lyric(id_value)
    elif search.get() == 0:
        search_s(value)


def Gene_lyric(id_value):
    lrc = GetLyric(id_value)
    lyric, tlyric = lrc
    com_lyc = Combination(lyric, tlyric)
    inf = Getinf(id_value)
    with open(Remove_chars(f"{inf}.txt"), 'w', encoding="utf-8") as file:
        file.write(inf+'\n'+com_lyc)
    file.close()


def List_confirm():
    global data
    Gene_lyric(int(data["result"]["songs"][listbox.curselection()[0]]["id"]))


# 创建kakasi对象
kakasi = kakasi()
kakasi.setMode("J", "a")

# 创建窗口
root = tk.Tk()
root.title("实例")
root.geometry("500x500")

# 初始化变量
mode = tk.IntVar(value=0)
search = tk.IntVar(value=0)

# 创建模式选择栏
mode_frame = ttk.Frame(root)
mode_frame.pack(fill='x')

mode_label = ttk.Label(mode_frame, text="模式选择：")
mode_label.pack(side='left')

pykakasi_radio = ttk.Radiobutton(
    mode_frame, text="pykakasi", variable=mode, value=0)
pykakasi_radio.pack(side='left')

api_radio = ttk.Radiobutton(mode_frame, text="api", variable=mode, value=1)
api_radio.pack(side='left')

# 创建输入设置栏位
search_frame = ttk.Frame(root)
search_frame.pack(fill='x')

search_label = ttk.Label(search_frame, text="输入设置：")
search_label.pack(side='left')

search_radio = ttk.Radiobutton(
    search_frame, text="search", variable=search, value=0)
search_radio.pack(side='left')

id_radio = ttk.Radiobutton(search_frame, text="id", variable=search, value=1)
id_radio.pack(side='left')

# 创建输入栏位和搜索键
input_frame = ttk.Frame(root)
input_frame.pack(fill='x')

input_label = ttk.Label(input_frame, text="输入：")
input_label.pack(side='left')

input_entry = ttk.Entry(input_frame, width=30)
input_entry.pack(side='left')

search_button = ttk.Button(input_frame, text="确认&搜索", command=search_song)
search_button.pack(side='left')

# 创建列表框和确认键
listbox_frame = ttk.Frame(root)
listbox_frame.pack(fill='x')

listbox_label = ttk.Label(listbox_frame, text="结果：")
listbox_label.pack(side='left')

listbox = tk.Listbox(listbox_frame, width=50, height=10)
listbox.pack(side='left')

main_button = ttk.Button(listbox_frame, text="确认", command=List_confirm)
main_button.pack(side='left')

# 创建输出栏
output_label = ttk.Label(root, text="输出：")
output_label.pack(side='left')

output_text = tk.Text(root, width=50, height=10)
output_text.pack(side='left')

# 运行窗口
root.mainloop()
