import random
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.title("俄罗斯方块")
cell_size = 30  # 定义单元格大小，单位是像素(pixels)
Y = 20  # 行
C = 14  # 列
height = Y * cell_size
width = C * cell_size
score = 0
root.title("SCORES: %s" % score)  # 标题中展示分数
canvas = tk.Canvas(root, width=width, height=height, )
canvas.pack()

block_list = []
for i in range(Y):
    i_row = ['' for _ in range(C)]
    block_list.append(i_row)


FPS = 400  # 刷新页面的毫秒间隔，间隔越大越容易

# 定义各种形状
SHAPES = {
    "O": [(-1, -1), (0, -1), (-1, 0), (0, 0)],   # 四方块
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],    # 闪电块
    "T": [(-1, 0), (0, 0), (0, -1), (1, 0)],     # 土字块
    "I": [(0, 1), (0, 0), (0, -1), (0, -2)],     # 一字块
    "L": [(-1, 0), (0, 0), (-1, -1), (-1, -2)],  # L形块
    "J": [(-1, 0), (0, 0), (0, -1), (0, -2)],    # 另一个颜色的L形块
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],    # 另一个颜色的闪电块
}

# 定义各种形状的颜色
shape_color = {
    "O": "blue",
    "S": "red",
    "T": "yellow",
    "I": "green",
    "L": "purple",
    "J": "orange",
    "Z": "Cyan",
}


'''class Button:
    def __init__(self, x, y, width, height, text):
        # 初始化按钮相关内容
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        # ...
'''


# 绘制游戏面板, 只有在第一次绘制时才绘制背景色方块
def draw_board(canva, block_l, is_first=False):
    # 删掉原来所有的行
    for ri in range(Y):
        canva.delete("row-%s" % ri)

    for ri in range(Y):
        for ci in range(C):
            cell_type = block_l[ri][ci]
            if cell_type:
                draw_cell_by_cr(canva, ci, ri, shape_color[cell_type], tag_kind="row")
            elif is_first:
                draw_cell_by_cr(canva, ci, ri)


# 游戏主循环的实现，负责更新游戏状态并循环执行游戏逻辑
def main():
    global root
    global current_block
    global canvas

    root.update()

    # canva.pack()
    if current_block is None:
        new_block = generate_new_block()
        # 新生成的俄罗斯方块需要先在生成位置绘制出来
        draw_block_move(canvas, new_block)
        current_block = new_block
        if not check_move(current_block, [0, 0]):
            messagebox.showinfo("Game Over!", "Your Score is %s" % score)
            root.destroy()
            return

    else:
        if check_move(current_block, [0, 1]):
            draw_block_move(canvas, current_block, [0, 1])
        else:
            # 无法移动，记入 block_l 中
            save_block_to_list(current_block)
            current_block = None
            check_and_clear()
    root.after(FPS, main)


# 这个函数可以增加难度级别
def increase_difficulty():
    print("增加难度！")
    # 这里可以放置控制游戏难度的代码


# 绘制方块的函数
def draw_cell_by_cr(canva, c, y, color="#CCCCCC", tag_kind: object = ""):
    """
    :param canva: 画板，用于绘制一个方块的Canvas对象
    :param c: 方块所在列
    :param y: 方块所在行
    :param color: 方块颜色，默认为#CCCCCC，轻灰色
    :param tag_kind: 方块的类型，用于定制绘制效果，可以是"falling"或"row"，默认为空字符串
    :return:
    """
    x0 = c * cell_size
    y0 = y * cell_size
    x1 = c * cell_size + cell_size
    y1 = y * cell_size + cell_size
    if tag_kind == "falling":
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag=tag_kind)
    elif tag_kind == "row":
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag="row-%s" % y)
    else:
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2)


# 下落效果的实现
def draw_cells(canva, c, y, cell_list, color="#CCCCCC"):
    # docstring 描述，用以明晰参数的含义
    """
    绘制指定形状指定颜色的俄罗斯方块
    :param canva: 画板
    :param y: 该形状设定的原点所在的行
    :param c: 该形状设定的原点所在的列
    :param cell_list: 该形状各个方格相对自身所处位置
    :param color: 该形状颜色
    :return:
    """
    for cell in cell_list:
        cell_c, cell_r = cell
        ci = cell_c + c
        ri = cell_r + y
        # 判断该位置方格在画板内部(画板外部的方格不再绘制)
        if 0 <= c < C and 0 <= y < Y:
            draw_cell_by_cr(canva, ci, ri, color, tag_kind="falling")


# 左右移动
def draw_block_move(canva, block, direction=None):
    """
    绘制向指定方向移动后的俄罗斯方块
    :param canva: 画板
    :param block: 俄罗斯方块对象
    :param direction: 俄罗斯方块移动方向
    :return:
    """
    if direction is None:
        direction = [0, 0]
    shape_type = block['kind']
    c, y = block['cr']
    cell_list = block['cell_list']

    # 移动前，清除原有位置绘制的俄罗斯方块
    canva.delete("falling")

    dc, dr = direction
    new_c, new_r = c + dc, y + dr
    block['cr'] = [new_c, new_r]
    # 在新位置绘制新的俄罗斯方块就好
    draw_cells(canva, new_c, new_r, cell_list, shape_color[shape_type])


# 随机生成新的俄罗斯方块
def generate_new_block():
    kind = random.choice(list(SHAPES.keys()))
    cr = [C // 2, 0]
    new_block = {
        'kind': kind,  # 对应俄罗斯方块的类型
        'cell_list': SHAPES[kind],
        'cr': cr
    }

    return new_block


# 检查移动是否可行
def check_move(block: object, direction: object = None) -> object:
    """
        判断俄罗斯方块是否可以朝制定方向移动
        :param block: 俄罗斯方块对象
        :param direction: 俄罗斯方块移动方向
        :return: boolean 是否可以朝制定方向移动
    """
    if not block:
        return
    if direction is None:
        direction = [0, 0]
    cc, cr = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_c, cell_r = cell
        c = cell_c + cc + direction[0]
        y = cell_r + cr + direction[1]
        # 判断该位置是否超出左右边界，以及下边界
        # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
        if c < 0 or c >= C or y >= Y:
            return False

        # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
        if y >= 0 and block_list[y][c]:
            return False

    return True


# 检查是否有可以消掉的得分行
def check_row_complete(row):
    for cell in row:
        if cell == '':
            return False
    return True


# 消除与得分功能的实现
def check_and_clear():
    global score
    has_complete_row = False
    for ri in range(len(block_list)):
        if check_row_complete(block_list[ri]):
            has_complete_row = True
            # 当前行可消除
            if ri > 0:
                for cur_ri in range(ri, 0, -1):
                    block_list[cur_ri] = block_list[cur_ri - 1][:]
                block_list[0] = ['' for _ in range(C)]  # 对于无需返回值的遍历中的迭代变量可以使用_表示
            else:
                block_list[ri] = ['' for _ in range(C)]
            score += 10

    if has_complete_row:
        draw_board(canvas, block_list)
        root.title("SCORES: %s" % score)  # 得分显示


# 避免重叠现象，实现方块固定
def save_block_to_list(block):
    # 清除原有的打上了 falling 标签的方块
    canvas.delete("falling")

    shape_type = block['kind']
    cc, cr = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_c, cell_r = cell
        c = cell_c + cc
        y = cell_r + cr
        # block_l 在对应位置记下其类型
        block_list[y][c] = shape_type

        draw_cell_by_cr(canvas, c, y, shape_color[shape_type], tag_kind="row")


# 水平移动操作指令输入的逻辑处理
def horizontal_move_block(event):
    if event.keysym == 'Left':  # 左移键操作
        direction = [-1, 0]
    elif event.keysym == 'Right':  # 右移键操作
        direction = [1, 0]
    else:
        return

    global current_block
    if current_block is not None and check_move(current_block, direction):
        draw_block_move(canvas, current_block, direction)  # 平移实现调用


# 旋转功能
def rotate_block():
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    rotate_list = []
    for cell in cell_list:
        cell_c, cell_r = cell
        rotate_cell = [cell_r, -cell_c]
        rotate_list.append(rotate_cell)

    block_after_rotate = {
        'kind': current_block['kind'],  # 对应俄罗斯方块的类型
        'cell_list': rotate_list,
        'cr': current_block['cr']
    }

    if check_move(block_after_rotate):
        cc, cr = current_block['cr']
        draw_cells(canvas, cc, cr, current_block['cell_list'])
        draw_cells(canvas, cc, cr, rotate_list, shape_color[current_block['kind']])
        current_block = block_after_rotate


# 快速下落
def land():
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    cc, cr = current_block['cr']
    min_height = Y
    for cell in cell_list:
        cell_c, cell_r = cell
        c, y = cell_c + cc, cell_r + cr
        if y >= 0 and block_list[y][c]:
            return
        h = 0
        for ri in range(y + 1, Y):
            if block_list[ri][c]:
                break
            else:
                h += 1
        if h < min_height:
            min_height = h

    down = [0, min_height]
    if check_move(current_block, down):
        draw_block_move(canvas, current_block, down)  # 左右移动调用

    root.after(FPS, main)  # 在FPS 毫秒后调用 main方法


# 按键操作的功能键调用
canvas.focus_set()  # 聚焦到canvas画板对象上
canvas.bind("<KeyPress-Left>", lambda event: horizontal_move_block(event))
canvas.bind("<KeyPress-Right>", lambda event: horizontal_move_block(event))
canvas.bind("<KeyPress-Up>", lambda event: rotate_block())
canvas.bind("<KeyPress-Down>", lambda event: land())

draw_board(canvas, block_list, True)
current_block = None  # 正在下落的方块

# 创建开始游戏的按钮，并且当按下时调用 start_game 函数
start_button = tk.Button(root, text="开始游戏", command=main)
start_button.pack(side=tk.LEFT, padx=10, pady=10)
difficulty_button = tk.Button(root, text="增加难度", command=increase_difficulty)
difficulty_button.pack(side=tk.RIGHT, padx=10, pady=10)
# pause_button = tk.Button(game_frame, text="暂停", command=pause_game)
# pause_button.pack(side=tk.RIGHT, padx=10, pady=10)

root.update()  # root.update() 的调用可以强制更新窗口，确保最新的游戏画面能够及时渲染出来
root.mainloop()  # 启动 tkinter 的事件循环
