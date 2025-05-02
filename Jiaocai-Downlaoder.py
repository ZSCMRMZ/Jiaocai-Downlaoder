from tkinter import ttk, filedialog, messagebox, StringVar
from tkinter.scrolledtext import ScrolledText
import re
import urllib.parse
import requests
from ttkbootstrap import Style
import threading
from queue import Queue
import os
from collections import deque


class DownloadTask:
    def __init__(self, url, progress_bar, status_var, title_label):
        self.url = url
        self.progress_bar = progress_bar
        self.status_var = status_var
        self.title_label = title_label
        self.running = True


def download_file(task, save_path):
    try:
        pattern = r'contentId=([^&]+)'
        match = re.search(pattern, task.url)
        if not match:
            task.status_var.set("无效URL")
            return False

        content_id = match.group(1)
        download_url = f"https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/{content_id}.pkg/pdf.pdf"
        download_url = urllib.parse.quote(download_url, safe='/:')

        response = requests.get(download_url, stream=True, timeout=10)
        total_size = int(response.headers.get('content-length', 0))

        with open(save_path, 'wb') as file:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=1024):
                if not task.running:
                    return False
                file.write(chunk)
                downloaded += len(chunk)
                progress = (downloaded / total_size) * 100 if total_size > 0 else 0
                task.progress_bar['value'] = progress
                task.status_var.set(f"下载中 {progress:.1f}%")

        task.status_var.set("下载完成")
        task.title_label.config(foreground="green")
        return True
    except Exception as e:
        task.status_var.set(f"错误: {str(e)}")
        task.title_label.config(foreground="red")
        return False


def download_worker():
    while True:
        task, save_path = task_queue.get()
        if task is None:
            break
        success = download_file(task, save_path)
        if not success:
            task.progress_bar['value'] = 0
        task_queue.task_done()


def start_download():
    global url_queue
    urls = url_text.get("1.0", "end-1c").splitlines()
    url_queue = deque([url.strip() for url in urls if url.strip()])

    if not url_queue:
        messagebox.showwarning("警告", "请输入至少一个URL")
        return

    # 禁用开始按钮
    start_btn.config(state="disabled")
    process_next_url()


def process_next_url():
    if not url_queue:
        start_btn.config(state="normal")
        return

    url = url_queue.popleft()
    idx = len(url_queue) + 1

    # 创建下载任务组件
    frame = ttk.Frame(main_frame)
    frame.pack(fill='x', pady=2, padx=5)

    default_name = f"教材_{idx}.pdf"
    title_label = ttk.Label(frame, text=default_name, width=20)
    title_label.pack(side='left', padx=5)

    progress_bar = ttk.Progressbar(frame, orient='horizontal', length=200, mode='determinate')
    progress_bar.pack(side='left', padx=5)

    status_var = StringVar(value="等待保存路径")
    status_label = ttk.Label(frame, textvariable=status_var, width=15)
    status_label.pack(side='left', padx=5)

    # 异步弹出保存对话框
    root.after(100, lambda: show_save_dialog(
        url, frame, progress_bar, status_var, title_label, default_name
    ))


def show_save_dialog(url, frame, progress_bar, status_var, title_label, default_name):
    save_path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        initialfile=default_name,
        filetypes=[("PDF Files", "*.pdf")]
    )

    if save_path:
        actual_name = os.path.basename(save_path)
        title_label.config(text=actual_name)
        task = DownloadTask(url, progress_bar, status_var, title_label)
        task_queue.put((task, save_path))
        status_var.set("已加入队列")
    else:
        status_var.set("已取消")
        frame.destroy()

    # 处理下一个URL
    root.after(100, process_next_url)


def stop_download():
    while not task_queue.empty():
        task, _ = task_queue.get()
        task.running = False
        task_queue.task_done()
    messagebox.showinfo("停止", "所有下载任务已终止")


# 初始化线程池
task_queue = Queue()
for _ in range(3):
    threading.Thread(target=download_worker, daemon=True).start()

# GUI设置
style = Style(theme='cosmo')
root = style.master
root.title("国家中小学智慧教育平台电子教材下载器")
root.geometry('720x480')
root.resizable(False, False)

try:
    root.iconbitmap('icon.ico')
except Exception as e:
    print(f"图标加载失败: {str(e)}")

main_frame = ttk.Frame(root)
main_frame.pack(fill='both', expand=True, padx=10, pady=10)

url_label = ttk.Label(main_frame, text="输入多个教材URL（每行一个）:")
url_label.pack(anchor='w', pady=5)
url_text = ScrolledText(main_frame, height=8, width=80)
url_text.pack(fill='x')

button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=15)
start_btn = ttk.Button(button_frame, text="开始下载", command=start_download, width=12)
start_btn.pack(side='left', padx=8)
ttk.Button(button_frame, text="停止下载", command=stop_download, width=12).pack(side='left', padx=8)

root.mainloop()
