import re
import requests
from lxml import etree


# ===============常量定义===============


types = ("主线", "活动", "干员密录")
st_url = "https://prts.wiki"
sep = re.compile(r'\[[Dd]ialog\]')
subtitle = re.compile(
    r'\[[Ss]ubtitle\(.*text="(.*?)".*\)\]')
dialog = re.compile(r'\[[Nn]ame="(.*)".*\](.*)')
decision = re.compile(
    r'\[[Dd]ecision\(.*options="(.*)".*values="(.*)".*\)\]')
predicate = re.compile(r'\[[Pp]redicate\(.*references="(.*)".*\)\]')
multiline = re.compile(
    r'\[[Mm]ultiline\(name="(.*)"(\s*,\s*end=(true))?\)\](.*)')
demand = re.compile(r'(\[.*\])|(\{\{.*)|(\}\})')
act = re.compile(r'//act\s([\S\s]*)//memory')
ptn_all = re.compile(r'title:.*?/干员密录/\d+=.*?\s')
amount = 5


# ===============基石函数===============


def decorate(url: str) -> str:
    '''相对url转绝对url'''

    if not url.startswith("http"):
        if not url.startswith('/w/'):
            url = '/w/' + url
        url = st_url + url
    return url


def tag_filter(string: str) -> str:
    '''去除字符串中的html标签'''

    stack, string1 = [], ""
    for char in string:
        if char == '<':
            stack.append(char)
        elif char == '>':
            stack.pop()
        elif not stack:
            string1 += char
    if stack:
        print("< !>")
        assert False
    return string1


def file_name(ans: str, type_: str) -> str:
    '''返回对应类型的文件名'''

    if type_ == "主线":
        return f"明日方舟主题曲剧情（{ans}）.txt"
    elif type_ == "活动":
        return f"明日方舟活动剧情（{ans}）.txt"
    elif type_ == "干员密录":
        return f"明日方舟干员密录（{ans}）.txt"


# ===============底层函数===============


def get_story_dic() -> dict:
    '''获取剧情（主线、活动）字典\n
    dic: {类型名: {章节名: {关卡名: url, ...}, ...}, ...}'''

    url = "https://prts.wiki/w/剧情一览"
    resp = requests.get(url)
    text = resp.text
    html = etree.HTML(text)

    trs = html.xpath("//table/tbody/tr")
    dic = {}
    status = ""
    line_num = 0
    for tr in trs:
        th = tr.find('th')
        if th is None:
            break
        elif 'colspan' in th.attrib:
            status = th.find('a').text[:2]
            dic[status] = {}
        elif 'rowspan' in th.attrib:
            line_num = int(th.attrib['rowspan'])
            th1 = th.getnext()
            chapter = th.text.strip() + th1.text.strip()
            dic[status][chapter] = {}
            td = th1.getnext()
            ass = td.findall('a')
            for a in ass:
                name, link = a.text, a.attrib['href']
                dic[status][chapter][name] = decorate(link)
            line_num -= 1
        elif line_num > 0:
            chapter = th.text.strip()
            if chapter == "长夜临光" and chapter not in dic[status]:
                chapter = "长夜临光·后记"
            dic[status][chapter] = {}
            td = th.getnext()
            ass = td.findall('a')
            for a in ass:
                name, link = a.text, a.attrib['href']
                dic[status][chapter][name] = decorate(link)
            line_num -= 1
        else:
            chapter = th.text.strip()
            dic[status][chapter] = {}
            td = th.getnext().getnext()
            ass = td.findall('a')
            for a in ass:
                name, link = a.text, a.attrib['href']
                dic[status][chapter][name] = decorate(link)
    return dic


def get_secret_dic() -> dict:
    '''获取干员密录字典\n
    dic: {'干员密录': {干员名: {密录名: url, ...}, ...}}'''

    dic = {'干员密录': {}}
    url = "https://prts.wiki/w/Lancet-2/干员密录/1"
    resp = requests.get(url)
    text = resp.text
    html = etree.HTML(text)

    url_to_name = html.xpath("//script[@id='datas_override']/text()")[0]
    mmatches = re.findall(ptn_all, url_to_name)
    for mmatch in mmatches:
        mmatch = mmatch.strip()
        url = mmatch[6:].split('=')[0]
        operator = url.split('/')[0]
        name = mmatch.split('=')[-1]
        dic['干员密录'].setdefault(operator, {})[name] = decorate(url)

    return dic


def get_input(dic: dict) -> tuple:
    '''返回所需下载的类型列表和章节/干员列表字典\n
    type_list: [类型名, ...]\n
    titles: {类型名: [关卡/干员名, ...], ...}'''
    ans = input("Please input type: ").strip()
    if ans.lower() == "all":
        type_list = list(types)
    else:
        type_list = ans.split()

    titles = {}
    for type_ in type_list:
        ans = input(f"This is type: {type_}\nPlease input title: ").strip()
        if ans.lower() == "all":
            titles[type_] = list(dic[type_].keys())
        else:
            titles[type_] = ans.split()
    return type_list, titles


def get_page_text(data_text: str) -> str:
    '''从prts剧情代码中提取剧情文本'''

    page_text = ""
    lines = data_text.split('\n')
    string = "//\n\n"
    for line in lines:
        line = tag_filter(line.strip())
        if ans := re.match(multiline, line):
            group = list(map(lambda x: x.strip() if type(x)
                         == str else None, ans.groups()))
            name, endp, sentence = group[0], bool(group[2]), group[3]
            if not string.startswith("multi"):
                string = f"multi{name + '  ' if name else ''}"
            string += f"{sentence}"
            if endp:
                string += f"\n\n"
                string = string[5:]
                page_text += string
            continue
        if string.startswith("multi"):
            string = string[5:] + "\n\n"
            page_text += string
        if ans := re.match(sep, line):
            if string == "//\n\n":
                continue
            string = "//\n\n"
            page_text += string
        elif ans := re.match(subtitle, line):
            sentence = ans.group(1).strip()
            if sentence:
                string = f"居中显示文本  {sentence}\n\n"
                page_text += string
        elif ans := re.match(dialog, line):
            name, sentence = map(lambda x: x.strip() if type(
                x) == str else None, ans.groups())
            if sentence:
                string = f"{name + '  ' if name else ''}{sentence}\n\n"
                page_text += string
        elif ans := re.match(decision, line):
            string = ""
            for option, value in zip(*map(lambda x: x.split(';'), ans.groups())):
                string += f"选项{value.strip()}：{option.strip()}\n"
            string += '\n'
            page_text += string
        elif ans := re.match(predicate, line):
            num = ans.group(1).strip()
            string = f"选项{num}对应剧情：\n\n"
            page_text += string
        elif re.match(demand, line) or line.startswith("//"):
            continue
        else:
            string = f"{line}\n\n"
            page_text += string
    if page_text.strip().endswith("//"):
        page_text = page_text.strip()[:-2]
    return page_text


def download_chapter(chapter: str, dic: dict, type_: str):
    '''下载某章节/干员的剧情/密录'''

    chapter_text = ""
    for name in dic[type_][chapter]:
        resp = requests.get(dic[type_][chapter][name])
        text = resp.text
        html = etree.HTML(text)

        data_text = html.xpath("//script[@id='datas_txt']/text()")[0]
        page_text = f"===== {name} =====\n\n{get_page_text(data_text)}"
        chapter_text += page_text
    chapter_text = chapter_text.strip()

    with open(f"{type_}\\{file_name(chapter, type_)}", 'w', encoding='utf-8') as f:
        f.write(chapter_text)
