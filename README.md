# A Downloader for Arknights Stories

一个从PRTS上下载明日方舟剧情文案（含**主线、活动、干员密录**）的爬虫

## 使用说明

1. 下载并安装3.8及以上版本的Python（勾选Add to PATH）
2. 安装requests库与lxml库（在命令行中运行以下命令）：
    ```sh
    pip install requests
    pip install lxml
    ```
3. 用Python打开main.py（在命令行中运行以下命令）：
    ```sh
    python main.py
    ```
4. 用**空格**分隔要下载的剧情类型（主线、活动、干员密录），或输入```All```下载全部。按下回车
5. 接下来每一个类型都会跳出来叫你输入。用**空格**分隔要下载的剧情名（主线名、活动名、干员名），或输入```All```下载全部。按下回车
6. 在黑窗口前无聊地等它运行完
7. 然后你就发现剧情都在对应类型的文件夹里了