import tkinter as tk
from tkinter import ttk, messagebox
import menu
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import matplotlib as mpl
from matplotlib.ticker import MaxNLocator

# 设置matplotlib的字体为支持中文的字体
mpl.rcParams['font.sans-serif'] = ['SimHei']  # 使用黑体
mpl.rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

def SortShow(data):
    # 清除现有内容
    sort_toplevel = tk.Toplevel()
    sort_toplevel.title("学生排名图")
    center_window(sort_toplevel, 800, 550)

    # 读取数据模型
    id2name, id2sortList, xaxis = data_model(data)
    # 初始化界面
    header_frame, plot_frame = init_sort_win(sort_toplevel, id2name, id2sortList, xaxis)

    # 检索展示折线图
    sort_toplevel.mainloop()

def init_sort_win(sort_toplevel, id2name, id2sortList, xaxis):
    # 创建框架
    header_frame = ttk.Frame(sort_toplevel, padding="10")
    header_frame.pack(fill=tk.X)

    plot_frame = ttk.Frame(sort_toplevel, padding=(10, 0, 10, 10))
    plot_frame.pack(fill=tk.BOTH, expand=True)

    selected_students = []
    def on_plot_button_click():
        selected_students.clear()
        selected_students.extend(show_multiselect_dialog(sort_toplevel, id2name))
        if len(selected_students) != 0:
            echarts_show(xaxis, id2name, id2sortList, selected_students, plot_frame)
        else:
            messagebox.showwarning("提示", "至少选择一个学生")

    def export_all_sort_pic():
        pass

    def export_selected_sort_pic():
        if len(selected_students) == 0:
            messagebox.showwarning("提示", "请先选择学生")
        else:
            print(selected_students)

    # 在最上面中间位置添加一个按钮
    plot_button = ttk.Button(header_frame, text="选择学生", command=on_plot_button_click)
    plot_button.pack(side=tk.LEFT, expand=True, padx=5, pady=10)
    plot_button = ttk.Button(header_frame, text="所有学生名次图", command=export_all_sort_pic)
    plot_button.pack(side=tk.LEFT, expand=True, padx=5, pady=10)
    plot_button = ttk.Button(header_frame, text="选中学生名次图", command=export_selected_sort_pic)
    plot_button.pack(side=tk.LEFT, expand=True, padx=5, pady=10)

    return header_frame, plot_frame

def show_multiselect_dialog(root, id2name):
    selected_students = []
    def on_select():
        nonlocal selected_students
        selected_students = [student for student, var in checkboxes.items() if var.get()]
        dialog.destroy()

    dialog = tk.Toplevel()
    dialog.title("选择学生")
    dia_size = center_select_dialog(dialog, 300, 300)
    dialog.geometry(dia_size)

    # 创建一个 Canvas 并添加滚动条
    canvas = tk.Canvas(dialog)
    scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    # 鼠标滚轮事件处理
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)


    checkboxes = {}
    for student_id, name in id2name.items():
        var = tk.BooleanVar()
        cb = ttk.Checkbutton(scrollable_frame, text=f"{name} ({student_id})", variable=var)
        cb.pack(anchor=tk.W)
        checkboxes[student_id] = var

    ok_button = ttk.Button(dialog, text="确定", command=on_select)
    ok_button.pack(pady=10)

    # 布局
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    dialog.transient(root)  # 使对话框保持在主窗口之上
    dialog.grab_set()  # 抓取焦点
    root.wait_window(dialog)  # 等待对话框关闭

    return selected_students

# 统计表格中的数据模式
def data_model(data):
    id2name = {}
    id2sortList = {}
    xaxis = []
    for index, row in data.iterrows():
        # 选出列名
        if '学号'==row.values[0]:
            for col_index, column in enumerate(data.columns):
                if col_index < 2:
                    continue
                xaxis.append(row[column])
            continue
        # 过滤掉不是学号的列
        if not isinstance(row.values[0], int):
            continue
        # 统计学号和姓名的关系
        id2name[row.values[0]] = row.values[1]
        # 统计该学生的学号和所有单元的排名
        sort_list = []
        for col_index, column in enumerate(data.columns):
            # 过滤掉 学号和姓名
            if col_index < 2:
                continue
            value = row[column]
            if not isinstance(value, int):
                sort_list.append(None)
            else:
                sort_list.append(value)
        id2sortList[row.values[0]] = sort_list
    return id2name, id2sortList, xaxis

# 检索展示成绩排名
def echarts_show(xaxis, id2name, id2sortList, selected_students, plot_frame):
    # 清除plot_frame中的现有内容
    for widget in plot_frame.winfo_children():
        widget.destroy()

    # 创建一个Figure对象
    fig = Figure(figsize=(8, 4), dpi=100)

    # 添加一个子图
    ax = fig.add_subplot(111)

    # 设置x轴标签
    ax.set_xlabel('单元')
    ax.set_ylabel('排名')
    ax.set_title('学生排名图')
    ax.set_xticks(np.arange(len(xaxis)))
    ax.set_xticklabels(xaxis, rotation=45, ha='right')
    # 设置y轴刻度为整数
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    # 添加栅格
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, color='gray')  # 启用网格线，并设置样式

    # 为每个选定的学生绘制折线图
    for student_id in selected_students:
        name = id2name[student_id]
        sort_list = id2sortList[student_id]
        y_values = [y if y is not None else np.nan for y in sort_list]  # 处理None值
        ax.plot(y_values, label=name, marker='o')

    # 添加图例
    ax.legend()

    # 创建一个FigureCanvasTkAgg对象
    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()

    # 将canvas放置到frame中
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def center_window(root, width, height):
    # 获取屏幕尺寸
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    # 计算窗口的开始位置
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    # 设置窗口的位置
    root.geometry(f"{width}x{height}+{int(x)}+{int(y)}")
    # 创建一个菜单栏
    menu.create_menu(root)

def center_select_dialog(master, width, height):
    # 获取屏幕尺寸
    screen_width = master.winfo_screenwidth()
    screen_height = master.winfo_screenheight()
    # 计算窗口的开始位置
    x = (screen_width - width) / 2
    y = (screen_height - height) / 2
    return f"{width}x{height}+{int(x)}+{int(y)}"