from pykakasi import kakasi
import requests
import re


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


def Getinf(id_value):
    url = f"https://cmapi.aclgh.xyz/song/detail?ids={id_value}"
    response = requests.get(url)
    data = response.json()
    s_name = data["songs"][0]["name"]
    try:
        s_name_tns = data["songs"][0]["tns"]
        song_name = f"{s_name}({s_name_tns[0]})"
    except:
        song_name = f"{s_name}"
    singer_name = data["songs"][0]["ar"][0]["name"]
    inf = f"{song_name}--{singer_name}"
    return inf


def GetLyric(id_value):
    # id_value = 460528
    url = f"http://music.163.com/api/song/lyric?id={id_value}&lv=1&kv=1&tv=-1"
    response = requests.get(url)
    data = response.json()
    lyric = data['lrc']['lyric'].split("\n")
    tlyric = data['tlyric']['lyric'].split("\n")
    return lyric, tlyric


def Getid():
    id_url = input("The id of the song or the share url:")
    if id_url[0] == 'h':
        pattern = r"id=(\d+)"  # 匹配数字
        match = re.search(pattern, id_url)
        if match:
            return match.group(1)  # 第一个分组
    else:
        return id_url


def Combination(lyric, tlyric):
    com_lrc = ""
    pattern = "\[\d{2}:\d{2}\.\d{2,3}\]"  # 匹配时间
    for lrc in lyric:
        # 循环判断读取歌曲信息
        if "作词" in lrc or "作曲" in lrc or "编曲" in lrc:
            result = re.search(pattern, lrc)
            com_lrc += lrc.replace(result.group(), '').strip() + '\n'
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
                    com_lrc += lrc.replace(lrc_match.group(),  # 日文
                                           '') + '\n' + hats+'\n'  # 罗马音
                # if (not tlrc.endswith(']')) and lrc_match.group() == tlrc_match.group():
                    # 译文
                    com_lrc += tlrc.replace(tlrc_match.group(), '')+'\n\n'
    return com_lrc.replace('\n\n\n', '\n\n')  # 处理没有译文时的三个']n'


def Hatsuon(text):
    result = kakasi.convert(text)
    hatsuon = ""
    for item in result:
        hatsuon += (item["hepburn"]+' ')
    return hatsuon


def main():
    id_value = Getid()
    lrc = GetLyric(id_value)
    lyric, tlyric = lrc
    com_lyc = Combination(lyric, tlyric)
    inf = Getinf(id_value)
    with open(Remove_chars(f"{inf}"), 'w', encoding="utf-8") as file:
        file.write(inf+'\n'+com_lyc)
    file.close()


# 创建一个kakasi对象并设置转换模式
kakasi = kakasi()
kakasi.setMode("J", "a")
main()
