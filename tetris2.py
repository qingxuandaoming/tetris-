import tkinter as tk
from tkinter import messagebox
import random

cell_size = 30
C = 12
R = 20
height = R * cell_size
width = C * cell_size
win = tk.Tk()
canvas = tk.Canvas(win, width=width, height=height, )
canvas.pack()
block_list = []
game_is_paused = False  # 默认游戏不是暂停状态

FPS = 300  # 刷新页面的毫秒间隔

# 定义各种形状
SHAPES = {
    "O": [(-1, -1), (0, -1), (-1, 0), (0, 0)],
    "S": [(-1, 0), (0, 0), (0, -1), (1, -1)],
    "T": [(-1, 0), (0, 0), (0, -1), (1, 0)],
    "I": [(0, 1), (0, 0), (0, -1), (0, -2)],
    "L": [(-1, 0), (0, 0), (-1, -1), (-1, -2)],
    "J": [(-1, 0), (0, 0), (0, -1), (0, -2)],
    "Z": [(-1, -1), (0, -1), (0, 0), (1, 0)],
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


def increase_difficulty():
    global FPS
    FPS -= 50


def pause_game():
    global game_is_paused
    if not game_is_paused:
        game_is_paused = True
        # 更新暂停按钮的文本
        pause_button.config(text="继续")
    else:
        game_is_paused = False
        # 更新暂停按钮的文本
        pause_button.config(text="暂停")


# 绘制方块，负责生成各种方块
def draw_cell_by_cr(canva, c, r, color="#CCCCCC", tag_kind=""):
    """
    :param canva: 画板，用于绘制一个方块的Canvas对象
    :param c: 方块所在列
    :param r: 方块所在行
    :param color: 方块颜色，默认为#CCCCCC，轻灰色
    :param tag_kind: 方块的类型，用于定制绘制效果，可以是"falling"或"row"，默认为空字符串
    :return:
    """
    x0 = c * cell_size
    y0 = r * cell_size
    x1 = c * cell_size + cell_size
    y1 = r * cell_size + cell_size
    if tag_kind == "falling":
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag=tag_kind)
    elif tag_kind == "row":
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2, tag="row-%s" % r)
    else:
        canva.create_rectangle(x0, y0, x1, y1, fill=color, outline="white", width=2)


# 绘制面板, 只有在第一次绘制时才绘制背景色方块
def draw_board(canva, b, is_first=False):
    # 删掉原来所有的行
    for ri in range(R):
        canva.delete("row-%s" % ri)

    for ri in range(R):
        for ci in range(C):
            cell_type = b[ri][ci]
            if cell_type:
                draw_cell_by_cr(canva, ci, ri, shape_color[cell_type], tag_kind="row")
            elif is_first:
                draw_cell_by_cr(canva, ci, ri)


# 实际绘制生成的方块
def draw_cells(canva, c, r, cell_list, color="#CCCCCC"):
    """
    绘制指定形状指定颜色的俄罗斯方块
    :param canva: 画板
    :param r: 该形状设定的原点所在的行
    :param c: 该形状设定的原点所在的列
    :param cell_list: 该形状各个方格相对自身所处位置
    :param color: 该形状颜色
    :return:
    """
    for cell in cell_list:
        cell_c, cell_r = cell
        ci = cell_c + c
        ri = cell_r + r
        # 判断该位置方格在画板内部(画板外部的方格不再绘制)
        if 0 <= c < C and 0 <= r < R:
            draw_cell_by_cr(canva, ci, ri, color, tag_kind="falling")


# 方块移动操作前后方块的实现
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
    c, r = block['cr']
    cell_list = block['cell_list']

    # 移动前，清除原有位置绘制的俄罗斯方块
    canva.delete("falling")

    dc, dr = direction
    new_c, new_r = c + dc, r + dr
    block['cr'] = [new_c, new_r]
    # 在新位置绘制新的俄罗斯方块就好
    draw_cells(canva, new_c, new_r, cell_list, shape_color[shape_type])


# 方块生成随机函数
def generate_new_block():
    # 随机生成新的俄罗斯方块

    kind = random.choice(list(SHAPES.keys()))
    # 对应横纵坐标，以左上角为原点，水平向右为x轴正方向，
    # 竖直向下为y轴正方向，x对应横坐标，y对应纵坐标
    cr = [C // 2, 0]
    new_block = {
        'kind': kind,  # 对应俄罗斯方块的类型
        'cell_list': SHAPES[kind],
        'cr': cr
    }

    return new_block


# 水平移动的实现
def check_move(block, direction=None):
    """
        判断俄罗斯方块是否可以朝制定方向移动
        :param block: 俄罗斯方块对象
        :param direction: 俄罗斯方块移动方向
        :return: boolean 是否可以朝制定方向移动
        """
    if direction is None:
        direction = [0, 0]
    cc, cr = block['cr']
    cell_list = block['cell_list']

    for cell in cell_list:
        cell_c, cell_r = cell
        c = cell_c + cc + direction[0]
        r = cell_r + cr + direction[1]
        # 判断该位置是否超出左右边界，以及下边界
        # 一般不判断上边界，因为俄罗斯方块生成的时候，可能有一部分在上边界之上还没有出来
        if c < 0 or c >= C or r >= R:
            return False

        # 必须要判断r不小于0才行，具体原因你可以不加这个判断，试试会出现什么效果
        if r >= 0 and block_list[r][c]:
            return False

    return True


# 检查清除并实现得分
def check_and_clear():
    global score
    has_complete_row = False

    for ri, row in enumerate(block_list):
        if all(cell != '' for cell in row):
            has_complete_row = True
            # 当前行可消除
            if ri > 0:
                # 将上面所有行下移
                for cur_ri in range(ri, 0, -1):
                    block_list[cur_ri] = block_list[cur_ri - 1][:]
                block_list[0] = ['' for _ in range(C)]
            else:
                block_list[ri] = ['' for _ in range(C)]
            global score
            score += 10

    if has_complete_row:
        draw_board(canvas, block_list)

        win.title("SCORES: %s" % score)


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
        r = cell_r + cr
        # block_list 在对应位置记下其类型
        block_list[r][c] = shape_type

        draw_cell_by_cr(canvas, c, r, shape_color[shape_type], tag_kind="row")


# 左右按键调用函数
def horizontal_move_block(event):
    if event.keysym == 'Left':
        direction = [-1, 0]
    elif event.keysym == 'Right':
        direction = [1, 0]
    else:
        return

    global current_block
    if current_block is not None and check_move(current_block, direction):
        draw_block_move(canvas, current_block, direction)


# 上键调用函数
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


# 下键调用函数
def land():
    global current_block
    if current_block is None:
        return

    cell_list = current_block['cell_list']
    cc, cr = current_block['cr']
    min_height = R
    for cell in cell_list:
        cell_c, cell_r = cell
        c, r = cell_c + cc, cell_r + cr
        if r >= 0 and block_list[r][c]:
            return
        h = 0
        for ri in range(r + 1, R):
            if block_list[ri][c]:
                break
            else:
                h += 1
        if h < min_height:
            min_height = h

    down = [0, min_height]
    if check_move(current_block, down):
        draw_block_move(canvas, current_block, down)


# 主函数进程，自动下落效果的实现，计时器实现
def game_loop():
    win.update()
    if not game_is_paused:
        global current_block
        if current_block is None:
            new_block = generate_new_block()
            # 新生成的俄罗斯方块需要先在生成位置绘制出来
            draw_block_move(canvas, new_block)
            current_block = new_block
            if not check_move(current_block, [0, 0]):
                messagebox.showinfo("Game Over!", "Your Score is %s" % score)
                win.destroy()
                return
        else:
            if check_move(current_block, [0, 1]):
                draw_block_move(canvas, current_block, [0, 1])
            else:
                # 无法移动，记入 block_list 中
                save_block_to_list(current_block)
                current_block = None
                check_and_clear()

    win.after(FPS, game_loop)


canvas.focus_set()  # 聚焦到canvas画板对象上
canvas.bind("<KeyPress-Left>", lambda event: horizontal_move_block(event))
canvas.bind("<KeyPress-Right>", lambda event: horizontal_move_block(event))
canvas.bind("<KeyPress-Up>", lambda event: rotate_block())
canvas.bind("<KeyPress-Down>", lambda event: land())
current_block = None  # 初始默认不存在移动的方块

# 创建开始游戏的按钮，并且当按下时调用 start_game 函数
start_button = tk.Button(win, text="开始游戏", command=game_loop)
start_button.pack(side=tk.LEFT, padx=10, pady=10)
difficulty_button = tk.Button(win, text="增加难度", command=increase_difficulty)
difficulty_button.pack(side=tk.RIGHT, padx=10, pady=10)
pause_button = tk.Button(win, text="暂停", command=pause_game)
pause_button.pack(side=tk.BOTTOM, padx=10, pady=10)

for i in range(R):
    i_row = ['' for j in range(C)]
    block_list.append(i_row)

draw_board(canvas, block_list, True)

score = 0
win.title("SCORES: %s" % score)  # 标题中展示分数
win.update()
# win.after(FPS, game_loop)  # 在FPS 毫秒后调用 game_loop方法

win.mainloop()