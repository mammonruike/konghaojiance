import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import urllib.request
import urllib.parse
import ssl
import json
import os
from datetime import datetime

class EmptyNumberDetector:
    def __init__(self, root):
        # 内嵌AppCode
        self.appcode = '您的阿里云密钥'
        
        self.root = root
        self.root.title("玛门睿科科技空号检测程序")
        self.root.geometry("700x600")
        self.root.resizable(True, True)
        
        # 存储批量检测结果用于导出
        self.batch_results = []
        
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
        
        # 文件上传区域
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="号码文件:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.file_path_var = tk.StringVar()
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, state='readonly')
        self.file_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 5))
        
        self.browse_button = ttk.Button(file_frame, text="浏览...", command=self.browse_file)
        self.browse_button.grid(row=0, column=2, pady=5, padx=(0, 5))
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        # 检测按钮
        self.detect_single_button = ttk.Button(button_frame, text="检测号码", command=self.detect_single_number)
        self.detect_single_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.detect_batch_button = ttk.Button(button_frame, text="批量检测", command=self.detect_batch_numbers)
        self.detect_batch_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 导出按钮
        self.export_button = ttk.Button(button_frame, text="导出实号", command=self.export_real_numbers, state=tk.DISABLED)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空按钮
        self.clear_button = ttk.Button(button_frame, text="清空结果", command=self.clear_result)
        self.clear_button.pack(side=tk.LEFT)
        
        # 结果显示区域框架
        result_frame = ttk.LabelFrame(main_frame, text="检测结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
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
        
    def browse_file(self):
        """浏览并选择号码文件"""
        file_path = filedialog.askopenfilename(
            title="选择号码文件",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.file_path_var.set(file_path)
    
    def detect_single_number(self):
        """检测单个号码"""
        mobile_number = self.mobile_var.get().strip()
        
        if not mobile_number:
            messagebox.showerror("错误", "请输入手机号码")
            return
            
        self.status_var.set("正在检测...")
        self.root.update()
        
        try:
            result = self.call_api(mobile_number)
            self.display_result(result)
            self.status_var.set("检测完成")
            
        except Exception as e:
            self.status_var.set("检测失败")
            messagebox.showerror("请求错误", f"检测过程中发生错误:\n{str(e)}")
    
    def detect_batch_numbers(self):
        """批量检测文件中的号码"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("错误", "请选择号码文件")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                numbers = [line.strip() for line in f.readlines() if line.strip()]
                
            if not numbers:
                messagebox.showerror("错误", "文件中没有找到有效的号码")
                return
                
            self.status_var.set(f"开始批量检测 {len(numbers)} 个号码...")
            self.root.update()
            
            # 清空之前的显示结果和存储的批量结果
            self.clear_result_display()
            self.batch_results = []
            self.export_button.config(state=tk.DISABLED)  # 禁用导出按钮直到检测完成
            
            # 逐个检测号码
            for i, number in enumerate(numbers):
                self.status_var.set(f"正在检测 ({i+1}/{len(numbers)}): {number}")
                self.root.update()
                
                try:
                    result = self.call_api(number)
                    self.display_batch_result(number, result)
                    # 保存结果用于导出
                    self.batch_results.append((number, result))
                except Exception as e:
                    # 显示错误信息
                    error_frame = ttk.Frame(self.scrollable_frame)
                    error_frame.pack(fill=tk.X, pady=2)
                    ttk.Label(error_frame, text=f"{number}:", foreground="red").pack(side=tk.LEFT)
                    ttk.Label(error_frame, text=f"错误: {str(e)}", foreground="red").pack(side=tk.LEFT, padx=(5, 0))
                    # 保存错误结果用于导出
                    self.batch_results.append((number, {"error": str(e)}))
                    
                # 添加分隔线
                ttk.Separator(self.scrollable_frame, orient='horizontal').pack(fill=tk.X, pady=5)
                
            # 启用导出按钮
            self.export_button.config(state=tk.NORMAL)
            self.status_var.set(f"批量检测完成，共检测 {len(numbers)} 个号码")
            
        except Exception as e:
            self.status_var.set("批量检测失败")
            messagebox.showerror("文件错误", f"读取文件时发生错误:\n{str(e)}")
    
    def export_real_numbers(self):
        """导出实号号码到TXT文件（只导出状态为1的号码）"""
        if not self.batch_results:
            messagebox.showerror("错误", "没有可导出的结果")
            return
            
        # 过滤出实号（状态为1）的号码
        real_numbers = []
        for number, result in self.batch_results:
            # 检查是否有有效数据且状态为1（实号）
            if ("data" in result and result["data"] and 
                "status" in result["data"] and result["data"]["status"] == "1"):
                real_numbers.append((number, "实号"))
        
        if not real_numbers:
            messagebox.showerror("错误", "没有找到实号号码")
            return
            
        # 让用户选择保存位置和文件名
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="保存实号号码",
            initialfile=f"实号号码_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        )
        
        if not file_path:
            return  # 用户取消了保存操作
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入标题
                f.write("实号号码列表\n")
                f.write("=" * 30 + "\n")
                f.write(f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"实号数量: {len(real_numbers)}\n\n")
                
                # 写入实号号码，格式为：电话号码+状态
                for number, status in real_numbers:
                    f.write(f"{number}\n")
                    
            messagebox.showinfo("导出成功", f"实号号码已成功导出到:\n{file_path}\n共导出 {len(real_numbers)} 个实号")
            self.status_var.set("实号导出完成")
            
        except Exception as e:
            self.status_var.set("导出失败")
            messagebox.showerror("导出错误", f"导出实号时发生错误:\n{str(e)}")
    
    def call_api(self, mobile_number):
        """调用空号检测API"""
        host = 'https://juweer.market.alicloudapi.com'
        path = '/mobile/empty-check'
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
            return json.loads(content.decode('utf-8'))
        else:
            raise Exception("未收到响应内容")
    
    def clear_result_display(self):
        """清除结果显示"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
    
    def display_result(self, result):
        """显示单个号码检测结果"""
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
    
    def display_batch_result(self, number, result):
        """显示批量检测结果"""
        # 号码标题
        title_frame = ttk.Frame(self.scrollable_frame)
        title_frame.pack(fill=tk.X, pady=2)
        ttk.Label(title_frame, text=number, font=("Arial", 10, "bold")).pack(side=tk.LEFT)
        
        # 显示检测数据
        if "data" in result and result["data"]:
            data = result["data"]
            
            if "status" in data:
                status_code = data['status']
                status_info = self.status_descriptions.get(status_code, ("未知状态", ""))
                
                # 根据状态设置颜色
                color = "black"
                if status_code == "1":  # 实号
                    color = "green"
                elif status_code in ["0", "2", "4"]:  # 空号、停机、沉默号
                    color = "orange"
                elif status_code in ["3", "5"]:  # 库无、风险号
                    color = "red"
                
                status_text = f"{status_info[0]} ({status_code})"
                status_label = ttk.Label(title_frame, text=status_text, foreground=color)
                status_label.pack(side=tk.RIGHT)
                
                # 显示地区和运营商（简化显示）
                info_text = ""
                if "area" in data:
                    info_text += f"地区: {data['area']} "
                if "isp" in data:
                    info_text += f"运营商: {data['isp']}"
                    
                if info_text:
                    info_label = ttk.Label(self.scrollable_frame, text=info_text, font=("Arial", 9))
                    info_label.pack(anchor=tk.W, padx=(20, 0))
        else:
            error_label = ttk.Label(self.scrollable_frame, text="未返回有效数据", foreground="red")
            error_label.pack(anchor=tk.W, padx=(20, 0))
    
    def clear_result(self):
        self.clear_result_display()
        self.batch_results = []  # 清空存储的批量结果
        self.export_button.config(state=tk.DISABLED)  # 禁用导出按钮
        self.status_var.set("就绪")

def main():
    root = tk.Tk()
    app = EmptyNumberDetector(root)
    root.mainloop()

if __name__ == "__main__":
    main()