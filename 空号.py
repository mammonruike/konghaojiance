import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import urllib.request
import urllib.parse
import ssl
import json

class EmptyNumberDetector:
    def __init__(self, root):
        # 内嵌AppCode
        self.appcode = '您的阿里云密钥'
        
        self.root = root
        self.root.title("玛门睿科科技空号检测程序")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 手机号码输入 (移除了AppCode输入框)
        ttk.Label(main_frame, text="手机号码:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.mobile_var = tk.StringVar()
        self.mobile_entry = ttk.Entry(main_frame, textvariable=self.mobile_var, width=50)
        self.mobile_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # 检测按钮
        self.detect_button = ttk.Button(button_frame, text="检测号码", command=self.detect_number)
        self.detect_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按钮
        self.clear_button = ttk.Button(button_frame, text="清空结果", command=self.clear_result)
        self.clear_button.pack(side=tk.LEFT)
        
        # 结果显示区域框架
        result_frame = ttk.LabelFrame(main_frame, text="检测结果", padding="10")
        result_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # 创建结果展示区域
        self.result_canvas = tk.Canvas(result_frame)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.result_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.result_canvas.configure(
                scrollregion=self.result_canvas.bbox("all")
            )
        )
        
        self.result_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.result_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.result_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("就绪")
        self.status_bar = ttk.Label(root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # 状态描述映射
        self.status_descriptions = {
            "0": ("空号", "该号码是空号，不存在或未分配给任何用户"),
            "1": ("实号", "该号码是真实有效的号码"),
            "2": ("停机", "该号码已停机，暂时无法使用"),
            "3": ("库无", "该号码在数据库中没有相关信息"),
            "4": ("沉默号", "该号码长期不使用，处于沉默状态"),
            "5": ("风险号", "该号码存在风险，可能涉及诈骗或其他非法活动")
        }
        
    def detect_number(self):
        mobile_number = self.mobile_var.get().strip()
        
        if not mobile_number:
            messagebox.showerror("错误", "请输入手机号码")
            return
            
        self.status_var.set("正在检测...")
        self.root.update()
        
        try:
            host = 'https://juweer.market.alicloudapi.com'
            path = '/mobile/empty-check'
            method = 'POST'
            querys = ''
            bodys = {}
            url = host + path

            bodys['mobile_number'] = mobile_number
            post_data = urllib.parse.urlencode(bodys).encode('utf-8')
            
            request = urllib.request.Request(url, data=post_data)
            request.add_header('Authorization', 'APPCODE ' + self.appcode)
            request.add_header('Content-Type', 'application/x-www-form-urlencoded; charset=UTF-8')
            
            # SSL上下文配置
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            response = urllib.request.urlopen(request, context=ctx)
            content = response.read()
            
            if content:
                result = json.loads(content.decode('utf-8'))
                self.display_result(result)
            else:
                self.clear_result_display()
                error_label = ttk.Label(self.scrollable_frame, text="未收到响应内容", foreground="red")
                error_label.pack(anchor=tk.W, pady=5)
                
            self.status_var.set("检测完成")
            
        except Exception as e:
            self.status_var.set("检测失败")
            messagebox.showerror("请求错误", f"检测过程中发生错误:\n{str(e)}")
    
    def clear_result_display(self):
        # 清除之前的结果显示
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def display_result(self, result):
        self.clear_result_display()
        
        # 显示响应码
        if "code" in result:
            code_frame = ttk.Frame(self.scrollable_frame)
            code_frame.pack(fill=tk.X, pady=5)
            ttk.Label(code_frame, text="响应码:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(code_frame, text=result['code']).pack(side=tk.LEFT, padx=(5, 0))
        
        # 显示任务编号
        if "taskNo" in result:
            task_frame = ttk.Frame(self.scrollable_frame)
            task_frame.pack(fill=tk.X, pady=5)
            ttk.Label(task_frame, text="任务编号:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
            ttk.Label(task_frame, text=result['taskNo']).pack(side=tk.LEFT, padx=(5, 0))
            
        # 显示检测数据
        if "data" in result and result["data"]:
            data = result["data"]
            
            # 分隔线
            ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=10)
            
            # 标题
            ttk.Label(self.scrollable_frame, text="详细信息", font=("Arial", 12, "bold")).pack(anchor=tk.W)
            
            # 地区信息
            if "area" in data:
                area_frame = ttk.Frame(self.scrollable_frame)
                area_frame.pack(fill=tk.X, pady=5)
                ttk.Label(area_frame, text="地区:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(area_frame, text=data['area']).pack(side=tk.LEFT, padx=(5, 0))
                
            # 运营商信息
            if "isp" in data:
                isp_frame = ttk.Frame(self.scrollable_frame)
                isp_frame.pack(fill=tk.X, pady=5)
                ttk.Label(isp_frame, text="运营商:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(isp_frame, text=data['isp']).pack(side=tk.LEFT, padx=(5, 0))
                
            # 状态信息
            if "status" in data:
                status_frame = ttk.Frame(self.scrollable_frame)
                status_frame.pack(fill=tk.X, pady=5)
                ttk.Label(status_frame, text="状态:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
                
                status_code = data['status']
                status_info = self.status_descriptions.get(status_code, ("未知状态", "无法识别该状态码"))
                
                # 根据状态设置颜色
                color = "black"
                if status_code == "1":  # 实号
                    color = "green"
                elif status_code in ["0", "2", "4"]:  # 空号、停机、沉默号
                    color = "orange"
                elif status_code in ["3", "5"]:  # 库无、风险号
                    color = "red"
                
                status_text = f"{status_info[0]} ({status_code})"
                status_label = ttk.Label(status_frame, text=status_text, foreground=color)
                status_label.pack(side=tk.LEFT, padx=(5, 0))
                
                # 状态详细描述
                desc_frame = ttk.Frame(self.scrollable_frame)
                desc_frame.pack(fill=tk.X, pady=5)
                ttk.Label(desc_frame, text="说明:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
                desc_text = ttk.Label(desc_frame, text=status_info[1], wraplength=500, justify=tk.LEFT)
                desc_text.pack(side=tk.LEFT, padx=(5, 0))
                
            # 状态描述（如果存在且与status不同）
            if "statusMsg" in data and data.get('status') != data.get('statusMsg'):
                msg_frame = ttk.Frame(self.scrollable_frame)
                msg_frame.pack(fill=tk.X, pady=5)
                ttk.Label(msg_frame, text="状态描述:", font=("Arial", 10, "bold"), width=10, anchor=tk.W).pack(side=tk.LEFT)
                ttk.Label(msg_frame, text=data['statusMsg']).pack(side=tk.LEFT, padx=(5, 0))
        else:
            error_label = ttk.Label(self.scrollable_frame, text="未返回有效数据", foreground="red")
            error_label.pack(anchor=tk.W, pady=5)
    
    def clear_result(self):
        self.clear_result_display()
        self.status_var.set("就绪")

def main():
    root = tk.Tk()
    app = EmptyNumberDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main()