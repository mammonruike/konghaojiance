import tkinter as tk
from tkinter import ttk, messagebox
import urllib.parse
import urllib3
import json
import ssl

class PhoneVerificationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("实名信息核验工具")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # 内嵌的AppCode
        self.APPCODE = "您的阿里云密钥"
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure("Title.TLabel", font=("Arial", 18, "bold"), foreground="#2c3e50")
        style.configure("Input.TLabel", font=("Arial", 11), foreground="#34495e")
        style.configure("Result.TLabel", font=("Arial", 12, "bold"))
        style.configure("Success.TLabel", foreground="#27ae60")
        style.configure("Error.TLabel", foreground="#e74c3c")
        style.configure("Warning.TLabel", foreground="#f39c12")
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="实名信息核验工具", style="Title.TLabel")
        title_label.pack(pady=(0, 20))
        
        # 输入区域框架
        input_frame = ttk.LabelFrame(main_frame, text="验证信息", padding="15")
        input_frame.pack(fill="x", pady=(0, 20))
        
        # 姓名输入
        name_frame = ttk.Frame(input_frame)
        name_frame.pack(fill="x", pady=5)
        name_label = ttk.Label(name_frame, text="姓名:", style="Input.TLabel", width=10, anchor="w")
        name_label.pack(side="left")
        self.name_entry = ttk.Entry(name_frame, width=35, font=("Arial", 11))
        self.name_entry.pack(side="right", fill="x", expand=True)
        
        # 手机号输入
        phone_frame = ttk.Frame(input_frame)
        phone_frame.pack(fill="x", pady=5)
        phone_label = ttk.Label(phone_frame, text="手机号:", style="Input.TLabel", width=10, anchor="w")
        phone_label.pack(side="left")
        self.phone_entry = ttk.Entry(phone_frame, width=35, font=("Arial", 11))
        self.phone_entry.pack(side="right", fill="x", expand=True)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(0, 20))
        
        # 核验按钮
        verify_button = ttk.Button(button_frame, text="开始核验", command=self.verify, width=15)
        verify_button.pack(side="left", padx=(0, 10))
        
        # 清空按钮
        clear_button = ttk.Button(button_frame, text="清空", command=self.clear, width=15)
        clear_button.pack(side="left")
        
        # 结果区域框架
        result_frame = ttk.LabelFrame(main_frame, text="核验结果", padding="15")
        result_frame.pack(fill="both", expand=True)
        
        # 结果显示区域
        self.result_frame_inner = ttk.Frame(result_frame)
        self.result_frame_inner.pack(fill="both", expand=True)
        
        # 初始提示
        self.init_result_display()
        
    def init_result_display(self):
        # 清除之前的组件
        for widget in self.result_frame_inner.winfo_children():
            widget.destroy()
            
        # 显示提示信息
        info_label = ttk.Label(self.result_frame_inner, 
                              text="请输入姓名和手机号，点击'开始核验'进行验证", 
                              font=("Arial", 10),
                              foreground="#7f8c8d")
        info_label.pack(expand=True)
        
    def show_result_display(self, name, verification_result):
        # 清除之前的组件
        for widget in self.result_frame_inner.winfo_children():
            widget.destroy()
            
        # 创建结果展示
        result_container = ttk.Frame(self.result_frame_inner)
        result_container.pack(fill="both", expand=True)
        
        # 核验结果
        result_title = ttk.Label(result_container, text="查询结果", 
                                font=("Arial", 12, "bold"),
                                foreground="#2c3e50")
        result_title.pack(anchor="w", pady=(0, 10))
        
        # 根据结果设置显示文本和样式
        if verification_result == "1":
            result_text = "一致"
            result_style = "Success.TLabel"
            result_icon = "核验"
        elif verification_result == "-1":
            result_text = "不一致"
            result_style = "Error.TLabel"
            result_icon = "注意"
        else:
            result_text = "系统无记录"
            result_style = "Warning.TLabel"
            result_icon = "警告"
        
        result_value = ttk.Label(result_container, 
                                text=f"{result_icon} {result_text}",
                                style=result_style,
                                font=("Arial", 14, "bold"))
        result_value.pack(anchor="w", pady=(0, 15))
        
        # 姓名信息
        name_title = ttk.Label(result_container, text="姓名", 
                              font=("Arial", 12, "bold"),
                              foreground="#2c3e50")
        name_title.pack(anchor="w")
        
        name_value = ttk.Label(result_container, 
                              text=name,
                              font=("Arial", 11))
        name_value.pack(anchor="w", pady=(0, 10))
        
    def verify(self):
        # 获取输入值
        name = self.name_entry.get().strip()
        phone = self.phone_entry.get().strip()
        
        # 验证输入
        if not name:
            messagebox.showerror("输入错误", "请输入姓名")
            return
            
        if not phone:
            messagebox.showerror("输入错误", "请输入手机号")
            return
            
        if not phone.isdigit() or len(phone) != 11:
            messagebox.showerror("输入错误", "手机号格式不正确，请输入11位数字")
            return
            
        # 发送请求
        try:
            result = self.send_verification_request(name, phone)
            self.display_result(result)
        except Exception as e:
            messagebox.showerror("网络错误", f"请求失败: {str(e)}")
            
    def send_verification_request(self, name, phone):
        host = 'https://ptwo.market.alicloudapi.com'
        path = '/efficient/cellphone/mobiletwo'
        url = host + path
        
        # 创建不验证SSL证书的PoolManager（某些环境下可能需要）
        http = urllib3.PoolManager(cert_reqs=ssl.CERT_NONE)
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Authorization': 'APPCODE ' + self.APPCODE
        }
        
        bodys = {
            'mobile': phone,
            'name': name
        }
        
        post_data = urllib.parse.urlencode(bodys).encode('utf-8')
        response = http.request('POST', url, body=post_data, headers=headers)
        content = response.data.decode('utf-8')
        
        return json.loads(content)
        
    def display_result(self, data):
        # 解析结果
        error_code = data.get("error_code", -1)
        
        if error_code != 0:
            reason = data.get("reason", "未知错误")
            messagebox.showerror("核验失败", f"核验失败: {reason}")
            self.init_result_display()
        else:
            result_data = data.get("result", {})
            name = result_data.get("Name", "")
            verification_result = result_data.get("VerificationResult", "0")
            
            # 显示结果
            self.show_result_display(name, verification_result)
        
    def clear(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.init_result_display()
        # 设置焦点到姓名输入框
        self.name_entry.focus()

def main():
    root = tk.Tk()
    app = PhoneVerificationApp(root)
    # 设置窗口居中显示
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (400 // 2)
    root.geometry(f"500x400+{x}+{y}")
    root.mainloop()

if __name__ == "__main__":
    main()