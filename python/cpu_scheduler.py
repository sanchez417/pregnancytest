import math
import random
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

# =====================================================================
#  CORE DATA & LOGIC  (unchanged scheduling logic)
# =====================================================================
class Process:
    def __init__(self, pid, arrival_time, burst_time, priority, order):
        self.pid = pid
        self.at = arrival_time
        self.bt = burst_time
        self.priority = priority
        self.order = order
        self.remaining_time = burst_time
        self.ct = 0
        self.tat = 0
        self.wt = 0
        self.rt = 0

    def calculate_metrics(self, first_start_time):
        self.tat = self.ct - self.at
        self.wt = self.tat - self.bt
        self.rt = first_start_time - self.at


def copy_processes(proc_list):
    return [Process(p.pid, p.at, p.bt, p.priority, p.order) for p in proc_list]


def add_segment(timeline, start, end, pid):
    if end <= start:
        return
    if timeline and timeline[-1][2] == pid and timeline[-1][1] == start:
        timeline[-1] = (timeline[-1][0], end, pid)
    else:
        timeline.append((start, end, pid))



TEAL = "#a0d9d0"
TEAL_DARK = "#7fc4b9"
BLUE = "#9bdcff"
BLUE_DARK = "#6cb8e6"
CREAM = "#fff8f0"
CREAM_ALT = "#f3ebe0"
SLATE = "#6b7d77"
INK = "#3b4a45"
OUTLINE = "#5d6e68"
SHADOW = "#6b7d77"
CORAL = "#f58585"
GRID = "#b6e5f2"

BTN_GREEN = "#6bcb77"
BTN_CORAL = "#f58585"
BTN_BLUE = "#5aa9e6"
BTN_PURPLE = "#b983ff"
BTN_YELLOW = "#ffd166"
BTN_ORANGE = "#ff9f45"

# one colour per process (like "thread colours" in a CPU trace)
PALETTE = ["#4D96FF", "#FF6B6B", "#6BCB77", "#FFD93D", "#B983FF",
           "#FF9F45", "#2EC4B6", "#F78FB3", "#7A8CFF", "#A3C644"]
IDLE_COLOR = "#cfd8d5"

STATUS_COLORS = {"Ready": "#2e9e5b", "Running": "#e67e22",
                 "Paused": "#b58900", "Complete": "#2980b9"}

ALGOS = ["FCFS", "SJF (Non-Preemptive)", "SRTF (Preemptive)",
         "Priority (Non-Preemptive)", "Priority (Preemptive)"]

# (full name, tab label, colour, badge, title, description)
ALGO_TABS = [
    ("FCFS", "FCFS", "#6bcb77", "NON-PREEMPTIVE",
     "FCFS  -  First-Come, First-Served",
     "Processes are served strictly in the order they arrive, like a queue at a counter. "
     "Once a process gets the CPU it keeps it until it finishes."),
    ("SJF (Non-Preemptive)", "SJF", "#5aa9e6", "NON-PREEMPTIVE",
     "SJF  -  Shortest Job First",
     "When the CPU becomes free, the arrived process with the smallest burst time is chosen. "
     "It then runs to completion without interruption."),
    ("SRTF (Preemptive)", "SRTF", "#b983ff", "PREEMPTIVE",
     "SRTF  -  Shortest Remaining Time First",
     "The preemptive version of SJF. Every time unit the CPU goes to the process with the "
     "least time left, so a shorter newcomer can interrupt the running one."),
    ("Priority (Non-Preemptive)", "PRIORITY (NP)", "#ffd166", "NON-PREEMPTIVE",
     "Priority Scheduling  -  Non-Preemptive",
     "Each process has a priority number (lower number = more important). When the CPU is free, "
     "the most important ready process runs until it finishes."),
    ("Priority (Preemptive)", "PRIORITY (P)", "#ff9f45", "PREEMPTIVE",
     "Priority Scheduling  -  Preemptive",
     "Same rule, but re-checked every time unit: a newly arrived higher-priority process "
     "immediately takes the CPU away from the running one."),
]

FONTS = {}
FRAME_MS = 33  # animation frame time (~30 fps)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, t):
    a, b = hex_to_rgb(c1), hex_to_rgb(c2)
    return "#%02x%02x%02x" % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def lighten(c, t=0.25):
    return mix(c, "#ffffff", t)


def text_color_for(c):
    r, g, b = hex_to_rgb(c)
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) > 150 else "white"


def pick_font(root, prefs):
    avail = set(tkfont.families(root))
    for f in prefs:
        if f in avail:
            return f
    return "Helvetica"


def init_fonts(root):
    heavy = pick_font(root, ["Segoe UI Black", "Arial Black", "Impact", "DejaVu Sans", "Helvetica"])
    body = pick_font(root, ["Segoe UI", "Calibri", "Helvetica", "DejaVu Sans", "Arial"])
    mono = pick_font(root, ["Consolas", "Courier New", "DejaVu Sans Mono", "Courier"])
    w = "normal" if heavy in ("Segoe UI Black", "Arial Black", "Impact") else "bold"
    FONTS.update(
        title=(heavy, 18, w), head=(heavy, 11, w), btn=(heavy, 9, w),
        chip=(heavy, 15, w), chips=(heavy, 8, w),
        body=(body, 10), bodyb=(body, 10, "bold"), small=(body, 9),
        mono=(mono, 11, "bold"), monos=(mono, 9, "bold"),
    )


# =====================================================================
#  CUSTOM WIDGETS
# =====================================================================
class RetroButton(tk.Canvas):
    """Chunky 3D button: hard drop-shadow, lifts on hover, sinks when pressed."""
    DEPTH = 4

    def __init__(self, parent, text, command, color, width=110, height=34, fg=INK):
        d = self.DEPTH
        super().__init__(parent, width=width + d, height=height + d, bg=parent.cget("bg"),
                         highlightthickness=0, bd=0, cursor="hand2")
        self.command, self.color, self.full_color = command, color, color
        self.w, self.h, self.fg, self.text = width, height, fg, text
        self.pressed = False
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<ButtonRelease-1>", self._release)
        self._draw()

    def _draw(self):
        d, w, h = self.DEPTH, self.w, self.h
        self.delete("all")
        self.pressed = False
        self.create_rectangle(d + 1, d + 1, w + d, h + d, fill=SHADOW, outline=OUTLINE)
        self.face = self.create_rectangle(1, 1, w, h, fill=self.color, outline=OUTLINE,
                                          width=2, tags="top")
        self.shine = self.create_rectangle(4, 4, w - 3, h // 2, fill=lighten(self.color, .35),
                                           outline="", tags="top")
        self.label = self.create_text(w // 2, h // 2, text=self.text, font=FONTS["btn"],
                                      fill=self.fg, tags="top")

    def resize(self, width):
        self.w = width
        self.configure(width=width + self.DEPTH)
        self._draw()

    def set_text(self, text):
        self.text = text
        self.itemconfig(self.label, text=text)

    def set_active(self, on):
        """Tab behaviour: active = full colour, inactive = pale."""
        self.color = self.full_color if on else mix(self.full_color, "#ffffff", .68)
        self.itemconfig(self.face, fill=self.color)
        self.itemconfig(self.shine, fill=lighten(self.color, .35))

    def _enter(self, _):
        self.itemconfig(self.face, fill=lighten(self.color, .22))
        self.itemconfig(self.shine, fill=lighten(self.color, .5))

    def _leave(self, _):
        self.itemconfig(self.face, fill=self.color)
        self.itemconfig(self.shine, fill=lighten(self.color, .35))
        if self.pressed:
            self.move("top", -(self.DEPTH - 1), -(self.DEPTH - 1))
            self.pressed = False

    def _press(self, _):
        if not self.pressed:
            self.move("top", self.DEPTH - 1, self.DEPTH - 1)
            self.pressed = True

    def _release(self, e):
        if self.pressed:
            self.move("top", -(self.DEPTH - 1), -(self.DEPTH - 1))
            self.pressed = False
            if 0 <= e.x <= self.w + self.DEPTH and 0 <= e.y <= self.h + self.DEPTH:
                self.command()


class RetroSlider(tk.Canvas):
    """Draggable 3D slider that stretches to fill the space it is given."""

    def __init__(self, parent, variable, lo=1, hi=12, command=None, height=34):
        super().__init__(parent, height=height, bg=parent.cget("bg"), highlightthickness=0,
                         cursor="hand2")
        self.var, self.lo, self.hi, self.command, self.hgt = variable, lo, hi, command, height
        self.bind("<Configure>", lambda _e: self.draw())
        self.bind("<Button-1>", self._set)
        self.bind("<B1-Motion>", self._set)
        self.var.trace_add("write", lambda *_a: self.draw())

    def _set(self, e):
        w = max(self.winfo_width() - 32, 1)
        frac = min(1.0, max(0.0, (e.x - 16) / w))
        v = round(self.lo + frac * (self.hi - self.lo))
        if v != self.var.get():
            self.var.set(v)
            if self.command:
                self.command(v)

    def draw(self):
        self.delete("all")
        w = self.winfo_width()
        if w < 60:
            return
        cy = self.hgt // 2
        span = w - 32
        x = 16 + span * (self.var.get() - self.lo) / (self.hi - self.lo)
        self.create_rectangle(18, cy - 3, w - 14, cy + 5, fill=SHADOW, outline=SHADOW)
        self.create_rectangle(16, cy - 5, w - 16, cy + 3, fill="white", outline=OUTLINE, width=2)
        self.create_rectangle(17, cy - 4, x, cy + 2, fill=BTN_GREEN, outline="")
        for v in range(self.lo, self.hi + 1):
            tx = 16 + span * (v - self.lo) / (self.hi - self.lo)
            self.create_line(tx, cy + 9, tx, cy + 13, fill=SLATE, width=2)
        self.create_rectangle(x - 6, cy - 11, x + 12, cy + 13, fill=SHADOW, outline=SHADOW)
        self.create_rectangle(x - 9, cy - 14, x + 9, cy + 10, fill=CORAL, outline=OUTLINE, width=2)
        self.create_rectangle(x - 6, cy - 11, x + 6, cy - 4, fill=lighten(CORAL, .4), outline="")
        for gx in (x - 2, x + 2):
            self.create_line(gx, cy - 2, gx, cy + 6, fill=OUTLINE, width=1)


SCROLLERS = []


class ScrollFrame(tk.Frame):
    """Vertically scrollable area. Put widgets in `.inner`; mouse wheel scrolls it."""

    def __init__(self, parent, min_height=120, bg=CREAM):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, height=min_height,
                                yscrollincrement=24)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview,
                                 style="Retro.Vertical.TScrollbar")
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda _e: self._sync())
        self.canvas.bind("<Configure>", lambda _e: self._sync())
        SCROLLERS.append(self)

    def _sync(self):
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        h = max(ch, self.inner.winfo_reqheight())  # fill the view when content is shorter
        self.canvas.itemconfigure(self.win, width=cw, height=h)
        self.canvas.configure(scrollregion=(0, 0, cw, h))


SH = 6  # window drop-shadow offset


def retro_window(parent, title, icon="", behind=TEAL, scroll=False, min_height=120):
    """Retro OS-style window: blue frame, title bar with 3 dots, cream body, hard shadow."""
    wrapper = tk.Frame(parent, bg=behind)
    shadow = tk.Frame(wrapper, bg=SHADOW)
    shadow.place(x=SH, y=SH, relwidth=1, relheight=1, width=-SH, height=-SH)
    win = tk.Frame(wrapper, bg=BLUE, highlightbackground=OUTLINE, highlightthickness=2)
    win.pack(fill="both", expand=True, padx=(0, SH), pady=(0, SH))

    bar = tk.Frame(win, bg=BLUE)
    bar.pack(fill="x")
    tk.Label(bar, text=f"{icon} {title}".strip(), bg=BLUE, fg=INK, font=FONTS["head"],
             anchor="w").pack(side="left", padx=8, pady=3)
    dots = tk.Canvas(bar, width=66, height=22, bg=BLUE, highlightthickness=0)
    dots.pack(side="right", padx=8)
    for i, col in enumerate((CORAL, CORAL, SLATE)):
        dots.create_oval(2 + i * 21, 3, 18 + i * 21, 19, fill=col, outline=OUTLINE, width=2)

    inner = tk.Frame(win, bg=BLUE)
    inner.pack(fill="both", expand=True, padx=6, pady=(0, 6))
    body = tk.Frame(inner, bg=CREAM, highlightbackground=OUTLINE, highlightthickness=2)
    body.pack(fill="both", expand=True)
    if scroll:
        sf = ScrollFrame(body, min_height)
        sf.pack(fill="both", expand=True)
        content = tk.Frame(sf.inner, bg=CREAM)
    else:
        content = tk.Frame(body, bg=CREAM)
    content.pack(fill="both", expand=True, padx=10, pady=8)
    return wrapper, content


def star_points(cx, cy, r):
    k = r * 0.25
    return [cx, cy - r, cx + k, cy - k, cx + r, cy, cx + k, cy + k,
            cx, cy + r, cx - k, cy + k, cx - r, cy, cx - k, cy - k]


# =====================================================================
#  MAIN APP
# =====================================================================
class CPUSchedulerGUI:
    def __init__(self, root):
        self.root = root
        init_fonts(root)
        root.title("PT 101 - CPU Scheduling Simulator")
        root.geometry("1240x900")
        root.minsize(1000, 720)
        root.configure(bg=TEAL)

        self.algo = ALGOS[0]
        self.processes = []
        self.pid_index = {}
        self.run = None
        self.t = 0.0
        self.playing = False
        self.finished = False
        self.anim_job = None
        self.frame_no = 0
        self.shown = -1
        self.comp = []
        self.comp_hover = -1
        self.stars = []
        self.g_x0, self.g_unit = 30, 1

        self.setup_styles()
        self.build_ui()
        for ev in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            root.bind_all(ev, self.on_wheel)
        self.select_algo(self.algo, run=False)
        self.reset_results()
        self.twinkle()

    # ------------------------------------------------------------ styles
    def setup_styles(self):
        st = ttk.Style()
        st.theme_use("clam")
        st.configure("Retro.Treeview", background="white", fieldbackground="white",
                     foreground=INK, rowheight=24, font=FONTS["body"],
                     bordercolor=SLATE, borderwidth=1)
        st.configure("Retro.Treeview.Heading", background=BLUE_DARK, foreground=INK,
                     font=FONTS["bodyb"], relief="flat", padding=3)
        st.map("Retro.Treeview", background=[("selected", CORAL)], foreground=[("selected", INK)])
        st.map("Retro.Treeview.Heading", background=[("active", "#b9e8ff")])
        st.configure("Retro.Vertical.TScrollbar", background=BLUE_DARK, troughcolor=CREAM_ALT,
                     bordercolor=SLATE, arrowcolor=INK, relief="flat")
        st.configure("Retro.TCombobox", fieldbackground="white", background=BLUE,
                     foreground=INK, arrowcolor=INK, bordercolor=SLATE, lightcolor=BLUE,
                     darkcolor=BLUE, padding=4, selectbackground="white", selectforeground=INK)
        st.map("Retro.TCombobox", fieldbackground=[("readonly", "white")],
               foreground=[("readonly", INK)], background=[("active", "#b9e8ff"), ("readonly", BLUE)])
        self.root.option_add("*TCombobox*Listbox.background", "white")
        self.root.option_add("*TCombobox*Listbox.foreground", INK)
        self.root.option_add("*TCombobox*Listbox.selectBackground", CORAL)
        self.root.option_add("*TCombobox*Listbox.selectForeground", INK)
        self.root.option_add("*TCombobox*Listbox.font", FONTS["body"])

    # ------------------------------------------------------------ layout
    def build_ui(self):
        r = self.root
        r.grid_columnconfigure(0, weight=3)
        r.grid_columnconfigure(1, weight=2)
        r.grid_rowconfigure(2, weight=3)
        r.grid_rowconfigure(3, weight=2)

        self.header = tk.Canvas(r, height=76, bg=TEAL, highlightthickness=0)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header.bind("<Configure>", self.draw_header)

        w, body = retro_window(r, "ADD PROCESS", "➕")
        w.grid(row=1, column=0, sticky="nsew", padx=(14, 4), pady=(2, 4))
        self.build_add_panel(body)

        w, body = retro_window(r, "CPU CORE", "🖥")
        w.grid(row=1, column=1, sticky="nsew", padx=(4, 14), pady=(2, 4))
        self.build_cpu_panel(body)

        w, body = retro_window(r, "SIMULATION  &  GANTT CHART", "📊", scroll=True, min_height=130)
        w.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=14, pady=4)
        self.build_gantt_panel(body)

        w, body = retro_window(r, "PROCESS METRICS", "📋", scroll=True, min_height=110)
        w.grid(row=3, column=0, sticky="nsew", padx=(14, 4), pady=(4, 8))
        self.build_metrics_panel(body)

        w, body = retro_window(r, "ALGORITHM LEADERBOARD", "🏆", scroll=True, min_height=110)
        w.grid(row=3, column=1, sticky="nsew", padx=(4, 14), pady=(4, 8))
        self.build_comparison_panel(body)

    # ---- header banner
    def draw_header(self, _=None):
        c = self.header
        c.delete("all")
        W = c.winfo_width() if c.winfo_width() > 10 else 1240
        H = 76
        for i in range(-14, 15):
            c.create_line(W / 2 + i * 14, 0, W / 2 + i * 80, H, fill=GRID)
        for y in (10, 24, 44):
            c.create_line(0, y, W, y, fill=GRID)

        tw = tkfont.Font(font=FONTS["title"]).measure("CPU SCHEDULING SIMULATOR") + 56
        x0, y0, x1, y1 = 18, 8, 18 + tw, 66
        c.create_rectangle(x0 + SH, y0 + SH, x1 + SH, y1 + SH, fill=SHADOW, outline=SHADOW)
        c.create_rectangle(x0, y0, x1, y1, fill=CREAM, outline=OUTLINE, width=2)
        c.create_rectangle(x0, y0, x1, y0 + 16, fill=BLUE, outline=OUTLINE, width=2)
        c.create_line(x0 + 10, y0 + 8, x0 + 52, y0 + 8, fill=SLATE, width=3)
        c.create_oval(x1 - 18, y0 + 4, x1 - 8, y0 + 14, fill=SLATE, outline=OUTLINE)
        c.create_text((x0 + x1) / 2, y0 + 38, text="CPU SCHEDULING SIMULATOR",
                      font=FONTS["title"], fill=SLATE)

        bw = 190
        bx0, bx1 = W - bw - 24, W - 24
        c.create_rectangle(bx0 + SH, 20 + SH, bx1 + SH, 56 + SH, fill=SHADOW, outline=SHADOW)
        c.create_rectangle(bx0, 20, bx1, 56, fill=BLUE, outline=OUTLINE, width=2)
        c.create_text((bx0 + bx1) / 2, 38, text="PT 101  •  TOPIC 1", font=FONTS["head"], fill=INK)

        self.stars = []
        rnd = random.Random(5)
        lo, hi = x1 + 50, bx0 - 30
        if hi > lo:
            for _i in range(12):
                cx, cy, r = rnd.uniform(lo, hi), rnd.uniform(10, 66), rnd.choice((4, 6, 8))
                self.stars.append(c.create_polygon(star_points(cx, cy, r), fill=SLATE, outline=""))

    def on_wheel(self, e):
        """Scroll whichever scrollable section the pointer is over."""
        try:
            w = self.root.winfo_containing(e.x_root, e.y_root)
        except (KeyError, tk.TclError):
            return
        while w is not None and not isinstance(w, ScrollFrame):
            if isinstance(w, ttk.Treeview) and w.yview() != (0.0, 1.0):
                return  # let a table that has its own overflow scroll itself
            w = w.master
        if w is None or w.canvas.yview() == (0.0, 1.0):
            return
        if e.num == 4:
            units = -1
        elif e.num == 5:
            units = 1
        else:
            units = -int(e.delta / 120) if abs(e.delta) >= 120 else (-1 if e.delta > 0 else 1)
        w.canvas.yview_scroll(units * 2, "units")

    def twinkle(self):
        for sid in self.stars:
            if random.random() < 0.3:
                self.header.itemconfig(sid, fill=random.choice((SLATE, "#d6efe9", SLATE)))
        self.root.after(600, self.twinkle)

    # ---- helpers
    def make_entry(self, parent, width=8):
        e = tk.Entry(parent, width=width, font=FONTS["body"], bg="white", fg=INK, relief="flat",
                     justify="center", highlightthickness=2, highlightbackground=SLATE,
                     highlightcolor=CORAL, insertbackground=INK)
        e.bind("<Return>", lambda _e: self.add_process())
        e.bind("<FocusIn>", lambda _e: e.select_range(0, tk.END))
        return e

    def make_tree(self, parent, cols, height, widths):
        wrap = tk.Frame(parent, bg=CREAM)
        tree = ttk.Treeview(wrap, columns=cols, show="headings", height=height, style="Retro.Treeview")
        sb = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview, style="Retro.Vertical.TScrollbar")
        tree.configure(yscrollcommand=sb.set)
        for col, w in zip(cols, widths):
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=w, minwidth=40)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        for i, colr in enumerate(PALETTE):
            tree.tag_configure(f"c{i}", background=lighten(colr, .62))
        return wrap, tree

    # ---- panel: add process
    def build_add_panel(self, parent):
        wrap, self.input_table = self.make_tree(parent, ("PID", "AT", "BT", "Priority"), 5, (64, 56, 56, 70))
        wrap.pack(side="left", fill="both", expand=True)

        form = tk.Frame(parent, bg=CREAM)
        form.pack(side="left", fill="y", padx=(14, 0))

        def lab(text, r, c):
            tk.Label(form, text=text, bg=CREAM, fg=INK, font=FONTS["bodyb"]).grid(
                row=r, column=c, sticky="e", padx=(0, 4), pady=4)

        lab("Process ID", 0, 0)
        self.entry_pid = self.make_entry(form)
        self.entry_pid.grid(row=0, column=1, padx=(0, 10))
        lab("Arrival (AT)", 0, 2)
        self.entry_at = self.make_entry(form)
        self.entry_at.grid(row=0, column=3)
        lab("Burst (BT)", 1, 0)
        self.entry_bt = self.make_entry(form)
        self.entry_bt.grid(row=1, column=1, padx=(0, 10))
        lab("Priority", 1, 2)
        self.entry_prio = self.make_entry(form)
        self.entry_prio.grid(row=1, column=3)
        tk.Label(form, text="lower priority number = runs first", bg=CREAM, fg=SLATE,
                 font=FONTS["small"]).grid(row=2, column=0, columnspan=4, pady=(0, 4))

        btns = tk.Frame(form, bg=CREAM)
        btns.grid(row=3, column=0, columnspan=4)
        RetroButton(btns, "▶ ADD", self.add_process, BTN_GREEN, 96).grid(row=0, column=0, padx=3, pady=3)
        RetroButton(btns, "✖ DELETE", self.delete_selected, BTN_CORAL, 96).grid(row=0, column=1, padx=3, pady=3)
        RetroButton(btns, "🗑 CLEAR", self.clear_all, BTN_ORANGE, 96).grid(row=0, column=2, padx=3, pady=3)
        RetroButton(btns, "★ SAMPLE", self.load_sample, BTN_BLUE, 96).grid(row=1, column=0, padx=3, pady=3)
        RetroButton(btns, "🎲 RANDOM", self.load_random, BTN_PURPLE, 96).grid(row=1, column=1, padx=3, pady=3)

        self.entry_pid.insert(0, "P1")

    # ---- panel: CPU core
    def build_cpu_panel(self, parent):
        self.chip = tk.Canvas(parent, width=170, height=170, bg=CREAM, highlightthickness=0)
        self.chip.pack(side="left")

        info = tk.Frame(parent, bg=CREAM)
        info.pack(side="left", fill="both", expand=True, padx=(10, 0))
        self.v_total = tk.StringVar()
        self.v_algo = tk.StringVar(value="FCFS")
        self.v_status = tk.StringVar(value="Ready")
        self.v_clock = tk.StringVar(value="0.0")

        def row(r, key, var):
            tk.Label(info, text=key, bg=CREAM, fg=SLATE, font=FONTS["monos"], anchor="w").grid(
                row=r, column=0, sticky="w", pady=3)
            lbl = tk.Label(info, textvariable=var, bg=CREAM, fg=INK, font=FONTS["mono"], anchor="w")
            lbl.grid(row=r, column=1, sticky="w", padx=8)
            return lbl

        row(0, "PROCESSES", self.v_total)
        row(1, "ALGORITHM", self.v_algo)
        self.lbl_status = row(2, "STATUS", self.v_status)
        row(3, "CLOCK (t)", self.v_clock)
        tk.Label(info, text="CPU LOAD", bg=CREAM, fg=SLATE, font=FONTS["monos"]).grid(
            row=4, column=0, sticky="w", pady=(8, 0))
        self.util = tk.Canvas(info, width=190, height=20, bg=CREAM, highlightthickness=0)
        self.util.grid(row=4, column=1, sticky="w", padx=8, pady=(8, 0))

    # ---- panel: algorithm tabs + info card + player bar + gantt
    def build_gantt_panel(self, parent):
        # --- tabs (stretch evenly across the panel; coloured bar marks the active one)
        self.tabbar = tk.Frame(parent, bg=CREAM)
        self.tabbar.pack(fill="x")
        self.tabs, self.tab_marks = {}, {}
        n = len(ALGO_TABS)
        for i, (full, label, *_rest) in enumerate(ALGO_TABS):
            cont = tk.Frame(self.tabbar, bg=CREAM)
            cont.pack(side="left", padx=(0, 10 if i < n - 1 else 0))
            tab = RetroButton(cont, label, lambda f=full: self.select_algo(f), _rest[0], 120, 34)
            tab.pack()
            mark = tk.Frame(cont, height=5, bg=CREAM)
            mark.pack(fill="x", padx=(0, RetroButton.DEPTH))
            self.tabs[full], self.tab_marks[full] = tab, mark
        self.tabbar.bind("<Configure>", self._layout_tabs)

        # --- info card
        self.card = tk.Frame(parent, bg="white", highlightbackground=OUTLINE, highlightthickness=2)
        self.card.pack(fill="x", pady=(0, 6))
        self.card_stripe = tk.Frame(self.card, width=10, bg=BTN_GREEN)
        self.card_stripe.pack(side="left", fill="y")
        box = tk.Frame(self.card, bg="white")
        box.pack(side="left", fill="both", expand=True, padx=10, pady=5)

        top = tk.Frame(box, bg="white")
        top.pack(fill="x")
        self.lbl_title = tk.Label(top, bg="white", fg=INK, font=FONTS["head"], anchor="w")
        self.lbl_title.pack(side="left")
        self.lbl_badge = tk.Label(top, font=FONTS["monos"], fg=INK, padx=8,
                                  highlightbackground=OUTLINE, highlightthickness=2)
        self.lbl_badge.pack(side="right")

        self.lbl_desc = tk.Label(box, bg="white", fg=INK, font=FONTS["body"], anchor="w",
                                 justify="left", wraplength=1000)
        self.lbl_desc.pack(fill="x", pady=(2, 2))

        box.bind("<Configure>", lambda e: self.lbl_desc.config(wraplength=max(300, e.width - 8)))

        # --- player bar: playback on the left, speed slider in the middle, compare on the right
        bar = tk.Frame(parent, bg="#e3f4fb", highlightbackground=OUTLINE, highlightthickness=2)
        bar.pack(fill="x")
        inner = tk.Frame(bar, bg="#e3f4fb")
        inner.pack(fill="x", padx=8, pady=6)

        RetroButton(inner, "▶ RUN", self.run_single, BTN_GREEN, 96, 32).pack(side="left", padx=(0, 6))
        self.btn_pause = RetroButton(inner, "⏸ PAUSE", self.toggle_pause, BTN_YELLOW, 108, 32)
        self.btn_pause.pack(side="left", padx=6)
        RetroButton(inner, "⏭ STEP", self.step, BTN_BLUE, 92, 32).pack(side="left", padx=6)
        RetroButton(inner, "⏩ SKIP", self.skip, BTN_ORANGE, 92, 32).pack(side="left", padx=6)

        RetroButton(inner, "⚡ COMPARE ALL", self.run_all_comparison, BTN_PURPLE, 150, 32).pack(side="right")

        sp = tk.Frame(inner, bg="#e3f4fb")
        sp.pack(side="left", fill="x", expand=True, padx=(18, 18))
        tk.Label(sp, text="SPEED", bg="#e3f4fb", fg=INK, font=FONTS["monos"]).pack(side="left", padx=(0, 6))
        tk.Label(sp, text="slow", bg="#e3f4fb", fg=SLATE, font=FONTS["small"]).pack(side="left")
        self.speed = tk.IntVar(value=4)
        self.lbl_speed = tk.Label(sp, text="4 u/s", bg="#e3f4fb", fg=INK, font=FONTS["monos"], width=6)
        self.lbl_speed.pack(side="right")
        tk.Label(sp, text="fast", bg="#e3f4fb", fg=SLATE, font=FONTS["small"]).pack(side="right")
        RetroSlider(sp, self.speed, 1, 12,
                    command=lambda v: self.lbl_speed.config(text=f"{v} u/s")).pack(
            side="left", fill="x", expand=True, padx=6)

        # --- gantt + ready queue
        self.canvas = tk.Canvas(parent, height=96, bg="white", highlightthickness=2,
                                highlightbackground=SLATE)
        self.canvas.pack(fill="both", expand=True, pady=(8, 4))
        self.canvas.bind("<Configure>", lambda _e: self.draw_gantt())
        self.canvas.bind("<Motion>", self.on_gantt_motion)
        self.canvas.bind("<Leave>", lambda _e: self.canvas.delete("tip"))

        self.queue = tk.Canvas(parent, height=38, bg=CREAM, highlightthickness=0)
        self.queue.pack(fill="x")
        self.queue.bind("<Configure>", lambda _e: self.draw_queue())

    def _layout_tabs(self, e):
        n, gap = len(ALGO_TABS), 10
        w = max(100, (e.width - gap * (n - 1) - 6) // n - RetroButton.DEPTH)
        for tab in self.tabs.values():
            if tab.w != w:
                tab.resize(w)

    # ---- panel: metrics
    def build_metrics_panel(self, parent):
        cols = ("PID", "AT", "BT", "Priority", "CT", "TAT", "WT", "RT")
        wrap, self.metrics_table = self.make_tree(parent, cols, 6, (60, 50, 50, 70, 50, 50, 50, 50))
        wrap.pack(fill="both", expand=True)
        self.lbl_averages = tk.Label(parent, text="Average TAT: -  |  Average WT: -  |  Average RT: -",
                                     bg="#ffe08a", fg=INK, font=FONTS["bodyb"],
                                     highlightbackground=OUTLINE, highlightthickness=2, pady=4)
        self.lbl_averages.pack(fill="x", pady=(8, 0))

    # ---- panel: comparison leaderboard
    def build_comparison_panel(self, parent):
        self.comp_canvas = tk.Canvas(parent, height=190, bg=CREAM, highlightthickness=0)
        self.comp_canvas.pack(fill="both", expand=True)
        self.comp_canvas.bind("<Configure>", lambda _e: self.draw_comparison())
        self.comp_canvas.bind("<Motion>", self.on_comp_motion)
        self.comp_canvas.bind("<Leave>", self.on_comp_leave)
        self.comp_canvas.bind("<Double-Button-1>", self.on_comp_double)

    # =================================================================
    #  PROCESS MANAGEMENT
    # =================================================================
    def color_of(self, pid):
        if pid == "IDLE":
            return IDLE_COLOR
        return PALETTE[self.pid_index.get(pid, 0) % len(PALETTE)]

    def reindex(self):
        for i, p in enumerate(self.processes):
            p.order = i
        self.pid_index = {p.pid: p.order for p in self.processes}

    def refresh_input_table(self):
        for item in self.input_table.get_children():
            self.input_table.delete(item)
        for p in self.processes:
            self.input_table.insert("", "end", values=(p.pid, p.at, p.bt, p.priority),
                                    tags=(f"c{p.order % len(PALETTE)}",))
        self.v_total.set(f"{len(self.processes):02d}")

    def suggest_pid(self):
        self.entry_pid.delete(0, tk.END)
        self.entry_pid.insert(0, f"P{len(self.processes) + 1}")

    def add_process(self):
        pid = self.entry_pid.get().strip()
        if not pid:
            messagebox.showerror("Error", "Process ID cannot be empty.")
            return
        if pid.upper() == "IDLE":
            messagebox.showerror("Error", "IDLE is a reserved Process ID.")
            return
        if any(p.pid.casefold() == pid.casefold() for p in self.processes):
            messagebox.showerror("Error", "Duplicate Process ID.")
            return
        try:
            at = int(self.entry_at.get())
            bt = int(self.entry_bt.get())
            prio = int(self.entry_prio.get()) if self.entry_prio.get() else 0
            if at < 0 or bt <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Arrival Time must be >= 0 and Burst Time must be > 0.")
            return

        self.processes.append(Process(pid, at, bt, prio, len(self.processes)))
        self.reindex()
        self.refresh_input_table()
        self.reset_results()
        for e in (self.entry_at, self.entry_bt, self.entry_prio):
            e.delete(0, tk.END)
        self.suggest_pid()
        self.entry_at.focus_set()

    def delete_selected(self):
        sel = self.input_table.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a process in the table first.")
            return
        for i in sorted((self.input_table.index(s) for s in sel), reverse=True):
            del self.processes[i]
        self.reindex()
        self.refresh_input_table()
        self.reset_results()
        self.suggest_pid()

    def clear_all(self):
        self.processes.clear()
        self.reindex()
        self.refresh_input_table()
        self.reset_results()
        self.suggest_pid()

    def _load(self, rows):
        self.processes = [Process(f"P{i + 1}", at, bt, pr, i) for i, (at, bt, pr) in enumerate(rows)]
        self.reindex()
        self.refresh_input_table()
        self.reset_results()
        self.suggest_pid()

    def load_sample(self):
        # includes an idle gap (17 -> 25) so IDLE blocks are visible
        self._load([(0, 6, 3), (2, 4, 1), (4, 2, 4), (6, 5, 2), (25, 3, 1)])

    def load_random(self):
        self._load([(random.randint(0, 10), random.randint(1, 9), random.randint(1, 5)) for _ in range(5)])

    # =================================================================
    #  STATE / STATUS
    # =================================================================
    def set_status(self, s):
        self.v_status.set(s)
        self.lbl_status.config(fg=STATUS_COLORS.get(s, INK))

    def select_algo(self, name, run=True):
        """Called when a tab is clicked: switch algorithm and play it straight away."""
        self.algo = name
        self.v_algo.set(name)
        for full, label, color, badge, title, desc in ALGO_TABS:
            self.tabs[full].set_active(full == name)
            self.tab_marks[full].config(bg=color if full == name else CREAM)
            if full == name:
                self.card_stripe.config(bg=color)
                self.lbl_title.config(text=title)
                self.lbl_badge.config(text=badge,
                                      bg="#ffd0d0" if badge == "PREEMPTIVE" else "#cfeeff")
                self.lbl_desc.config(text=desc)
        if run and self.processes:
            self.setup_run(True)
        elif run and self.run:
            self.reset_results()

    def cancel_anim(self):
        if self.anim_job is not None:
            self.root.after_cancel(self.anim_job)
            self.anim_job = None

    def reset_results(self):
        self.cancel_anim()
        self.run = None
        self.t = 0.0
        self.playing = False
        self.finished = False
        self.shown = -1
        self.comp = []
        self.comp_hover = -1
        for item in self.metrics_table.get_children():
            self.metrics_table.delete(item)
        self.lbl_averages.config(text="Average TAT: -  |  Average WT: -  |  Average RT: -")
        self.v_total.set(f"{len(self.processes):02d}")
        self.v_algo.set(self.algo)
        self.v_clock.set("0.0")
        self.set_status("Ready")
        self.btn_pause.set_text("⏸ PAUSE")
        self.draw_gantt()
        self.draw_queue()
        self.draw_comparison()
        self.refresh_chip()
        self.draw_util(0)

    # =================================================================
    #  PLAYBACK
    # =================================================================
    def simulate_by_name(self, name):
        return {
            "FCFS": lambda: self.simulate_fcfs(self.processes),
            "SJF (Non-Preemptive)": lambda: self.simulate_sjf(self.processes),
            "SRTF (Preemptive)": lambda: self.simulate_srtf(self.processes),
            "Priority (Non-Preemptive)": lambda: self.simulate_priority(self.processes, False),
            "Priority (Preemptive)": lambda: self.simulate_priority(self.processes, True),
        }[name]()

    def setup_run(self, autoplay=True):
        if not self.processes:
            messagebox.showwarning("Warning", "Please enter process details first.")
            return False
        algo = self.algo
        procs, timeline, a_tat, a_wt, a_rt = self.simulate_by_name(algo)
        self.cancel_anim()
        self.run = dict(algo=algo, procs=procs, timeline=timeline,
                        total=timeline[-1][1], avgs=(a_tat, a_wt, a_rt))
        self.t = 0.0
        self.finished = False
        self.shown = -1
        self.playing = autoplay
        self.v_algo.set(algo)
        self.btn_pause.set_text("⏸ PAUSE" if autoplay else "▶ RESUME")
        self.lbl_averages.config(text="Average TAT: -  |  Average WT: -  |  Average RT: -")
        self.set_status("Running" if autoplay else "Paused")
        self.update_view()
        if autoplay:
            self.anim_job = self.root.after(FRAME_MS, self._frame)
        return True

    def run_single(self):
        self.setup_run(True)

    def _frame(self):
        self.anim_job = None
        if not self.run or not self.playing:
            return
        self.t = min(self.t + self.speed.get() * FRAME_MS / 1000.0, self.run["total"])
        if self.t >= self.run["total"]:
            self.finish_run()
            return
        self.update_view()
        self.anim_job = self.root.after(FRAME_MS, self._frame)

    def finish_run(self):
        self.cancel_anim()
        self.t = self.run["total"]
        self.playing = False
        self.finished = True
        self.update_view()
        a_tat, a_wt, a_rt = self.run["avgs"]
        self.lbl_averages.config(
            text=f"Average TAT: {a_tat:.2f}  |  Average WT: {a_wt:.2f}  |  Average RT: {a_rt:.2f}")
        self.set_status("Complete")
        self.btn_pause.set_text("↻ REPLAY")

    def toggle_pause(self):
        if not self.run:
            self.setup_run(True)
        elif self.finished:
            self.select_algo(self.run["algo"], run=False)
            self.setup_run(True)
        elif self.playing:
            self.playing = False
            self.cancel_anim()
            self.set_status("Paused")
            self.btn_pause.set_text("▶ RESUME")
        else:
            self.playing = True
            self.set_status("Running")
            self.btn_pause.set_text("⏸ PAUSE")
            self.anim_job = self.root.after(FRAME_MS, self._frame)

    def step(self):
        if not self.run and not self.setup_run(False):
            return
        if self.finished:
            return
        self.playing = False
        self.cancel_anim()
        self.set_status("Paused")
        self.btn_pause.set_text("▶ RESUME")
        self.t = min(math.floor(self.t + 1e-9) + 1, self.run["total"])
        if self.t >= self.run["total"]:
            self.finish_run()
        else:
            self.update_view()

    def skip(self):
        if not self.run and not self.setup_run(False):
            return
        self.finish_run()

    def running_pid(self):
        if not self.run:
            return None
        for s, e, pid in self.run["timeline"]:
            if s <= self.t < e:
                return pid
        return None

    def update_view(self):
        self.frame_no += 1
        self.draw_gantt()
        self.draw_queue()
        self.refresh_chip()
        self.v_clock.set(f"{self.t:.1f}")

        busy = sum(min(e, self.t) - s for s, e, pid in self.run["timeline"] if pid != "IDLE" and s < self.t)
        self.draw_util(busy / self.t * 100 if self.t > 0 else 0)

        done = sorted([p for p in self.run["procs"] if p.ct <= self.t + 1e-9], key=lambda p: p.order)
        if len(done) != self.shown:
            self.shown = len(done)
            for item in self.metrics_table.get_children():
                self.metrics_table.delete(item)
            for p in done:
                self.metrics_table.insert("", "end",
                                          values=(p.pid, p.at, p.bt, p.priority, p.ct, p.tat, p.wt, p.rt),
                                          tags=(f"c{p.order % len(PALETTE)}",))

    # =================================================================
    #  DRAWING
    # =================================================================
    def draw_chip(self, label, color, active=False, small=False):
        c = self.chip
        c.delete("all")
        cx = cy = 85
        s = 42
        for i in range(5):
            o = -28 + i * 14
            c.create_line(cx + o, cy - s - 14, cx + o, cy - s, fill=SLATE, width=5)
            c.create_line(cx + o, cy + s, cx + o, cy + s + 14, fill=SLATE, width=5)
            c.create_line(cx - s - 14, cy + o, cx - s, cy + o, fill=SLATE, width=5)
            c.create_line(cx + s, cy + o, cx + s + 14, cy + o, fill=SLATE, width=5)
        if active:
            ring = 2 + ((self.frame_no // 3) % 3) * 2
            c.create_rectangle(cx - s - 19, cy - s - 19, cx + s + 19, cy + s + 19,
                               outline=lighten(color, .1), width=ring, dash=(6, 4))
        c.create_rectangle(cx - s + 5, cy - s + 5, cx + s + 5, cy + s + 5, fill=SHADOW, outline=SHADOW)
        c.create_rectangle(cx - s, cy - s, cx + s, cy + s, fill=color, outline=OUTLINE, width=3)
        c.create_rectangle(cx - s + 9, cy - s + 9, cx + s - 9, cy + s - 9,
                           fill=lighten(color, .3), outline=OUTLINE)
        c.create_text(cx, cy - 14, text="CPU", font=FONTS["chips"], fill=OUTLINE)
        c.create_text(cx, cy + 6, text=label, font=FONTS["chips"] if small else FONTS["chip"],
                      fill=INK)

    def refresh_chip(self):
        if not self.run:
            self.draw_chip("STANDBY", IDLE_COLOR, small=True)
        elif self.t >= self.run["total"]:
            self.draw_chip("DONE ✔", BTN_GREEN, small=True)
        else:
            pid = self.running_pid()
            if pid == "IDLE" or pid is None:
                self.draw_chip("IDLE", IDLE_COLOR)
            else:
                self.draw_chip(pid, self.color_of(pid), active=True)

    def draw_util(self, pct):
        u = self.util
        u.delete("all")
        u.create_rectangle(2, 3, 188, 19, fill=SHADOW, outline=SHADOW)
        u.create_rectangle(0, 1, 186, 17, fill="white", outline=OUTLINE, width=2)
        w = 182 * min(pct, 100) / 100
        col = BTN_GREEN if pct < 70 else (BTN_YELLOW if pct < 90 else BTN_CORAL)
        if w > 1:
            u.create_rectangle(2, 3, 2 + w, 15, fill=col, outline="")
        u.create_text(93, 9, text=f"{pct:.0f}%", font=FONTS["monos"], fill=INK)

    def draw_gantt(self):
        c = self.canvas
        c.delete("all")
        W = c.winfo_width() if c.winfo_width() > 10 else 900
        if not self.run:
            c.create_text(W / 2, 58, text="▶  Add processes, choose an algorithm and press RUN",
                          font=FONTS["head"], fill=SLATE)
            return
        tl, total, upto = self.run["timeline"], self.run["total"], self.t
        pad = 30
        unit = min((W - 2 * pad) / total, 64)
        self.g_x0, self.g_unit = pad, unit
        ytop, ybot, d = 30, 76, 4
        c.create_line(pad, ybot + d + 3, pad + total * unit, ybot + d + 3, fill=SLATE, width=2)
        for start, end, pid in tl:
            if start >= upto:
                break
            x1 = pad + start * unit
            x2 = pad + min(end, upto) * unit
            col = self.color_of(pid)
            c.create_rectangle(x1 + d, ytop + d, x2 + d, ybot + d, fill=SHADOW, outline=SHADOW)
            c.create_rectangle(x1, ytop, x2, ybot, fill=col, outline=OUTLINE, width=2,
                               dash=(4, 2) if pid == "IDLE" else None)
            if x2 - x1 > 10:
                c.create_rectangle(x1 + 3, ytop + 3, x2 - 3, ytop + 14, fill=lighten(col, .4), outline="")
            if x2 - x1 >= 24:
                c.create_text((x1 + x2) / 2, (ytop + ybot) / 2 + 4, text=pid,
                              fill=text_color_for(col), font=FONTS["head"])
            c.create_text(x1, ybot + d + 16, text=str(start), font=FONTS["monos"], fill=INK)
        if upto >= total:
            c.create_text(pad + total * unit, ybot + d + 16, text=str(total), font=FONTS["monos"], fill=INK)
        elif upto > 0 or self.playing:
            mx = pad + upto * unit
            c.create_line(mx, 18, mx, ybot + d + 3, fill=CORAL, width=3)
            c.create_rectangle(mx - 24, 2, mx + 24, 18, fill=CORAL, outline=OUTLINE, width=2)
            c.create_text(mx, 10, text=f"t={upto:.1f}", font=FONTS["monos"], fill=INK)

    def on_gantt_motion(self, e):
        c = self.canvas
        c.delete("tip")
        if not self.run or self.g_unit <= 0:
            return
        t = (e.x - self.g_x0) / self.g_unit
        if t < 0 or t >= min(self.t, self.run["total"]):
            return
        for s, en, pid in self.run["timeline"]:
            if s <= t < en:
                txt = f"{pid}   {s} → {en}   (len {en - s})"
                p = next((p for p in self.run["procs"] if p.pid == pid), None)
                if p:
                    txt += f"\nAT {p.at}  BT {p.bt}  Prio {p.priority}"
                x, y = e.x + 14, max(2, e.y - 46)
                tid = c.create_text(x, y, text=txt, anchor="nw", font=FONTS["small"], fill=INK, tags="tip")
                bb = c.bbox(tid)
                if bb[2] + 8 > c.winfo_width():
                    c.move("tip", c.winfo_width() - bb[2] - 10, 0)
                    bb = c.bbox(tid)
                rid = c.create_rectangle(bb[0] - 6, bb[1] - 4, bb[2] + 6, bb[3] + 4,
                                         fill="#fff3c4", outline=OUTLINE, width=2, tags="tip")
                c.tag_raise(tid)
                return

    def draw_queue(self):
        q = self.queue
        q.delete("all")
        W = q.winfo_width() if q.winfo_width() > 10 else 900
        q.create_text(6, 19, text="READY QUEUE ▸", anchor="w", font=FONTS["bodyb"], fill=SLATE)
        if not self.run:
            return
        running = self.running_pid()
        waiting = sorted([p for p in self.run["procs"] if p.at <= self.t < p.ct and p.pid != running],
                         key=lambda p: (p.at, p.order))
        x = 130
        if not waiting:
            q.create_text(x, 19, text="— empty —", anchor="w", font=FONTS["small"], fill=SLATE)
            return
        for i, p in enumerate(waiting):
            if x > W - 120 and i < len(waiting) - 1:
                q.create_text(x, 19, text=f"+{len(waiting) - i} more", anchor="w",
                              font=FONTS["bodyb"], fill=SLATE)
                break
            col = self.color_of(p.pid)
            q.create_rectangle(x + 3, 9, x + 57, 33, fill=SHADOW, outline=SHADOW)
            q.create_rectangle(x, 6, x + 54, 30, fill=col, outline=OUTLINE, width=2)
            q.create_text(x + 27, 18, text=p.pid, font=FONTS["bodyb"], fill=text_color_for(col))
            x += 66

    # ---- leaderboard
    def comp_geom(self):
        W = self.comp_canvas.winfo_width() if self.comp_canvas.winfo_width() > 10 else 560
        return W, 186, (W - 186 - 12) / 3, 26, 29

    def draw_comparison(self):
        c = self.comp_canvas
        c.delete("all")
        W, namew, colw, y0, rowh = self.comp_geom()
        if not self.comp:
            c.create_text(W / 2, 85, text="⚡ Press COMPARE ALL to rank every algorithm",
                          font=FONTS["head"], fill=SLATE)
            return
        bar_cols = (BTN_BLUE, BTN_CORAL, BTN_GREEN)
        for i, h in enumerate(("AVG TAT", "AVG WT", "AVG RT")):
            c.create_text(namew + colw * i + 4, 12, text=h, anchor="w", font=FONTS["monos"], fill=SLATE)
        best = [min(r[k] for r in self.comp) for k in (1, 2, 3)]
        maxv = [max(max(r[k] for r in self.comp), 1e-9) for k in (1, 2, 3)]
        for idx, (name, *vals) in enumerate(self.comp):
            y1 = y0 + idx * rowh
            bg = "#dff3ff" if idx == self.comp_hover else (CREAM if idx % 2 == 0 else CREAM_ALT)
            c.create_rectangle(0, y1, W, y1 + rowh, fill=bg, outline="")
            c.create_text(8, y1 + rowh / 2, text=name, anchor="w", font=FONTS["bodyb"], fill=INK)
            for k in range(3):
                v = vals[k]
                bx = namew + colw * k + 4
                bw = max(3, v / maxv[k] * max(colw - 70, 10))
                is_best = abs(v - best[k]) < 1e-9
                col = "#ffd166" if is_best else bar_cols[k]
                c.create_rectangle(bx + 2, y1 + 8, bx + bw + 2, y1 + rowh - 6, fill=SHADOW, outline=SHADOW)
                c.create_rectangle(bx, y1 + 6, bx + bw, y1 + rowh - 8, fill=col, outline=OUTLINE)
                c.create_text(bx + bw + 7, y1 + rowh / 2 - 1, text=("★ " if is_best else "") + f"{v:.2f}",
                              anchor="w", font=FONTS["monos"], fill=INK)
        c.create_text(W / 2, y0 + len(self.comp) * rowh + 12,
                      text="★ = best in column   •   double-click a row to run it",
                      font=FONTS["small"], fill=SLATE)

    def _comp_row(self, y):
        _, _, _, y0, rowh = self.comp_geom()
        i = int((y - y0) // rowh)
        return i if 0 <= i < len(self.comp) else -1

    def on_comp_motion(self, e):
        i = self._comp_row(e.y)
        self.comp_canvas.config(cursor="hand2" if i >= 0 else "")
        if i != self.comp_hover:
            self.comp_hover = i
            self.draw_comparison()

    def on_comp_leave(self, _e):
        if self.comp_hover != -1:
            self.comp_hover = -1
            self.draw_comparison()

    def on_comp_double(self, e):
        i = self._comp_row(e.y)
        if i >= 0:
            self.select_algo(self.comp[i][0])

    def run_all_comparison(self):
        if not self.processes:
            messagebox.showwarning("Warning", "Please enter process details first.")
            return
        self.comp = []
        for name in ALGOS:
            _p, _t, a_tat, a_wt, a_rt = self.simulate_by_name(name)
            self.comp.append((name, a_tat, a_wt, a_rt))
        self.comp_hover = -1
        self.draw_comparison()

    # =================================================================
    #  SIMULATION ALGORITHMS (unchanged)
    # =================================================================
    def simulate_fcfs(self, proc_list):
        processes = copy_processes(proc_list)
        processes.sort(key=lambda p: (p.at, p.order))
        current_time, timeline = 0, []
        for p in processes:
            if current_time < p.at:
                add_segment(timeline, current_time, p.at, "IDLE")
                current_time = p.at
            start_time = current_time
            current_time += p.bt
            p.ct = current_time
            p.calculate_metrics(start_time)
            add_segment(timeline, start_time, current_time, p.pid)
        return self.get_results(processes, timeline)

    def simulate_sjf(self, proc_list):
        processes = copy_processes(proc_list)
        completed, current_time, timeline = 0, 0, []
        is_completed = [False] * len(processes)
        while completed < len(processes):
            ready = [i for i in range(len(processes)) if processes[i].at <= current_time and not is_completed[i]]
            if not ready:
                next_arrival = min(processes[i].at for i in range(len(processes)) if not is_completed[i])
                add_segment(timeline, current_time, next_arrival, "IDLE")
                current_time = next_arrival
                continue
            idx = min(ready, key=lambda i: (processes[i].bt, processes[i].at, processes[i].order))
            p = processes[idx]
            start_time = current_time
            current_time += p.bt
            p.ct = current_time
            p.calculate_metrics(start_time)
            is_completed[idx] = True
            completed += 1
            add_segment(timeline, start_time, current_time, p.pid)
        return self.get_results(processes, timeline)

    def simulate_srtf(self, proc_list):
        processes = copy_processes(proc_list)
        completed, current_time, timeline = 0, 0, []
        first_starts = {}
        while completed < len(processes):
            ready = [p for p in processes if p.at <= current_time and p.remaining_time > 0]
            if not ready:
                next_arrival = min(p.at for p in processes if p.remaining_time > 0)
                add_segment(timeline, current_time, next_arrival, "IDLE")
                current_time = next_arrival
                continue
            p = min(ready, key=lambda x: (x.remaining_time, x.at, x.order))
            if p.pid not in first_starts:
                first_starts[p.pid] = current_time
            add_segment(timeline, current_time, current_time + 1, p.pid)
            p.remaining_time -= 1
            current_time += 1
            if p.remaining_time == 0:
                p.ct = current_time
                p.calculate_metrics(first_starts[p.pid])
                completed += 1
        return self.get_results(processes, timeline)

    def simulate_priority(self, proc_list, is_preemptive=False):
        processes = copy_processes(proc_list)
        completed, current_time, timeline = 0, 0, []
        first_starts = {}
        if not is_preemptive:
            is_completed = [False] * len(processes)
            while completed < len(processes):
                ready = [i for i in range(len(processes)) if processes[i].at <= current_time and not is_completed[i]]
                if not ready:
                    next_arrival = min(processes[i].at for i in range(len(processes)) if not is_completed[i])
                    add_segment(timeline, current_time, next_arrival, "IDLE")
                    current_time = next_arrival
                    continue
                idx = min(ready, key=lambda i: (processes[i].priority, processes[i].at, processes[i].order))
                p = processes[idx]
                start_time = current_time
                current_time += p.bt
                p.ct = current_time
                p.calculate_metrics(start_time)
                is_completed[idx] = True
                completed += 1
                add_segment(timeline, start_time, current_time, p.pid)
        else:
            while completed < len(processes):
                ready = [p for p in processes if p.at <= current_time and p.remaining_time > 0]
                if not ready:
                    next_arrival = min(p.at for p in processes if p.remaining_time > 0)
                    add_segment(timeline, current_time, next_arrival, "IDLE")
                    current_time = next_arrival
                    continue
                p = min(ready, key=lambda x: (x.priority, x.at, x.order))
                if p.pid not in first_starts:
                    first_starts[p.pid] = current_time
                add_segment(timeline, current_time, current_time + 1, p.pid)
                p.remaining_time -= 1
                current_time += 1
                if p.remaining_time == 0:
                    p.ct = current_time
                    p.calculate_metrics(first_starts[p.pid])
                    completed += 1
        return self.get_results(processes, timeline)

    def get_results(self, processes, timeline):
        n = len(processes)
        avg_tat = sum(p.tat for p in processes) / n
        avg_wt = sum(p.wt for p in processes) / n
        avg_rt = sum(p.rt for p in processes) / n
        return processes, timeline, avg_tat, avg_wt, avg_rt


if __name__ == "__main__":
    root = tk.Tk()
    app = CPUSchedulerGUI(root)
    root.mainloop()
