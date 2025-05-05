from tkinter import ttk, filedialog, messagebox, Menu
import re
import urllib.parse
import requests
from ttkbootstrap import Style
import threading

# 全局变量用于控制下载
stop_download = False
response = None


def download_file(url, save_path, update_progress):
    global stop_download, response
    stop_download = False
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('Content-Length', 0))
        downloaded = 0

        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                if stop_download:
                    break
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    update_progress(downloaded, total_size)
        return not stop_download
    except Exception as e:
        print(e)
        return False
    finally:
        response = None


def update_progress(downloaded, total):
    progress = (downloaded / total) * 100 if total != 0 else 0
    progress_bar['value'] = progress
    root.after(10, lambda: None)  # 强制更新UI


def download_thread():
    url = url_entry.get()
    match = re.search(r'contentId=([^&]+)', url)
    if not match:
        messagebox.showerror("错误", "应包含'contentId='")
        return

    content_id = match.group(1)
    download_url = f"https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/{content_id}.pkg/pdf.pdf"
    download_url = urllib.parse.quote(download_url, safe='/:')

    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    if not save_path:
        return

    progress_bar['value'] = 0
    download_button.config(state='disabled')
    stop_button.config(state='normal')

    success = download_file(download_url, save_path, update_progress)

    download_button.config(state='normal')
    stop_button.config(state='disabled')

    if success:
        messagebox.showinfo("下载成功", "文件已保存")
    else:
        messagebox.showerror("下载失败", "下载被取消或失败")


def start_download():
    threading.Thread(target=download_thread, daemon=True).start()


def cancel_download():
    global stop_download, response
    stop_download = True
    if response:
        response.close()


# GUI设置
style = Style(theme='cosmo')
style.configure('.', font=('System', 20))
style.configure('TButton', font=('System', 20), padding=4)

root = style.master
root.title("国家中小学智慧教育平台电子教材下载器")
root.geometry('450x200')
root.resizable(False, False)
root.iconbitmap('icon.ico')

# 控件
url_label = ttk.Label(root, text="URL")
url_label.pack()
url_entry = ttk.Entry(root, width=50)
url_entry.pack()

progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='determinate')
progress_bar.pack(pady=10)

button_frame = ttk.Frame(root)
button_frame.pack(pady=5)

download_button = ttk.Button(button_frame, text="START", command=start_download)
download_button.pack(side='left', padx=5)

stop_button = ttk.Button(button_frame, text="STOP", command=cancel_download, state='disabled')
stop_button.pack(side='left', padx=5)


# 菜单栏
menubar = Menu(root)
root.config(menu=menubar)
menubar.add_command(label="工作原理", command=lambda: messagebox.showinfo("工作原理","教科书的统一下载链接为“https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/{content_id}.pkg/pdf.pdf”，所以只需要提取所提供URL中的contenId替换进下载链接即可"))
menubar.add_command(label="关于我们", command=lambda:messagebox.showinfo("关于我们", "Copyright © 2023-2025 MRMZSoft  All Rights Reserved. "
                                "\n访问我们的GitHub主页：https://github.com/MRMZSoft"
                                "\n\n项目地址：https://github.com/MRMZSoft/Jiaocai-Downloader"
                                "\n如果你觉得还不错，欢迎Star！"))

root.mainloop()
