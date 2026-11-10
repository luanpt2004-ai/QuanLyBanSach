import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import luu_tru
import nhan_vien
import khach_hang
import sach
import hoa_don
import ton_kho
import bao_cao


class QuanLyBanSachApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("QUẢN LÝ BÁN SÁCH")
        self.geometry("1150x700")
        self.minsize(1050, 650)
        self.configure(bg="#F4F6F9")

        self.nhan_vien_hien_tai = None
        self.thiet_lap_style()

        luu_tru.khoi_tao_du_lieu_mau()

        self.hien_thi_man_hinh_dang_nhap()

    def thiet_lap_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        PRIMARY_COLOR = "#1F497D"
        SUCCESS_COLOR = "#28A745"
        DANGER_COLOR = "#DC3545"

        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#E4E8EC", foreground=PRIMARY_COLOR)
        self.style.configure("Treeview", rowheight=26)
        self.style.map("Treeview", background=[("selected", PRIMARY_COLOR)], foreground=[("selected", "white")])

        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), background=PRIMARY_COLOR, foreground="white")
        self.style.map("Primary.TButton", background=[("active", "#153256")])

        self.style.configure("Success.TButton", font=("Segoe UI", 10, "bold"), background=SUCCESS_COLOR, foreground="white")
        self.style.map("Success.TButton", background=[("active", "#218838")])

        self.style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), background=DANGER_COLOR, foreground="white")
        self.style.map("Danger.TButton", background=[("active", "#C82333")])

    def xoa_toan_bo_widget(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ===================================================
    # MÀN HÌNH ĐĂNG NHẬP (KHÔNG PHÂN QUYỀN PHỨC TẠP)
    # ===================================================
    def hien_thi_man_hinh_dang_nhap(self):
        self.xoa_toan_bo_widget()
        self.nhan_vien_hien_tai = None

        container = tk.Frame(self, bg="#F4F6F9")
        container.place(relx=0.5, rely=0.5, anchor="center")

        box = tk.Frame(container, bg="white", padx=45, pady=40, relief="groove", bd=1)
        box.pack()

        tk.Label(box, text="ĐĂNG NHẬP HỆ THỐNG", font=("Segoe UI", 18, "bold"), fg="#1F497D", bg="white").pack(pady=(0, 5))
        tk.Label(box, text="Hệ thống Quản lý Bán Sách & Kho Hàng", font=("Segoe UI", 10), fg="#666666", bg="white").pack(pady=(0, 20))

        tk.Label(box, text="Tên đăng nhập:", font=("Segoe UI", 10, "bold"), bg="white", anchor="w").pack(fill="x", pady=(5, 2))
        self.txt_login_user = ttk.Entry(box, width=32, font=("Segoe UI", 11))
        self.txt_login_user.pack(pady=(0, 10))
        self.txt_login_user.insert(0, "admin")

        tk.Label(box, text="Mật khẩu:", font=("Segoe UI", 10, "bold"), bg="white", anchor="w").pack(fill="x", pady=(5, 2))
        self.txt_login_pass = ttk.Entry(box, width=32, font=("Segoe UI", 11), show="*")
        self.txt_login_pass.pack(pady=(0, 20))
        self.txt_login_pass.insert(0, "admin123")

        btn_login = ttk.Button(box, text="ĐĂNG NHẬP", style="Primary.TButton", command=self.xu_ly_dang_nhap)
        btn_login.pack(fill="x", ipady=5)

        tk.Label(box, text="Tài khoản có sẵn: admin / admin123  hoặc  nhanvien / 123456", font=("Segoe UI", 8, "italic"), fg="#888888", bg="white").pack(pady=(15, 0))
        self.bind("<Return>", lambda e: self.xu_ly_dang_nhap())

    def xu_ly_dang_nhap(self):
        u = self.txt_login_user.get().strip()
        p = self.txt_login_pass.get().strip()
        if not u or not p:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tên đăng nhập và mật khẩu!")
            return

        nv, msg = nhan_vien.xac_thuc_dang_nhap(u, p)
        if nv:
            self.nhan_vien_hien_tai = nv
            self.unbind("<Return>")
            messagebox.showinfo("Thành công", f"Đăng nhập thành công!\nXin chào: {nv.get('ho_ten')}")
            self.hien_thi_giao_dien_chinh()
        else:
            messagebox.showerror("Đăng nhập thất bại", msg)

    # ===================================================
    # GIAO DIỆN CHÍNH (ĐẦY ĐỦ 8 TABS THEO ĐỀ XUẤT)
    # ===================================================
    def hien_thi_giao_dien_chinh(self):
        self.xoa_toan_bo_widget()

        # Thanh Header
        top_bar = tk.Frame(self, bg="#1F497D", height=50)
        top_bar.pack(fill="x", side="top")

        tk.Label(top_bar, text="QUẢN LÝ BÁN SÁCH", font=("Segoe UI", 14, "bold"), fg="white", bg="#1F497D").pack(side="left", padx=20, pady=10)

        # Ghi nhận người dùng: "Xin chào: [Tên nhân viên]"
        tk.Label(
            top_bar,
            text=f"Xin chào: {self.nhan_vien_hien_tai.get('ho_ten')} ({self.nhan_vien_hien_tai.get('ma_nhan_vien')})",
            font=("Segoe UI", 10),
            fg="#F0F0F0",
            bg="#1F497D"
        ).pack(side="right", padx=15)

        ttk.Button(top_bar, text="Đăng xuất", command=self.hien_thi_man_hinh_dang_nhap).pack(side="right", padx=10, pady=10)

        # Tab Notebook
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=8)

        # 1. Tổng quan
        self.tab_tong_quan = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_tong_quan, text=" 🏠 Tổng Quan ")
        self.khoi_tao_tab_tong_quan()

        # 2. Hóa đơn bán sách (Bán hàng)
        self.tab_ban_hang = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_ban_hang, text=" 🛒 Hóa Đơn Bán Sách ")
        self.khoi_tao_tab_ban_hang()

        # 3. Quản lý Sách
        self.tab_sach = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sach, text=" 📚 Quản Lý Sách ")
        self.khoi_tao_tab_sach()

        # 4. Thể loại sách
        self.tab_the_loai = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_the_loai, text=" 🏷️ Thể Loại Sách ")
        self.khoi_tao_tab_the_loai()

        # 5. Khách hàng
        self.tab_khach_hang = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_khach_hang, text=" 👥 Khách Hàng ")
        self.khoi_tao_tab_khach_hang()

        # 6. Nhân viên
        self.tab_nhan_vien = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_nhan_vien, text=" 👤 Nhân Viên ")
        self.khoi_tao_tab_nhan_vien()

        # 7. Lịch sử tồn kho
        self.tab_lich_su = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_lich_su, text=" 📦 Lịch Sử Tồn Kho ")
        self.khoi_tao_tab_lich_su()

        # 8. Báo cáo – Thống kê
        self.tab_bao_cao = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_bao_cao, text=" 📊 Báo Cáo – Thống Kê ")
        self.khoi_tao_tab_bao_cao()

    # ===================================================
    # 1. TAB TỔNG QUAN
    # ===================================================
    def khoi_tao_tab_tong_quan(self):
        f = tk.Frame(self.tab_tong_quan, bg="#F4F6F9", padx=20, pady=20)
        f.pack(fill="both", expand=True)

        tk.Label(f, text="DASHBOARD TỔNG QUAN NHÀ SÁCH", font=("Segoe UI", 16, "bold"), fg="#1F497D", bg="#F4F6F9").pack(anchor="w", pady=(0, 15))

        # Khối thẻ tóm tắt
        cards_f = tk.Frame(f, bg="#F4F6F9")
        cards_f.pack(fill="x", pady=10)

        self.card_tong_sach = tk.Label(cards_f, text="📚 TỔNG ĐẦU SÁCH\n0", font=("Segoe UI", 11, "bold"), bg="white", fg="#1F497D", padx=20, pady=15, relief="groove", bd=1)
        self.card_tong_sach.pack(side="left", fill="x", expand=True, padx=5)

        self.card_tong_don = tk.Label(cards_f, text="🧾 ĐƠN HOÀN THÀNH\n0", font=("Segoe UI", 11, "bold"), bg="white", fg="#28A745", padx=20, pady=15, relief="groove", bd=1)
        self.card_tong_don.pack(side="left", fill="x", expand=True, padx=5)

        self.card_doanh_thu = tk.Label(cards_f, text="💰 TỔNG DOANH THU\n0 VNĐ", font=("Segoe UI", 11, "bold"), bg="white", fg="#E67E22", padx=20, pady=15, relief="groove", bd=1)
        self.card_doanh_thu.pack(side="left", fill="x", expand=True, padx=5)

        self.card_canh_bao_kho = tk.Label(cards_f, text="🚨 CẢNH BÁO TỒN KHO\n0", font=("Segoe UI", 11, "bold"), bg="white", fg="#DC3545", padx=20, pady=15, relief="groove", bd=1)
        self.card_canh_bao_kho.pack(side="left", fill="x", expand=True, padx=5)

        # Nút thao tác nhanh
        quick_f = tk.LabelFrame(f, text="Lối tắt thao tác nhanh", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=15)
        quick_f.pack(fill="x", pady=20)

        ttk.Button(quick_f, text="➕ Tạo Hóa Đơn Mới", style="Primary.TButton", command=lambda: self.notebook.select(self.tab_ban_hang)).pack(side="left", padx=10)
        ttk.Button(quick_f, text="📚 Xem Kho Sách", command=lambda: self.notebook.select(self.tab_sach)).pack(side="left", padx=10)
        ttk.Button(quick_f, text="📦 Xem Lịch Sử Kho", command=lambda: self.notebook.select(self.tab_lich_su)).pack(side="left", padx=10)
        ttk.Button(quick_f, text="📊 Xuất Báo Cáo Excel", style="Success.TButton", command=self.xuat_excel_nhanh).pack(side="left", padx=10)

        self.cap_nhat_dashboard()

    def cap_nhat_dashboard(self):
        ds_s = sach.lay_danh_sach_sach()
        rev = bao_cao.thong_ke_doanh_thu()
        low = bao_cao.thong_ke_sach_ton_kho_canh_bao()

        self.card_tong_sach.config(text=f"📚 TỔNG ĐẦU SÁCH\n{len(ds_s)} tựa sách")
        self.card_tong_don.config(text=f"🧾 ĐƠN HOÀN THÀNH\n{rev['tong_so_don']} đơn")
        self.card_doanh_thu.config(text=f"💰 TỔNG DOANH THU\n{rev['tong_doanh_thu']:,.0f} VNĐ")
        self.card_canh_bao_kho.config(text=f"🚨 CẢNH BÁO TỒN KHO\n{len(low)} sách sắp hết")

    def xuat_excel_nhanh(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialdir="bao_cao/excel",
            initialfile="BaoCao_TongHop.xlsx"
        )
        if file_path:
            bao_cao.xuat_bao_cao_excel(file_path)
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel thành công tại:\n{file_path}")

    # ===================================================
    # 2. TAB HÓA ĐƠN BÁN SÁCH & BÁN HÀNG
    # ===================================================
    def khoi_tao_tab_ban_hang(self):
        self.gio_hang = []

        sub_nb = ttk.Notebook(self.tab_ban_hang)
        sub_nb.pack(fill="both", expand=True, padx=5, pady=5)

        tab_tao_moi = ttk.Frame(sub_nb)
        sub_nb.add(tab_tao_moi, text=" 🛒 Lập Hóa Đơn Bán Hàng ")

        tab_danh_sach_hd = ttk.Frame(sub_nb)
        sub_nb.add(tab_danh_sach_hd, text=" 📜 Danh Sách Hóa Đơn & Xử Lý ")

        # --- Giao diện Tạo đơn mới ---
        paned = tk.PanedWindow(tab_tao_moi, orient=tk.HORIZONTAL, bg="#D0D7DE")
        paned.pack(fill="both", expand=True, padx=5, pady=5)

        # Cột trái: Chọn sách
        f_left = tk.Frame(paned, bg="white", padx=10, pady=10)
        paned.add(f_left, minsize=460)

        tk.Label(f_left, text="KHO SÁCH SẴN CÓ", font=("Segoe UI", 11, "bold"), fg="#1F497D", bg="white").pack(anchor="w")

        search_bar = tk.Frame(f_left, bg="white")
        search_bar.pack(fill="x", pady=5)
        tk.Label(search_bar, text="Tìm sách:", bg="white").pack(side="left")
        self.txt_search_sale = ttk.Entry(search_bar, width=22)
        self.txt_search_sale.pack(side="left", padx=5)
        ttk.Button(search_bar, text="Tìm", command=self.load_sach_ban_hang).pack(side="left")

        cols = ("ma_sach", "ten_sach", "gia_ban", "so_luong_ton")
        self.tree_sale_sach = ttk.Treeview(f_left, columns=cols, show="headings", height=12)
        self.tree_sale_sach.heading("ma_sach", text="Mã")
        self.tree_sale_sach.heading("ten_sach", text="Tên sách")
        self.tree_sale_sach.heading("gia_ban", text="Giá bán")
        self.tree_sale_sach.heading("so_luong_ton", text="Tồn kho")

        self.tree_sale_sach.column("ma_sach", width=40, anchor="center")
        self.tree_sale_sach.column("ten_sach", width=200)
        self.tree_sale_sach.column("gia_ban", width=85, anchor="e")
        self.tree_sale_sach.column("so_luong_ton", width=65, anchor="center")
        self.tree_sale_sach.pack(fill="both", expand=True, pady=5)

        add_bar = tk.Frame(f_left, bg="white")
        add_bar.pack(fill="x", pady=5)
        tk.Label(add_bar, text="Số lượng:", bg="white", font=("Segoe UI", 9, "bold")).pack(side="left")
        self.sp_qty = ttk.Spinbox(add_bar, from_=1, to=500, width=6)
        self.sp_qty.set(1)
        self.sp_qty.pack(side="left", padx=5)

        tk.Label(add_bar, text="Giảm giá món:", bg="white").pack(side="left", padx=(10, 2))
        self.txt_item_discount = ttk.Entry(add_bar, width=8)
        self.txt_item_discount.insert(0, "0")
        self.txt_item_discount.pack(side="left")

        ttk.Button(add_bar, text="➕ Thêm Giỏ", style="Primary.TButton", command=self.them_vao_gio).pack(side="left", padx=10)

        # Cột phải: Giỏ hàng & Thanh toán
        f_right = tk.Frame(paned, bg="white", padx=10, pady=10)
        paned.add(f_right, minsize=500)

        tk.Label(f_right, text="GIỎ HÀNG & THANH TOÁN", font=("Segoe UI", 11, "bold"), fg="#1F497D", bg="white").pack(anchor="w")

        info_box = tk.Frame(f_right, bg="white")
        info_box.pack(fill="x", pady=5)
        tk.Label(info_box, text="Khách hàng:", bg="white").grid(row=0, column=0, sticky="w")
        self.cb_khach = ttk.Combobox(info_box, state="readonly", width=32)
        self.cb_khach.grid(row=0, column=1, padx=5, sticky="w")
        self.load_combobox_khach_hang()

        tk.Label(info_box, text="Trạng thái:", bg="white").grid(row=0, column=2, padx=(10, 2), sticky="w")
        self.cb_order_status = ttk.Combobox(info_box, state="readonly", values=["Hoàn thành", "Nháp"], width=12)
        self.cb_order_status.current(0)
        self.cb_order_status.grid(row=0, column=3, sticky="w")

        # Bảng giỏ hàng
        c_cols = ("ma_sach", "ten_sach", "so_luong", "don_gia_ban", "giam_gia", "thanh_tien")
        self.tree_cart = ttk.Treeview(f_right, columns=c_cols, show="headings", height=8)
        self.tree_cart.heading("ma_sach", text="Mã")
        self.tree_cart.heading("ten_sach", text="Tên sách")
        self.tree_cart.heading("so_luong", text="SL")
        self.tree_cart.heading("don_gia_ban", text="Đơn giá")
        self.tree_cart.heading("giam_gia", text="Giảm")
        self.tree_cart.heading("thanh_tien", text="Thành tiền")

        self.tree_cart.column("ma_sach", width=35, anchor="center")
        self.tree_cart.column("ten_sach", width=160)
        self.tree_cart.column("so_luong", width=40, anchor="center")
        self.tree_cart.column("don_gia_ban", width=75, anchor="e")
        self.tree_cart.column("giam_gia", width=65, anchor="e")
        self.tree_cart.column("thanh_tien", width=85, anchor="e")
        self.tree_cart.pack(fill="both", expand=True, pady=5)

        ttk.Button(f_right, text="Xóa dòng đã chọn khỏi giỏ", command=self.xoa_khoi_gio).pack(anchor="e")

        # Khối tổng tiền
        sum_box = tk.Frame(f_right, bg="#F0F4F8", padx=10, pady=8, relief="groove", bd=1)
        sum_box.pack(fill="x", pady=8)

        tk.Label(sum_box, text="Chiết khấu/Giảm giá hóa đơn (VNĐ):", bg="#F0F4F8").grid(row=0, column=0, sticky="w")
        self.txt_order_discount = ttk.Entry(sum_box, width=15)
        self.txt_order_discount.insert(0, "0")
        self.txt_order_discount.grid(row=0, column=1, padx=5, sticky="w")
        self.txt_order_discount.bind("<KeyRelease>", lambda e: self.cap_nhat_tong_tien_hien_thi())

        self.lbl_pay_total = tk.Label(sum_box, text="TỔNG TIỀN: 0 VNĐ", font=("Segoe UI", 13, "bold"), fg="#DC3545", bg="#F0F4F8")
        self.lbl_pay_total.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))

        ttk.Button(sum_box, text="💳 HOÀN THÀNH & LẬP HÓA ĐƠN", style="Success.TButton", command=self.xu_ly_thanh_toan).grid(row=1, column=2, padx=10, sticky="e")

        # --- Danh sách Hóa đơn & Xử lý (Tab 2 của Hóa đơn) ---
        f_hd_list = tk.Frame(tab_danh_sach_hd, bg="#F4F6F9", padx=10, pady=10)
        f_hd_list.pack(fill="both", expand=True)

        tool_bar = tk.Frame(f_hd_list, bg="#F4F6F9")
        tool_bar.pack(fill="x", pady=(0, 5))

        ttk.Button(tool_bar, text="🔄 Làm Mới", command=self.load_danh_sach_hoa_don).pack(side="left")
        ttk.Button(tool_bar, text="📄 Xuất Hóa Đơn PDF", style="Primary.TButton", command=self.xuat_pdf_hoa_don_da_chon).pack(side="left", padx=10)
        ttk.Button(tool_bar, text="❌ Hủy Hóa Đơn (Hoàn Kho)", style="Danger.TButton", command=self.xu_ly_huy_hoa_don).pack(side="left")

        hd_cols = ("ma_hd", "ma_hoa_don", "ngay_lap", "ten_kh", "ten_nv", "tong_tien", "trang_thai")
        self.tree_all_hd = ttk.Treeview(f_hd_list, columns=hd_cols, show="headings", height=15)
        self.tree_all_hd.heading("ma_hd", text="ID")
        self.tree_all_hd.heading("ma_hoa_don", text="Mã HĐ")
        self.tree_all_hd.heading("ngay_lap", text="Ngày lập")
        self.tree_all_hd.heading("ten_kh", text="Khách hàng")
        self.tree_all_hd.heading("ten_nv", text="Người lập")
        self.tree_all_hd.heading("tong_tien", text="Tổng tiền")
        self.tree_all_hd.heading("trang_thai", text="Trạng thái")

        self.tree_all_hd.column("ma_hd", width=40, anchor="center")
        self.tree_all_hd.column("ma_hoa_don", width=80, anchor="center")
        self.tree_all_hd.column("ngay_lap", width=140, anchor="center")
        self.tree_all_hd.column("ten_kh", width=170)
        self.tree_all_hd.column("ten_nv", width=150)
        self.tree_all_hd.column("tong_tien", width=110, anchor="e")
        self.tree_all_hd.column("trang_thai", width=100, anchor="center")
        self.tree_all_hd.pack(fill="both", expand=True)

        self.load_sach_ban_hang()
        self.load_danh_sach_hoa_don()

    def load_combobox_khach_hang(self):
        kh_list = khach_hang.lay_danh_sach_khach_hang()
        self.kh_dict = {f"{k['ma_kh']} - {k['ho_ten']} ({k.get('so_dien_thoai') or 'Khách lẻ'})": k['ma_kh'] for k in kh_list}
        self.cb_khach['values'] = list(self.kh_dict.keys())
        if self.kh_dict:
            self.cb_khach.current(0)

    def load_sach_ban_hang(self):
        kw = self.txt_search_sale.get().strip()
        ds = sach.lay_danh_sach_sach(tu_khoa=kw)
        self.tree_sale_sach.delete(*self.tree_sale_sach.get_children())
        for s in ds:
            self.tree_sale_sach.insert("", "end", values=(
                s["ma_sach"], s["ten_sach"], f"{float(s['gia_ban']):,.0f}", s["so_luong_ton"]
            ))

    def them_vao_gio(self):
        sel = self.tree_sale_sach.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một cuốn sách từ bảng!")
            return

        try:
            sl = int(self.sp_qty.get())
            gg_mon = float(self.txt_item_discount.get().strip())
            if sl <= 0 or gg_mon < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Số lượng mua phải > 0 và giảm giá món >= 0!")
            return

        row_vals = self.tree_sale_sach.item(sel[0])["values"]
        ma_s = str(row_vals[0])
        ten_s = str(row_vals[1])
        gia_ban = float(str(row_vals[2]).replace(",", ""))
        ton_kho_hien_tai = int(row_vals[3])

        # Kiểm tra tồn kho đối với các mặt hàng trong giỏ
        sl_trong_gio = sum(item["so_luong"] for item in self.gio_hang if item["ma_sach"] == ma_s)
        if (sl_trong_gio + sl) > ton_kho_hien_tai:
            messagebox.showerror("Không đủ tồn kho", f"Sách '{ten_s}' chỉ còn {ton_kho_hien_tai} cuốn trong kho!")
            return

        for item in self.gio_hang:
            if item["ma_sach"] == ma_s:
                item["so_luong"] += sl
                item["giam_gia"] += gg_mon
                item["thanh_tien"] = max(0, (item["so_luong"] * item["don_gia_ban"]) - item["giam_gia"])
                self.cap_nhat_bang_gio_hang()
                return

        thanh_tien = max(0, (sl * gia_ban) - gg_mon)
        self.gio_hang.append({
            "ma_sach": ma_s,
            "ten_sach": ten_s,
            "so_luong": sl,
            "don_gia_ban": gia_ban,
            "giam_gia": gg_mon,
            "thanh_tien": thanh_tien
        })
        self.cap_nhat_bang_gio_hang()

    def xoa_khoi_gio(self):
        sel = self.tree_cart.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn dòng sách cần xóa trong giỏ hàng!")
            return
        idx = self.tree_cart.index(sel[0])
        del self.gio_hang[idx]
        self.cap_nhat_bang_gio_hang()

    def cap_nhat_bang_gio_hang(self):
        self.tree_cart.delete(*self.tree_cart.get_children())
        for it in self.gio_hang:
            self.tree_cart.insert("", "end", values=(
                it["ma_sach"], it["ten_sach"], it["so_luong"],
                f"{it['don_gia_ban']:,.0f}", f"{it['giam_gia']:,.0f}", f"{it['thanh_tien']:,.0f}"
            ))
        self.cap_nhat_tong_tien_hien_thi()

    def cap_nhat_tong_tien_hien_thi(self):
        try:
            gg_tong = float(self.txt_order_discount.get().strip())
        except ValueError:
            gg_tong = 0
        ket_qua = hoa_don.tinh_tong_tien_gio_hang(self.gio_hang, gg_tong)
        self.lbl_pay_total.config(text=f"TỔNG TIỀN: {ket_qua['tong_thanh_toan']:,.0f} VNĐ")

    def xu_ly_thanh_toan(self):
        if not self.gio_hang:
            messagebox.showwarning("Giỏ hàng rỗng", "Vui lòng thêm sách vào giỏ hàng trước!")
            return

        try:
            gg_tong = float(self.txt_order_discount.get().strip())
            if gg_tong < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Giảm giá hóa đơn phải là số không âm (>= 0)!")
            return

        kh_str = self.cb_khach.get()
        ma_kh = self.kh_dict.get(kh_str, "1")
        ma_nv = self.nhan_vien_hien_tai.get("ma_nv")
        status = self.cb_order_status.get()

        xac_nhan = messagebox.askyesno("Xác nhận", f"Xác nhận lập hóa đơn với trạng thái '{status}'?")
        if not xac_nhan:
            return

        ok, res = hoa_don.lap_hoa_don(ma_kh, ma_nv, self.gio_hang, giam_gia=gg_tong, trang_thai=status)
        if ok:
            hd_moi = res
            messagebox.showinfo("Thành công", f"Đã lập hóa đơn {hd_moi['ma_hoa_don']} thành công!")

            # Hỏi xuất PDF
            in_pdf = messagebox.askyesno("Xuất PDF", "Bạn có muốn xuất hóa đơn ra file PDF ngay không?")
            if in_pdf:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialdir="bao_cao/pdf",
                    initialfile=f"HoaDon_{hd_moi['ma_hoa_don']}.pdf"
                )
                if file_path:
                    bao_cao.xuat_hoa_don_pdf(file_path, hd_moi["ma_hd"])
                    messagebox.showinfo("Thông báo", f"Đã xuất hóa đơn PDF thành công tại:\n{file_path}")

            # Dọn dẹp giỏ hàng và đồng bộ dữ liệu
            self.gio_hang = []
            self.cap_nhat_bang_gio_hang()
            self.load_sach_ban_hang()
            self.load_danh_sach_hoa_don()
            self.cap_nhat_dashboard()
            if hasattr(self, "load_bang_sach"):
                self.load_bang_sach()
            if hasattr(self, "load_lich_su"):
                self.load_lich_su()
        else:
            messagebox.showerror("Lập đơn thất bại", res)

    def load_danh_sach_hoa_don(self):
        ds_hd = hoa_don.lay_danh_sach_hoa_don()
        self.tree_all_hd.delete(*self.tree_all_hd.get_children())
        for hd in ds_hd:
            self.tree_all_hd.insert("", "end", values=(
                hd["ma_hd"], hd["ma_hoa_don"], hd["ngay_lap"],
                hd["ten_kh"], hd["ten_nv"], f"{hd['tong_tien']:,.0f}", hd["trang_thai"]
            ))

    def xuat_pdf_hoa_don_da_chon(self):
        sel = self.tree_all_hd.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hóa đơn từ bảng để xuất PDF!")
            return
        mhd = self.tree_all_hd.item(sel[0])["values"][0]
        mhd_code = self.tree_all_hd.item(sel[0])["values"][1]

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialdir="bao_cao/pdf",
            initialfile=f"HoaDon_{mhd_code}.pdf"
        )
        if file_path:
            bao_cao.xuat_hoa_don_pdf(file_path, mhd)
            messagebox.showinfo("Thành công", f"Đã xuất hóa đơn PDF thành công:\n{file_path}")

    def xu_ly_huy_hoa_don(self):
        sel = self.tree_all_hd.selection()
        if not sel:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hóa đơn cần hủy!")
            return

        vals = self.tree_all_hd.item(sel[0])["values"]
        mhd = vals[0]
        mhd_code = vals[1]
        tt_cu = vals[6]

        if tt_cu == "Đã hủy":
            messagebox.showwarning("Thông báo", "Hóa đơn này đã được hủy trước đó!")
            return

        xac_nhan = messagebox.askyesno("Cảnh báo hủy", f"Bạn có chắc muốn hủy hóa đơn {mhd_code}?\nNếu hóa đơn đã Hoàn thành, số lượng sách sẽ được HOÀN LẠI VÀO KHO.")
        if not xac_nhan:
            return

        ok, msg = hoa_don.huy_hoa_don(mhd, self.nhan_vien_hien_tai.get("ma_nv"), ly_do="Nhân viên hủy đơn")
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.load_danh_sach_hoa_don()
            self.load_sach_ban_hang()
            self.cap_nhat_dashboard()
            if hasattr(self, "load_bang_sach"):
                self.load_bang_sach()
            if hasattr(self, "load_lich_su"):
                self.load_lich_su()
        else:
            messagebox.showerror("Lỗi", msg)

    # ===================================================
    # 3. TAB QUẢN LÝ SÁCH
    # ===================================================
    def khoi_tao_tab_sach(self):
        f = tk.Frame(self.tab_sach, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        form = tk.LabelFrame(f, text="Thông tin chi tiết cuốn sách", font=("Segoe UI", 10, "bold"), bg="white", padx=12, pady=10)
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Mã sách:", bg="white").grid(row=0, column=0, sticky="w", pady=3)
        self.txt_sach_id = ttk.Entry(form, width=10, state="readonly")
        self.txt_sach_id.grid(row=0, column=1, sticky="w", pady=3)

        tk.Label(form, text="Tên sách (*):", bg="white").grid(row=0, column=2, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_ten = ttk.Entry(form, width=32)
        self.txt_sach_ten.grid(row=0, column=3, sticky="w", pady=3)

        tk.Label(form, text="Tác giả:", bg="white").grid(row=0, column=4, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_tacgia = ttk.Entry(form, width=22)
        self.txt_sach_tacgia.grid(row=0, column=5, sticky="w", pady=3)

        tk.Label(form, text="Thể loại (*):", bg="white").grid(row=1, column=0, sticky="w", pady=3)
        self.cb_sach_theloai = ttk.Combobox(form, state="readonly", width=16)
        self.cb_sach_theloai.grid(row=1, column=1, sticky="w", pady=3)
        self.load_combobox_the_loai()

        tk.Label(form, text="Nhà xuất bản:", bg="white").grid(row=1, column=2, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_nxb = ttk.Entry(form, width=32)
        self.txt_sach_nxb.grid(row=1, column=3, sticky="w", pady=3)

        tk.Label(form, text="Năm XB:", bg="white").grid(row=1, column=4, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_namxb = ttk.Entry(form, width=10)
        self.txt_sach_namxb.grid(row=1, column=5, sticky="w", pady=3)

        tk.Label(form, text="Giá nhập (*):", bg="white").grid(row=2, column=0, sticky="w", pady=3)
        self.txt_sach_gianhap = ttk.Entry(form, width=14)
        self.txt_sach_gianhap.grid(row=2, column=1, sticky="w", pady=3)

        tk.Label(form, text="Giá bán (*):", bg="white").grid(row=2, column=2, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_giaban = ttk.Entry(form, width=16)
        self.txt_sach_giaban.grid(row=2, column=3, sticky="w", pady=3)

        tk.Label(form, text="Tồn kho (*):", bg="white").grid(row=2, column=4, sticky="w", padx=(15, 0), pady=3)
        self.txt_sach_tonkho = ttk.Entry(form, width=12)
        self.txt_sach_tonkho.grid(row=2, column=5, sticky="w", pady=3)

        # Nút thao tác
        btn_bar = tk.Frame(form, bg="white")
        btn_bar.grid(row=3, column=0, columnspan=6, pady=10, sticky="w")
        ttk.Button(btn_bar, text="➕ Thêm Mới", style="Success.TButton", command=self.them_sach_moi).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="✏️ Cập Nhật", style="Primary.TButton", command=self.cap_nhat_sach_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="🗑️ Xóa", style="Danger.TButton", command=self.xoa_sach_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="Làm Mới Form", command=self.xoa_form_sach).pack(side="left", padx=5)
        ttk.Button(btn_bar, text="📦 Nhập Thêm Hàng", command=self.mo_hop_nhap_hang).pack(side="left", padx=15)

        # Thanh tìm kiếm
        filter_bar = tk.Frame(f, bg="#F4F6F9")
        filter_bar.pack(fill="x", pady=5)
        tk.Label(filter_bar, text="Tìm kiếm sách:", bg="#F4F6F9", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.txt_search_book = ttk.Entry(filter_bar, width=28)
        self.txt_search_book.pack(side="left", padx=8)
        ttk.Button(filter_bar, text="Tìm", command=self.load_bang_sach).pack(side="left")

        # Bảng sách
        b_cols = ("ma_sach", "ten_sach", "tac_gia", "the_loai", "gia_nhap", "gia_ban", "so_luong_ton", "trang_thai")
        self.tree_books = ttk.Treeview(f, columns=b_cols, show="headings", height=12)
        self.tree_books.heading("ma_sach", text="Mã")
        self.tree_books.heading("ten_sach", text="Tên sách")
        self.tree_books.heading("tac_gia", text="Tác giả")
        self.tree_books.heading("the_loai", text="Thể loại")
        self.tree_books.heading("gia_nhap", text="Giá nhập")
        self.tree_books.heading("gia_ban", text="Giá bán")
        self.tree_books.heading("so_luong_ton", text="Tồn kho")
        self.tree_books.heading("trang_thai", text="Trạng thái")

        self.tree_books.column("ma_sach", width=40, anchor="center")
        self.tree_books.column("ten_sach", width=230)
        self.tree_books.column("tac_gia", width=140)
        self.tree_books.column("the_loai", width=120)
        self.tree_books.column("gia_nhap", width=85, anchor="e")
        self.tree_books.column("gia_ban", width=85, anchor="e")
        self.tree_books.column("so_luong_ton", width=65, anchor="center")
        self.tree_books.column("trang_thai", width=110, anchor="center")
        self.tree_books.pack(fill="both", expand=True)

        self.tree_books.bind("<<TreeviewSelect>>", self.on_select_sach_row)
        self.load_bang_sach()

    def load_combobox_the_loai(self):
        tl_list = sach.lay_danh_sach_the_loai()
        self.tl_dict = {f"{t['ma_the_loai']} - {t['ten_the_loai']}": t['ma_the_loai'] for t in tl_list}
        self.cb_sach_theloai['values'] = list(self.tl_dict.keys())
        if self.tl_dict:
            self.cb_sach_theloai.current(0)

    def xoa_form_sach(self):
        self.txt_sach_id.config(state="normal")
        self.txt_sach_id.delete(0, tk.END)
        self.txt_sach_id.config(state="readonly")
        self.txt_sach_ten.delete(0, tk.END)
        self.txt_sach_tacgia.delete(0, tk.END)
        self.txt_sach_nxb.delete(0, tk.END)
        self.txt_sach_namxb.delete(0, tk.END)
        self.txt_sach_gianhap.delete(0, tk.END)
        self.txt_sach_giaban.delete(0, tk.END)
        self.txt_sach_tonkho.delete(0, tk.END)

    def on_select_sach_row(self, e):
        sel = self.tree_books.selection()
        if not sel:
            return
        m_sach = self.tree_books.item(sel[0])["values"][0]
        s_info = sach.tim_sach_theo_ma(m_sach)
        if not s_info:
            return

        self.xoa_form_sach()
        self.txt_sach_id.config(state="normal")
        self.txt_sach_id.insert(0, s_info.get("ma_sach"))
        self.txt_sach_id.config(state="readonly")
        self.txt_sach_ten.insert(0, s_info.get("ten_sach"))
        self.txt_sach_tacgia.insert(0, s_info.get("tac_gia"))
        self.txt_sach_nxb.insert(0, s_info.get("nha_xuat_ban"))
        self.txt_sach_namxb.insert(0, s_info.get("nam_xuat_ban"))
        self.txt_sach_gianhap.insert(0, s_info.get("gia_nhap"))
        self.txt_sach_giaban.insert(0, s_info.get("gia_ban"))
        self.txt_sach_tonkho.insert(0, s_info.get("so_luong_ton"))

        for k, v in self.tl_dict.items():
            if v == s_info.get("ma_the_loai"):
                self.cb_sach_theloai.set(k)
                break

    def load_bang_sach(self):
        kw = self.txt_search_book.get().strip()
        ds = sach.lay_danh_sach_sach(tu_khoa=kw)
        self.tree_books.delete(*self.tree_books.get_children())
        for s in ds:
            self.tree_books.insert("", "end", values=(
                s["ma_sach"], s["ten_sach"], s["tac_gia"], s["ten_the_loai"],
                f"{float(s['gia_nhap']):,.0f}", f"{float(s['gia_ban']):,.0f}",
                s["so_luong_ton"], s["trang_thai"]
            ))

    def them_sach_moi(self):
        ten = self.txt_sach_ten.get().strip()
        tg = self.txt_sach_tacgia.get().strip()
        nxb = self.txt_sach_nxb.get().strip()
        nam = self.txt_sach_namxb.get().strip() or "2024"
        g_nhap = self.txt_sach_gianhap.get().strip()
        g_ban = self.txt_sach_giaban.get().strip()
        sl = self.txt_sach_tonkho.get().strip()
        ma_tl = self.tl_dict.get(self.cb_sach_theloai.get(), "TL01")

        ok, res = sach.them_sach(ten, tg, nxb, ma_tl, nam, g_nhap, g_ban, sl)
        if ok:
            messagebox.showinfo("Thành công", "Đã thêm cuốn sách mới vào kho!")
            self.xoa_form_sach()
            self.load_bang_sach()
            self.load_sach_ban_hang()
            self.cap_nhat_dashboard()
        else:
            messagebox.showerror("Lỗi", res)

    def cap_nhat_sach_hien_tai(self):
        ms = self.txt_sach_id.get().strip()
        if not ms:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cuốn sách cần cập nhật!")
            return

        ten = self.txt_sach_ten.get().strip()
        tg = self.txt_sach_tacgia.get().strip()
        nxb = self.txt_sach_nxb.get().strip()
        nam = self.txt_sach_namxb.get().strip() or "2024"
        g_nhap = self.txt_sach_gianhap.get().strip()
        g_ban = self.txt_sach_giaban.get().strip()
        sl = self.txt_sach_tonkho.get().strip()
        ma_tl = self.tl_dict.get(self.cb_sach_theloai.get(), "TL01")

        ok, res = sach.cap_nhat_sach(ms, ten, tg, nxb, ma_tl, nam, g_nhap, g_ban, sl, 5, "Đang kinh doanh", "")
        if ok:
            messagebox.showinfo("Thành công", res)
            self.load_bang_sach()
            self.load_sach_ban_hang()
            self.cap_nhat_dashboard()
        else:
            messagebox.showerror("Lỗi", res)

    def xoa_sach_hien_tai(self):
        ms = self.txt_sach_id.get().strip()
        if not ms:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn cuốn sách cần xóa!")
            return

        xac_nhan = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa cuốn sách mã #{ms}?")
        if not xac_nhan:
            return

        ok, msg = sach.xoa_sach(ms)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.xoa_form_sach()
            self.load_bang_sach()
            self.load_sach_ban_hang()
            self.cap_nhat_dashboard()
        else:
            messagebox.showerror("Không thể xóa", msg)

    def mo_hop_nhap_hang(self):
        ms = self.txt_sach_id.get().strip()
        if not ms:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn sách cần nhập thêm hàng từ bảng trước!")
            return

        s_info = sach.tim_sach_theo_ma(ms)
        top = tk.Toplevel(self)
        top.title("Nhập thêm hàng vào kho")
        top.geometry("380x220")
        top.grab_set()

        tk.Label(top, text=f"Nhập thêm sách: {s_info.get('ten_sach')}", font=("Segoe UI", 10, "bold"), fg="#1F497D", wraplength=350).pack(pady=10)
        tk.Label(top, text=f"Số lượng tồn hiện tại: {s_info.get('so_luong_ton')} cuốn").pack()

        f_in = tk.Frame(top)
        f_in.pack(pady=10)
        tk.Label(f_in, text="Số lượng nhập thêm:").pack(side="left")
        sp_nhap = ttk.Spinbox(f_in, from_=1, to=1000, width=10)
        sp_nhap.set(10)
        sp_nhap.pack(side="left", padx=5)

        def do_nhap():
            try:
                sl_n = int(sp_nhap.get())
                ok, res = ton_kho.nhap_them_hang(ms, sl_n, self.nhan_vien_hien_tai.get("ma_nv"))
                if ok:
                    messagebox.showinfo("Thành công", f"Đã nhập thêm {sl_n} cuốn vào kho thành công!")
                    top.destroy()
                    self.load_bang_sach()
                    self.load_sach_ban_hang()
                    self.cap_nhat_dashboard()
                    if hasattr(self, "load_lich_su"):
                        self.load_lich_su()
                else:
                    messagebox.showerror("Lỗi", res)
            except ValueError:
                messagebox.showerror("Lỗi", "Số lượng nhập không hợp lệ!")

        ttk.Button(top, text="Xác nhận nhập kho", style="Success.TButton", command=do_nhap).pack(pady=10)

    # ===================================================
    # 4. TAB THỂ LOẠI SÁCH
    # ===================================================
    def khoi_tao_tab_the_loai(self):
        f = tk.Frame(self.tab_the_loai, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        form = tk.LabelFrame(f, text="Quản lý thể loại sách", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=10)
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Mã thể loại (Tự động):", bg="white").grid(row=0, column=0, sticky="w", pady=4)
        self.txt_tl_id = ttk.Entry(form, width=15, state="readonly")
        self.txt_tl_id.grid(row=0, column=1, pady=4, padx=5)

        tk.Label(form, text="Tên thể loại (*):", bg="white").grid(row=0, column=2, sticky="w", padx=(15, 0), pady=4)
        self.txt_tl_ten = ttk.Entry(form, width=28)
        self.txt_tl_ten.grid(row=0, column=3, pady=4, padx=5)

        tk.Label(form, text="Mô tả:", bg="white").grid(row=0, column=4, sticky="w", padx=(15, 0), pady=4)
        self.txt_tl_mota = ttk.Entry(form, width=35)
        self.txt_tl_mota.grid(row=0, column=5, pady=4, padx=5)

        btn_box = tk.Frame(form, bg="white")
        btn_box.grid(row=1, column=0, columnspan=6, pady=10, sticky="w")
        ttk.Button(btn_box, text="➕ Thêm Mới", style="Success.TButton", command=self.them_the_loai_moi).pack(side="left", padx=5)
        ttk.Button(btn_box, text="✏️ Cập Nhật", style="Primary.TButton", command=self.cap_nhat_the_loai_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="🗑️ Xóa", style="Danger.TButton", command=self.xoa_the_loai_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Làm Mới Form", command=self.xoa_form_the_loai).pack(side="left", padx=5)

        tl_cols = ("ma_the_loai", "ten_the_loai", "mo_ta", "trang_thai")
        self.tree_the_loai = ttk.Treeview(f, columns=tl_cols, show="headings", height=14)
        self.tree_the_loai.heading("ma_the_loai", text="Mã thể loại")
        self.tree_the_loai.heading("ten_the_loai", text="Tên thể loại")
        self.tree_the_loai.heading("mo_ta", text="Mô tả")
        self.tree_the_loai.heading("trang_thai", text="Trạng thái")

        self.tree_the_loai.column("ma_the_loai", width=120, anchor="center")
        self.tree_the_loai.column("ten_the_loai", width=250)
        self.tree_the_loai.column("mo_ta", width=400)
        self.tree_the_loai.column("trang_thai", width=130, anchor="center")
        self.tree_the_loai.pack(fill="both", expand=True)

        self.tree_the_loai.bind("<<TreeviewSelect>>", self.on_select_tl_row)
        self.load_bang_the_loai()

    def xoa_form_the_loai(self):
        self.txt_tl_id.config(state="normal")
        self.txt_tl_id.delete(0, tk.END)
        self.txt_tl_id.config(state="readonly")
        self.txt_tl_ten.delete(0, tk.END)
        self.txt_tl_mota.delete(0, tk.END)

    def on_select_tl_row(self, e):
        sel = self.tree_the_loai.selection()
        if not sel:
            return
        vals = self.tree_the_loai.item(sel[0])["values"]
        self.xoa_form_the_loai()
        self.txt_tl_id.config(state="normal")
        self.txt_tl_id.insert(0, vals[0])
        self.txt_tl_id.config(state="readonly")
        self.txt_tl_ten.insert(0, vals[1])
        self.txt_tl_mota.insert(0, vals[2] if vals[2] else "")

    def load_bang_the_loai(self):
        ds = sach.lay_danh_sach_the_loai()
        self.tree_the_loai.delete(*self.tree_the_loai.get_children())
        for tl in ds:
            self.tree_the_loai.insert("", "end", values=(
                tl["ma_the_loai"], tl["ten_the_loai"], tl["mo_ta"], tl["trang_thai"]
            ))

    def them_the_loai_moi(self):
        ten = self.txt_tl_ten.get().strip()
        mota = self.txt_tl_mota.get().strip()
        ok, res = sach.them_the_loai(ten, mota)
        if ok:
            messagebox.showinfo("Thành công", f"Đã thêm thể loại mới thành công với mã: {res['ma_the_loai']}!")
            self.xoa_form_the_loai()
            self.load_bang_the_loai()
            self.load_combobox_the_loai()
        else:
            messagebox.showerror("Lỗi", res)

    def cap_nhat_the_loai_hien_tai(self):
        mid = self.txt_tl_id.get().strip()
        if not mid:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thể loại cần cập nhật từ danh sách!")
            return
        ten = self.txt_tl_ten.get().strip()
        mota = self.txt_tl_mota.get().strip()
        ok, res = sach.cap_nhat_the_loai(mid, ten, mota, "Hoạt động")
        if ok:
            messagebox.showinfo("Thành công", res)
            self.load_bang_the_loai()
            self.load_combobox_the_loai()
            if hasattr(self, "load_bang_sach"):
                self.load_bang_sach()
        else:
            messagebox.showerror("Lỗi", res)

    def xoa_the_loai_hien_tai(self):
        mid = self.txt_tl_id.get().strip()
        if not mid:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn thể loại cần xóa từ danh sách!")
            return

        xac_nhan = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa thể loại '{mid}'?")
        if not xac_nhan:
            return

        ok, msg = sach.xoa_the_loai(mid)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.xoa_form_the_loai()
            self.load_bang_the_loai()
            self.load_combobox_the_loai()
        else:
            messagebox.showerror("Không thể xóa", msg)

    # ===================================================
    # 5. TAB QUẢN LÝ KHÁCH HÀNG
    # ===================================================
    def khoi_tao_tab_khach_hang(self):
        f = tk.Frame(self.tab_khach_hang, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        form = tk.LabelFrame(f, text="Thông tin khách hàng", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=10)
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Mã KH:", bg="white").grid(row=0, column=0, sticky="w", pady=4)
        self.txt_kh_id = ttk.Entry(form, width=10, state="readonly")
        self.txt_kh_id.grid(row=0, column=1, pady=4, padx=5)

        tk.Label(form, text="Họ và tên (*):", bg="white").grid(row=0, column=2, sticky="w", padx=(15, 0), pady=4)
        self.txt_kh_ten = ttk.Entry(form, width=28)
        self.txt_kh_ten.grid(row=0, column=3, pady=4, padx=5)

        tk.Label(form, text="Số điện thoại:", bg="white").grid(row=0, column=4, sticky="w", padx=(15, 0), pady=4)
        self.txt_kh_sdt = ttk.Entry(form, width=18)
        self.txt_kh_sdt.grid(row=0, column=5, pady=4, padx=5)

        tk.Label(form, text="Địa chỉ:", bg="white").grid(row=1, column=0, sticky="w", pady=4)
        self.txt_kh_diachi = ttk.Entry(form, width=45)
        self.txt_kh_diachi.grid(row=1, column=1, columnspan=3, pady=4, padx=5, sticky="w")

        btn_box = tk.Frame(form, bg="white")
        btn_box.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")
        ttk.Button(btn_box, text="➕ Thêm Khách Hàng", style="Success.TButton", command=self.them_khach_hang_moi).pack(side="left", padx=5)
        ttk.Button(btn_box, text="✏️ Cập Nhật", style="Primary.TButton", command=self.cap_nhat_khach_hang_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="🗑️ Xóa", style="Danger.TButton", command=self.xoa_khach_hang_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Làm Mới Form", command=self.xoa_form_khach_hang).pack(side="left", padx=5)

        # Thanh tìm kiếm
        filter_bar = tk.Frame(f, bg="#F4F6F9")
        filter_bar.pack(fill="x", pady=5)
        tk.Label(filter_bar, text="Tìm kiếm khách:", bg="#F4F6F9", font=("Segoe UI", 10, "bold")).pack(side="left")
        self.txt_search_kh = ttk.Entry(filter_bar, width=28)
        self.txt_search_kh.pack(side="left", padx=8)
        ttk.Button(filter_bar, text="Tìm", command=self.load_bang_khach_hang).pack(side="left")

        kh_cols = ("ma_kh", "ma_khach_hang", "ho_ten", "so_dien_thoai", "dia_chi", "ngay_tao")
        self.tree_khach_hang = ttk.Treeview(f, columns=kh_cols, show="headings", height=13)
        self.tree_khach_hang.heading("ma_kh", text="ID")
        self.tree_khach_hang.heading("ma_khach_hang", text="Mã KH")
        self.tree_khach_hang.heading("ho_ten", text="Họ và tên")
        self.tree_khach_hang.heading("so_dien_thoai", text="Số điện thoại")
        self.tree_khach_hang.heading("dia_chi", text="Địa chỉ")
        self.tree_khach_hang.heading("ngay_tao", text="Ngày tạo")

        self.tree_khach_hang.column("ma_kh", width=50, anchor="center")
        self.tree_khach_hang.column("ma_khach_hang", width=90, anchor="center")
        self.tree_khach_hang.column("ho_ten", width=220)
        self.tree_khach_hang.column("so_dien_thoai", width=140)
        self.tree_khach_hang.column("dia_chi", width=300)
        self.tree_khach_hang.column("ngay_tao", width=110, anchor="center")
        self.tree_khach_hang.pack(fill="both", expand=True)

        self.tree_khach_hang.bind("<<TreeviewSelect>>", self.on_select_kh_row)
        self.load_bang_khach_hang()

    def xoa_form_khach_hang(self):
        self.txt_kh_id.config(state="normal")
        self.txt_kh_id.delete(0, tk.END)
        self.txt_kh_id.config(state="readonly")
        self.txt_kh_ten.delete(0, tk.END)
        self.txt_kh_sdt.delete(0, tk.END)
        self.txt_kh_diachi.delete(0, tk.END)

    def on_select_kh_row(self, e):
        sel = self.tree_khach_hang.selection()
        if not sel:
            return
        vals = self.tree_khach_hang.item(sel[0])["values"]
        self.xoa_form_khach_hang()
        self.txt_kh_id.config(state="normal")
        self.txt_kh_id.insert(0, vals[0])
        self.txt_kh_id.config(state="readonly")
        self.txt_kh_ten.insert(0, vals[2])
        self.txt_kh_sdt.insert(0, vals[3] if vals[3] else "")
        self.txt_kh_diachi.insert(0, vals[4] if vals[4] else "")

    def load_bang_khach_hang(self):
        kw = self.txt_search_kh.get().strip()
        ds = khach_hang.lay_danh_sach_khach_hang(tu_khoa=kw)
        self.tree_khach_hang.delete(*self.tree_khach_hang.get_children())
        for k in ds:
            self.tree_khach_hang.insert("", "end", values=(
                k["ma_kh"], k["ma_khach_hang"], k["ho_ten"], k["so_dien_thoai"], k["dia_chi"], k["ngay_tao"]
            ))

    def them_khach_hang_moi(self):
        ten = self.txt_kh_ten.get().strip()
        sdt = self.txt_kh_sdt.get().strip()
        dc = self.txt_kh_diachi.get().strip()
        ok, res = khach_hang.them_khach_hang(ten, sdt, "", dc)
        if ok:
            messagebox.showinfo("Thành công", "Đã thêm khách hàng thành công!")
            self.xoa_form_khach_hang()
            self.load_bang_khach_hang()
            self.load_combobox_khach_hang()
        else:
            messagebox.showerror("Lỗi", res)

    def cap_nhat_khach_hang_hien_tai(self):
        mkh = self.txt_kh_id.get().strip()
        if not mkh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần cập nhật!")
            return
        ten = self.txt_kh_ten.get().strip()
        sdt = self.txt_kh_sdt.get().strip()
        dc = self.txt_kh_diachi.get().strip()
        ok, res = khach_hang.cap_nhat_khach_hang(mkh, ten, sdt, "", dc, "Hoạt động")
        if ok:
            messagebox.showinfo("Thành công", res)
            self.load_bang_khach_hang()
            self.load_combobox_khach_hang()
        else:
            messagebox.showerror("Lỗi", res)

    def xoa_khach_hang_hien_tai(self):
        mkh = self.txt_kh_id.get().strip()
        if not mkh:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn khách hàng cần xóa!")
            return

        xac_nhan = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa khách hàng ID #{mkh}?")
        if not xac_nhan:
            return

        ok, msg = khach_hang.xoa_khach_hang(mkh)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.xoa_form_khach_hang()
            self.load_bang_khach_hang()
            self.load_combobox_khach_hang()
        else:
            messagebox.showerror("Không thể xóa", msg)

    # ===================================================
    # 6. TAB QUẢN LÝ NHÂN VIÊN
    # ===================================================
    def khoi_tao_tab_nhan_vien(self):
        f = tk.Frame(self.tab_nhan_vien, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        form = tk.LabelFrame(f, text="Quản lý thông tin nhân viên", font=("Segoe UI", 10, "bold"), bg="white", padx=15, pady=10)
        form.pack(fill="x", pady=(0, 10))

        tk.Label(form, text="Mã NV:", bg="white").grid(row=0, column=0, sticky="w", pady=4)
        self.txt_nv_id = ttk.Entry(form, width=10, state="readonly")
        self.txt_nv_id.grid(row=0, column=1, pady=4, padx=5)

        tk.Label(form, text="Họ tên (*):", bg="white").grid(row=0, column=2, sticky="w", padx=(15, 0), pady=4)
        self.txt_nv_hoten = ttk.Entry(form, width=26)
        self.txt_nv_hoten.grid(row=0, column=3, pady=4, padx=5)

        tk.Label(form, text="SĐT:", bg="white").grid(row=0, column=4, sticky="w", padx=(15, 0), pady=4)
        self.txt_nv_sdt = ttk.Entry(form, width=18)
        self.txt_nv_sdt.grid(row=0, column=5, pady=4, padx=5)

        tk.Label(form, text="Tài khoản (*):", bg="white").grid(row=1, column=0, sticky="w", pady=4)
        self.txt_nv_user = ttk.Entry(form, width=18)
        self.txt_nv_user.grid(row=1, column=1, pady=4, padx=5)

        tk.Label(form, text="Mật khẩu (*):", bg="white").grid(row=1, column=2, sticky="w", padx=(15, 0), pady=4)
        self.txt_nv_pass = ttk.Entry(form, width=26, show="*")
        self.txt_nv_pass.grid(row=1, column=3, pady=4, padx=5)

        tk.Label(form, text="Trạng thái:", bg="white").grid(row=1, column=4, sticky="w", padx=(15, 0), pady=4)
        self.cb_nv_status = ttk.Combobox(form, state="readonly", values=["Hoạt động", "Đã nghỉ việc"], width=15)
        self.cb_nv_status.current(0)
        self.cb_nv_status.grid(row=1, column=5, pady=4, padx=5)

        btn_box = tk.Frame(form, bg="white")
        btn_box.grid(row=2, column=0, columnspan=6, pady=10, sticky="w")
        ttk.Button(btn_box, text="➕ Thêm Nhân Viên", style="Success.TButton", command=self.them_nhan_vien_moi).pack(side="left", padx=5)
        ttk.Button(btn_box, text="✏️ Cập Nhật", style="Primary.TButton", command=self.cap_nhat_nhan_vien_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="🗑️ Xóa", style="Danger.TButton", command=self.xoa_nhan_vien_hien_tai).pack(side="left", padx=5)
        ttk.Button(btn_box, text="Làm Mới Form", command=self.xoa_form_nhan_vien).pack(side="left", padx=5)

        nv_cols = ("ma_nv", "ma_nhan_vien", "ho_ten", "so_dien_thoai", "ten_dang_nhap", "trang_thai")
        self.tree_nhan_vien = ttk.Treeview(f, columns=nv_cols, show="headings", height=13)
        self.tree_nhan_vien.heading("ma_nv", text="ID")
        self.tree_nhan_vien.heading("ma_nhan_vien", text="Mã NV")
        self.tree_nhan_vien.heading("ho_ten", text="Họ và tên")
        self.tree_nhan_vien.heading("so_dien_thoai", text="Số điện thoại")
        self.tree_nhan_vien.heading("ten_dang_nhap", text="Tên tài khoản")
        self.tree_nhan_vien.heading("trang_thai", text="Trạng thái")

        self.tree_nhan_vien.column("ma_nv", width=50, anchor="center")
        self.tree_nhan_vien.column("ma_nhan_vien", width=90, anchor="center")
        self.tree_nhan_vien.column("ho_ten", width=230)
        self.tree_nhan_vien.column("so_dien_thoai", width=140)
        self.tree_nhan_vien.column("ten_dang_nhap", width=160)
        self.tree_nhan_vien.column("trang_thai", width=120, anchor="center")
        self.tree_nhan_vien.pack(fill="both", expand=True)

        self.tree_nhan_vien.bind("<<TreeviewSelect>>", self.on_select_nv_row)
        self.load_bang_nhan_vien()

    def xoa_form_nhan_vien(self):
        self.txt_nv_id.config(state="normal")
        self.txt_nv_id.delete(0, tk.END)
        self.txt_nv_id.config(state="readonly")
        self.txt_nv_hoten.delete(0, tk.END)
        self.txt_nv_sdt.delete(0, tk.END)
        self.txt_nv_user.config(state="normal")
        self.txt_nv_user.delete(0, tk.END)
        self.txt_nv_pass.delete(0, tk.END)
        self.cb_nv_status.current(0)

    def on_select_nv_row(self, e):
        sel = self.tree_nhan_vien.selection()
        if not sel:
            return
        vals = self.tree_nhan_vien.item(sel[0])["values"]
        self.xoa_form_nhan_vien()
        self.txt_nv_id.config(state="normal")
        self.txt_nv_id.insert(0, vals[0])
        self.txt_nv_id.config(state="readonly")
        self.txt_nv_hoten.insert(0, vals[2])
        self.txt_nv_sdt.insert(0, vals[3] if vals[3] else "")
        self.txt_nv_user.insert(0, vals[4])
        self.txt_nv_user.config(state="readonly")
        self.cb_nv_status.set(vals[5])

    def load_bang_nhan_vien(self):
        ds = nhan_vien.lay_danh_sach_nhan_vien()
        self.tree_nhan_vien.delete(*self.tree_nhan_vien.get_children())
        for n in ds:
            self.tree_nhan_vien.insert("", "end", values=(
                n["ma_nv"], n["ma_nhan_vien"], n["ho_ten"], n["so_dien_thoai"], n["ten_dang_nhap"], n["trang_thai"]
            ))

    def them_nhan_vien_moi(self):
        ten = self.txt_nv_hoten.get().strip()
        sdt = self.txt_nv_sdt.get().strip()
        user = self.txt_nv_user.get().strip()
        pwd = self.txt_nv_pass.get().strip()
        tt = self.cb_nv_status.get()
        ok, res = nhan_vien.them_nhan_vien(ten, "", "", sdt, "", "", user, pwd, trang_thai=tt)
        if ok:
            messagebox.showinfo("Thành công", "Đã thêm nhân viên mới thành công!")
            self.xoa_form_nhan_vien()
            self.load_bang_nhan_vien()
        else:
            messagebox.showerror("Lỗi", res)

    def cap_nhat_nhan_vien_hien_tai(self):
        mnv = self.txt_nv_id.get().strip()
        if not mnv:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên từ bảng!")
            return
        ten = self.txt_nv_hoten.get().strip()
        sdt = self.txt_nv_sdt.get().strip()
        pwd = self.txt_nv_pass.get().strip()
        tt = self.cb_nv_status.get()
        ok, res = nhan_vien.cap_nhat_nhan_vien(mnv, ten, "", "", sdt, "", "", pwd, tt)
        if ok:
            messagebox.showinfo("Thành công", res)
            self.load_bang_nhan_vien()
        else:
            messagebox.showerror("Lỗi", res)

    def xoa_nhan_vien_hien_tai(self):
        mnv = self.txt_nv_id.get().strip()
        if not mnv:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn nhân viên cần xóa!")
            return
        if str(mnv) == str(self.nhan_vien_hien_tai.get("ma_nv")):
            messagebox.showerror("Lỗi", "Không thể xóa tài khoản bạn đang đăng nhập trực!")
            return

        xac_nhan = messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc muốn xóa nhân viên ID #{mnv}?")
        if not xac_nhan:
            return

        ok, msg = nhan_vien.xoa_nhan_vien(mnv)
        if ok:
            messagebox.showinfo("Thành công", msg)
            self.xoa_form_nhan_vien()
            self.load_bang_nhan_vien()
        else:
            messagebox.showerror("Không thể xóa", msg)

    # ===================================================
    # 7. TAB LỊCH SỬ TỒN KHO
    # ===================================================
    def khoi_tao_tab_lich_su(self):
        f = tk.Frame(self.tab_lich_su, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        top_f = tk.Frame(f, bg="#F4F6F9")
        top_f.pack(fill="x", pady=(0, 8))
        ttk.Button(top_f, text="🔄 Làm Mới Nhật Ký", command=self.load_lich_su).pack(side="left")
        tk.Label(top_f, text=" (Ghi nhận tự động: Bán hàng, Hoàn kho khi hủy đơn, Nhập hàng)", bg="#F4F6F9", font=("Segoe UI", 9, "italic")).pack(side="left", padx=10)

        cols = ("ma_ls", "thoi_gian", "ten_sach", "loai_giao_dich", "so_luong_thay_doi", "ton_truoc", "ton_sau", "ten_nhan_vien", "ghi_chu")
        self.tree_lich_su = ttk.Treeview(f, columns=cols, show="headings", height=16)
        self.tree_lich_su.heading("ma_ls", text="Mã")
        self.tree_lich_su.heading("thoi_gian", text="Thời gian")
        self.tree_lich_su.heading("ten_sach", text="Tựa sách")
        self.tree_lich_su.heading("loai_giao_dich", text="Loại biến động")
        self.tree_lich_su.heading("so_luong_thay_doi", text="Biến động")
        self.tree_lich_su.heading("ton_truoc", text="Tồn trước")
        self.tree_lich_su.heading("ton_sau", text="Tồn sau")
        self.tree_lich_su.heading("ten_nhan_vien", text="Nhân viên")
        self.tree_lich_su.heading("ghi_chu", text="Ghi chú")

        self.tree_lich_su.column("ma_ls", width=40, anchor="center")
        self.tree_lich_su.column("thoi_gian", width=140, anchor="center")
        self.tree_lich_su.column("ten_sach", width=220)
        self.tree_lich_su.column("loai_giao_dich", width=110, anchor="center")
        self.tree_lich_su.column("so_luong_thay_doi", width=80, anchor="center")
        self.tree_lich_su.column("ton_truoc", width=70, anchor="center")
        self.tree_lich_su.column("ton_sau", width=70, anchor="center")
        self.tree_lich_su.column("ten_nhan_vien", width=160)
        self.tree_lich_su.column("ghi_chu", width=200)
        self.tree_lich_su.pack(fill="both", expand=True)

        self.load_lich_su()

    def load_lich_su(self):
        ds = ton_kho.lay_lich_su_ton_kho()
        self.tree_lich_su.delete(*self.tree_lich_su.get_children())
        for row in ds:
            self.tree_lich_su.insert("", "end", values=(
                row["ma_ls"], row["thoi_gian"], row["ten_sach"], row["loai_giao_dich"],
                row["so_luong_thay_doi"], row["ton_truoc"], row["ton_sau"],
                row["ten_nhan_vien"], row["ghi_chu"]
            ))

    # ===================================================
    # 8. TAB BÁO CÁO - THỐNG KÊ
    # ===================================================
    def khoi_tao_tab_bao_cao(self):
        f = tk.Frame(self.tab_bao_cao, bg="#F4F6F9", padx=10, pady=10)
        f.pack(fill="both", expand=True)

        bar = tk.Frame(f, bg="#F4F6F9")
        bar.pack(fill="x", pady=(0, 10))

        ttk.Button(bar, text="🔄 Cập Nhật Dữ Liệu Báo Cáo", command=self.load_tat_ca_bao_cao).pack(side="left")
        ttk.Button(bar, text="📊 Xuất Báo Cáo Toàn Diện (Excel)", style="Success.TButton", command=self.xuat_excel_nhanh).pack(side="left", padx=15)

        sub_nb = ttk.Notebook(f)
        sub_nb.pack(fill="both", expand=True)

        # Tab con 1: Doanh thu theo ngày
        t_rev = ttk.Frame(sub_nb)
        sub_nb.add(t_rev, text=" Doanh Thu Theo Ngày & Tháng ")
        cols_r = ("ngay", "so_don", "doanh_thu")
        self.tree_rev = ttk.Treeview(t_rev, columns=cols_r, show="headings", height=12)
        self.tree_rev.heading("ngay", text="Thời gian (Ngày)")
        self.tree_rev.heading("so_don", text="Số hóa đơn hoàn thành")
        self.tree_rev.heading("doanh_thu", text="Tổng doanh thu (VNĐ)")
        self.tree_rev.column("ngay", width=160, anchor="center")
        self.tree_rev.column("so_don", width=160, anchor="center")
        self.tree_rev.column("doanh_thu", width=220, anchor="e")
        self.tree_rev.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab con 2: Top sách bán chạy
        t_top = ttk.Frame(sub_nb)
        sub_nb.add(t_top, text=" Top Sách Bán Chạy Nhất ")
        cols_top = ("ma_sach", "ten_sach", "the_loai", "so_luong_ban", "tong_tien")
        self.tree_top = ttk.Treeview(t_top, columns=cols_top, show="headings", height=12)
        self.tree_top.heading("ma_sach", text="Mã")
        self.tree_top.heading("ten_sach", text="Tên sách")
        self.tree_top.heading("the_loai", text="Thể loại")
        self.tree_top.heading("so_luong_ban", text="Số cuốn đã bán")
        self.tree_top.heading("tong_tien", text="Tổng tiền thu (VNĐ)")
        self.tree_top.column("ma_sach", width=50, anchor="center")
        self.tree_top.column("ten_sach", width=260)
        self.tree_top.column("the_loai", width=140)
        self.tree_top.column("so_luong_ban", width=120, anchor="center")
        self.tree_top.column("tong_tien", width=180, anchor="e")
        self.tree_top.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab con 3: Cảnh báo tồn kho
        t_warn = ttk.Frame(sub_nb)
        sub_nb.add(t_warn, text=" ⚠️ Cảnh Báo Sách Sắp Hết Hàng ")
        cols_w = ("ma_sach", "ten_sach", "tac_gia", "the_loai", "so_luong_ton", "muc_ton_toi_thieu")
        self.tree_warn = ttk.Treeview(t_warn, columns=cols_w, show="headings", height=12)
        self.tree_warn.heading("ma_sach", text="Mã")
        self.tree_warn.heading("ten_sach", text="Tên sách")
        self.tree_warn.heading("tac_gia", text="Tác giả")
        self.tree_warn.heading("the_loai", text="Thể loại")
        self.tree_warn.heading("so_luong_ton", text="Tồn kho thực tế")
        self.tree_warn.heading("muc_ton_toi_thieu", text="Mức tối thiểu")
        self.tree_warn.column("ma_sach", width=50, anchor="center")
        self.tree_warn.column("ten_sach", width=260)
        self.tree_warn.column("tac_gia", width=160)
        self.tree_warn.column("the_loai", width=130)
        self.tree_warn.column("so_luong_ton", width=130, anchor="center")
        self.tree_warn.column("muc_ton_toi_thieu", width=110, anchor="center")
        self.tree_warn.pack(fill="both", expand=True, padx=5, pady=5)

        # Tab con 4: Doanh số nhân viên
        t_emp = ttk.Frame(sub_nb)
        sub_nb.add(t_emp, text=" Doanh Số Theo Nhân Viên ")
        cols_e = ("ma_nhan_vien", "ho_ten", "ten_dang_nhap", "so_don", "doanh_thu")
        self.tree_emp_stat = ttk.Treeview(t_emp, columns=cols_e, show="headings", height=12)
        self.tree_emp_stat.heading("ma_nhan_vien", text="Mã NV")
        self.tree_emp_stat.heading("ho_ten", text="Họ tên nhân viên")
        self.tree_emp_stat.heading("ten_dang_nhap", text="Tài khoản")
        self.tree_emp_stat.heading("so_don", text="Số hóa đơn lập")
        self.tree_emp_stat.heading("doanh_thu", text="Tổng tiền thu (VNĐ)")
        self.tree_emp_stat.column("ma_nhan_vien", width=80, anchor="center")
        self.tree_emp_stat.column("ho_ten", width=220)
        self.tree_emp_stat.column("ten_dang_nhap", width=150)
        self.tree_emp_stat.column("so_don", width=120, anchor="center")
        self.tree_emp_stat.column("doanh_thu", width=180, anchor="e")
        self.tree_emp_stat.pack(fill="both", expand=True, padx=5, pady=5)

        self.load_tat_ca_bao_cao()

    def load_tat_ca_bao_cao(self):
        # 1. Doanh thu theo ngày
        rev = bao_cao.thong_ke_doanh_thu()
        self.tree_rev.delete(*self.tree_rev.get_children())
        for r in rev["theo_ngay"]:
            self.tree_rev.insert("", "end", values=(r["ngay"], r["so_don"], f"{r['doanh_thu']:,.0f}"))

        # 2. Top bán chạy
        top = bao_cao.thong_ke_sach_ban_chay(15)
        self.tree_top.delete(*self.tree_top.get_children())
        for t in top:
            self.tree_top.insert("", "end", values=(
                t["ma_sach"], t["ten_sach"], t["the_loai"], t["so_luong_ban"], f"{t['tong_tien']:,.0f}"
            ))

        # 3. Cảnh báo tồn
        low = bao_cao.thong_ke_sach_ton_kho_canh_bao()
        self.tree_warn.delete(*self.tree_warn.get_children())
        for w in low:
            self.tree_warn.insert("", "end", values=(
                w["ma_sach"], w["ten_sach"], w.get("tac_gia", ""), w.get("ten_the_loai", ""),
                f"🚨 {w.get('so_luong_ton')} cuốn", w.get("muc_ton_toi_thieu", 5)
            ))

        # 4. Doanh số nhân viên
        emp = bao_cao.thong_ke_doanh_so_nhan_vien()
        self.tree_emp_stat.delete(*self.tree_emp_stat.get_children())
        for e in emp:
            self.tree_emp_stat.insert("", "end", values=(
                e["ma_nhan_vien"], e["ho_ten"], e["ten_dang_nhap"], e["so_don"], f"{e['doanh_thu']:,.0f}"
            ))


if __name__ == "__main__":
    app = QuanLyBanSachApp()
    app.mainloop()
