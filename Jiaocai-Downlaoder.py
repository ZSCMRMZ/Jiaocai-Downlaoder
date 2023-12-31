from tkinter import ttk, filedialog, messagebox
import re
import urllib.parse
import requests
from ttkbootstrap import Style

def download_file(url, save_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
        return True
    return False

def download_handler():
    url = url_entry.get()

    #提取contentId
    pattern = r'contentId=([^&]+)'
    match = re.search(pattern, url)
    if match:
        content_id = match.group(1)
        download_url = f"https://r2-ndr.ykt.cbern.com.cn/edu_product/esp/assets_document/{content_id}.pkg/pdf.pdf"

        #URL编码
        download_url = urllib.parse.quote(download_url, safe='/:')

        #选择保存位置
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
        if save_path:
            if download_file(download_url, save_path):
                messagebox.showinfo("下载成功", "文件已保存")
            else:
                messagebox.showerror("下载失败", "文件下载失败，请检查网址是否有效")
    else:
        messagebox.showerror("错误", "网址应包含'contentId='")

#主题
style = Style(theme='cosmo')
style.configure('.', font=('System', 20))
style.configure('TButton', font=('System', 20), padding=4)

#主窗口
root = style.master
root.title("国家中小学智慧教育平台电子教材下载器")
root.geometry('450x150')
root.iconbitmap('icon.ico')
root.resizable(False, False)

#标签 输入框
url_label = ttk.Label(root, text="URL")
url_label.pack()
url_entry = ttk.Entry(root, width=50)
url_entry.pack()

#下载按钮
download_button = ttk.Button(root, text="Download", command=download_handler)
download_button.pack(expand=True)

root.mainloop()
