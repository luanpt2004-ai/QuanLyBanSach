import sqlite3
import os
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "quanlybansach.db")


def get_connection():
    """Tạo và trả về kết nối tới CSDL SQLite, bật hỗ trợ Foreign Key."""
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Khởi tạo cấu trúc các bảng theo đúng đặc tả tài liệu đề tài."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Bảng Sach (Quản lý kho hàng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Sach (
            MaSach INTEGER PRIMARY KEY AUTOINCREMENT,
            TenSach TEXT NOT NULL,
            TacGia TEXT,
            TheLoai TEXT,
            GiaBan REAL NOT NULL CHECK(GiaBan >= 0),
            TonKho INTEGER NOT NULL DEFAULT 0 CHECK(TonKho >= 0)
        );
    """)

    # 2. Bảng NhanVien (Quản lý nội bộ & Tài khoản)
    # VaiTro: 1: Quản lý (Admin), 0: Nhân viên bán hàng
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS NhanVien (
            MaNV INTEGER PRIMARY KEY AUTOINCREMENT,
            TenNV TEXT NOT NULL,
            SoDienThoai TEXT,
            TenDangNhap TEXT UNIQUE NOT NULL,
            MatKhau TEXT NOT NULL,
            VaiTro INTEGER NOT NULL DEFAULT 0 CHECK(VaiTro IN (0, 1))
        );
    """)

    # 3. Bảng KhachHang (Chăm sóc khách hàng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS KhachHang (
            MaKH INTEGER PRIMARY KEY AUTOINCREMENT,
            TenKH TEXT NOT NULL,
            SoDienThoai TEXT,
            DiaChi TEXT
        );
    """)

    # 4. Bảng HoaDon (Quản lý giao dịch)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS HoaDon (
            MaHD INTEGER PRIMARY KEY AUTOINCREMENT,
            MaKH INTEGER,
            MaNV INTEGER NOT NULL,
            NgayLap TEXT NOT NULL,
            TongTien REAL NOT NULL DEFAULT 0,
            FOREIGN KEY (MaKH) REFERENCES KhachHang(MaKH) ON DELETE SET NULL,
            FOREIGN KEY (MaNV) REFERENCES NhanVien(MaNV) ON DELETE RESTRICT
        );
    """)

    # 5. Bảng ChiTietHoaDon (Quản lý giỏ hàng)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ChiTietHoaDon (
            MaCTHD INTEGER PRIMARY KEY AUTOINCREMENT,
            MaHD INTEGER NOT NULL,
            MaSach INTEGER NOT NULL,
            SoLuong INTEGER NOT NULL CHECK(SoLuong > 0),
            GiaMua REAL NOT NULL CHECK(GiaMua >= 0),
            FOREIGN KEY (MaHD) REFERENCES HoaDon(MaHD) ON DELETE CASCADE,
            FOREIGN KEY (MaSach) REFERENCES Sach(MaSach) ON DELETE RESTRICT
        );
    """)

    conn.commit()
    seed_initial_data(conn)
    conn.close()


def seed_initial_data(conn):
    """Nạp dữ liệu mẫu ban đầu nếu bảng còn trống để kiểm thử thuận tiện."""
    cursor = conn.cursor()

    # Thêm tài khoản quản lý và nhân viên mẫu nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM NhanVien")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO NhanVien (TenNV, SoDienThoai, TenDangNhap, MatKhau, VaiTro)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("Quản Lý Nguyễn", "0901234567", "admin", "admin123", 1),
            ("Nhân Viên Trần", "0912345678", "nhanvien", "123456", 0),
        ])

    # Thêm danh mục sách mẫu nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM Sach")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO Sach (TenSach, TacGia, TheLoai, GiaBan, TonKho)
            VALUES (?, ?, ?, ?, ?)
        """, [
            ("Lập trình Python cơ bản đến nâng cao", "Nguyễn Văn A", "Công nghệ thông tin", 125000, 50),
            ("Cấu trúc dữ liệu và giải thuật", "Trần Đình C", "Công nghệ thông tin", 150000, 30),
            ("Đắc Nhân Tâm", "Dale Carnegie", "Kỹ năng sống", 85000, 100),
            ("Nhà Giả Kim", "Paulo Coelho", "Văn học", 79000, 80),
            ("Kinh Tế Học Hài Hước", "Steven Levitt", "Kinh tế", 110000, 25),
            ("Mắt Biếc", "Nguyễn Nhật Ánh", "Văn học", 95000, 4),  # Tồn kho thấp để test cảnh báo
            ("Lược Sử Thời Gian", "Stephen Hawking", "Khoa học", 135000, 3) # Tồn kho thấp
        ])

    # Thêm khách hàng mẫu nếu chưa có
    cursor.execute("SELECT COUNT(*) FROM KhachHang")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO KhachHang (TenKH, SoDienThoai, DiaChi)
            VALUES (?, ?, ?)
        """, [
            ("Khách vãng lai", "", ""),
            ("Lê Hoàng Nam", "0987654321", "Ninh Kiều, Cần Thơ"),
            ("Phạm Minh Thư", "0977889900", "Bình Thủy, Cần Thơ")
        ])

    conn.commit()


# ==========================================
# CÁC HÀM XỬ LÝ NGHIỆP VỤ (DATABASE SERVICES)
# ==========================================

# 1. Nghiệp vụ Xác thực & Người dùng
def authenticate(ten_dang_nhap, mat_khau):
    """Xác thực đăng nhập người dùng."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MaNV, TenNV, SoDienThoai, TenDangNhap, VaiTro
        FROM NhanVien
        WHERE TenDangNhap = ? AND MatKhau = ?
    """, (ten_dang_nhap, mat_khau))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None


def get_all_nhanvien():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MaNV, TenNV, SoDienThoai, TenDangNhap, VaiTro FROM NhanVien ORDER BY MaNV ASC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_nhanvien(ten_nv, sdt, ten_dang_nhap, mat_khau, vai_tro):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO NhanVien (TenNV, SoDienThoai, TenDangNhap, MatKhau, VaiTro)
            VALUES (?, ?, ?, ?, ?)
        """, (ten_nv, sdt, ten_dang_nhap, mat_khau, vai_tro))
        conn.commit()
        nv_id = cursor.lastrowid
        return True, nv_id
    except sqlite3.IntegrityError:
        return False, "Tên đăng nhập đã tồn tại!"
    finally:
        conn.close()


def update_nhanvien(ma_nv, ten_nv, sdt, mat_khau, vai_tro):
    conn = get_connection()
    cursor = conn.cursor()
    if mat_khau:
        cursor.execute("""
            UPDATE NhanVien
            SET TenNV = ?, SoDienThoai = ?, MatKhau = ?, VaiTro = ?
            WHERE MaNV = ?
        """, (ten_nv, sdt, mat_khau, vai_tro, ma_nv))
    else:
        cursor.execute("""
            UPDATE NhanVien
            SET TenNV = ?, SoDienThoai = ?, VaiTro = ?
            WHERE MaNV = ?
        """, (ten_nv, sdt, vai_tro, ma_nv))
    conn.commit()
    conn.close()
    return True


def delete_nhanvien(ma_nv):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM NhanVien WHERE MaNV = ?", (ma_nv,))
        conn.commit()
        return True, "Thành công"
    except sqlite3.IntegrityError:
        return False, "Không thể xóa nhân viên này vì đã có dữ liệu hóa đơn liên kết!"
    finally:
        conn.close()


# 2. Nghiệp vụ Quản lý Sách (Kho hàng)
def get_all_sach(keyword=""):
    conn = get_connection()
    cursor = conn.cursor()
    if keyword:
        kw = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM Sach
            WHERE TenSach LIKE ? OR TacGia LIKE ? OR TheLoai LIKE ?
            ORDER BY MaSach DESC
        """, (kw, kw, kw))
    else:
        cursor.execute("SELECT * FROM Sach ORDER BY MaSach DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_sach(ten_sach, tac_gia, the_loai, gia_ban, ton_kho):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO Sach (TenSach, TacGia, TheLoai, GiaBan, TonKho)
        VALUES (?, ?, ?, ?, ?)
    """, (ten_sach, tac_gia, the_loai, gia_ban, ton_kho))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return new_id


def update_sach(ma_sach, ten_sach, tac_gia, the_loai, gia_ban, ton_kho):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE Sach
        SET TenSach = ?, TacGia = ?, TheLoai = ?, GiaBan = ?, TonKho = ?
        WHERE MaSach = ?
    """, (ten_sach, tac_gia, the_loai, gia_ban, ton_kho, ma_sach))
    conn.commit()
    conn.close()
    return True


def delete_sach(ma_sach):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Sach WHERE MaSach = ?", (ma_sach,))
        conn.commit()
        return True, "Đã xóa sách thành công!"
    except sqlite3.IntegrityError:
        return False, "Không thể xóa cuốn sách này vì đã phát sinh giao dịch trong hóa đơn!"
    finally:
        conn.close()


# 3. Nghiệp vụ Khách Hàng
def get_all_khachhang(keyword=""):
    conn = get_connection()
    cursor = conn.cursor()
    if keyword:
        kw = f"%{keyword}%"
        cursor.execute("""
            SELECT * FROM KhachHang
            WHERE TenKH LIKE ? OR SoDienThoai LIKE ?
            ORDER BY MaKH DESC
        """, (kw, kw))
    else:
        cursor.execute("SELECT * FROM KhachHang ORDER BY MaKH DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def add_khachhang(ten_kh, sdt, dia_chi):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO KhachHang (TenKH, SoDienThoai, DiaChi)
        VALUES (?, ?, ?)
    """, (ten_kh, sdt, dia_chi))
    conn.commit()
    kh_id = cursor.lastrowid
    conn.close()
    return kh_id


# 4. Nghiệp vụ Giao dịch (Tạo Hóa Đơn & Trừ tồn kho)
def create_order(ma_kh, ma_nv, items):
    """
    Tạo đơn hàng mới:
    - items: danh sách tuple hoặc dict [{'ma_sach': int, 'so_luong': int, 'gia_mua': float}]
    - Thực hiện giao dịch an toàn (Transaction), trừ tồn kho, tính tổng tiền.
    """
    if not items:
        return False, "Giỏ hàng đang trống!"

    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Kiểm tra tồn kho trước
        for it in items:
            cursor.execute("SELECT TenSach, TonKho FROM Sach WHERE MaSach = ?", (it['ma_sach'],))
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return False, f"Không tìm thấy sách có mã {it['ma_sach']}"
            if row['TonKho'] < it['so_luong']:
                conn.rollback()
                return False, f"Sách '{row['TenSach']}' chỉ còn tồn {row['TonKho']} quyển, không đủ bán!"

        # Tính tổng tiền hóa đơn
        tong_tien = sum(it['so_luong'] * it['gia_mua'] for it in items)
        ngay_lap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Lưu thông tin Hóa Đơn
        cursor.execute("""
            INSERT INTO HoaDon (MaKH, MaNV, NgayLap, TongTien)
            VALUES (?, ?, ?, ?)
        """, (ma_kh, ma_nv, ngay_lap, tong_tien))
        ma_hd = cursor.lastrowid

        # Lưu Chi Tiết Hóa Đơn và trừ Tồn Kho
        for it in items:
            cursor.execute("""
                INSERT INTO ChiTietHoaDon (MaHD, MaSach, SoLuong, GiaMua)
                VALUES (?, ?, ?, ?)
            """, (ma_hd, it['ma_sach'], it['so_luong'], it['gia_mua']))

            cursor.execute("""
                UPDATE Sach
                SET TonKho = TonKho - ?
                WHERE MaSach = ?
            """, (it['so_luong'], it['ma_sach']))

        conn.commit()
        return True, ma_hd
    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        conn.close()


def get_all_hoadon():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.MaHD, h.NgayLap, h.TongTien,
               k.TenKH, k.SoDienThoai AS SDTKhach,
               n.TenNV
        FROM HoaDon h
        LEFT JOIN KhachHang k ON h.MaKH = k.MaKH
        JOIN NhanVien n ON h.MaNV = n.MaNV
        ORDER BY h.MaHD DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_order_detail(ma_hd):
    conn = get_connection()
    cursor = conn.cursor()
    # Thông tin hóa đơn
    cursor.execute("""
        SELECT h.MaHD, h.NgayLap, h.TongTien,
               k.TenKH, k.SoDienThoai AS SDTKhach, k.DiaChi,
               n.TenNV
        FROM HoaDon h
        LEFT JOIN KhachHang k ON h.MaKH = k.MaKH
        JOIN NhanVien n ON h.MaNV = n.MaNV
        WHERE h.MaHD = ?
    """, (ma_hd,))
    order_info = cursor.fetchone()
    if not order_info:
        conn.close()
        return None, []

    # Chi tiết sách đã mua
    cursor.execute("""
        SELECT ct.MaSach, s.TenSach, ct.SoLuong, ct.GiaMua, (ct.SoLuong * ct.GiaMua) AS ThanhTien
        FROM ChiTietHoaDon ct
        JOIN Sach s ON ct.MaSach = s.MaSach
        WHERE ct.MaHD = ?
    """, (ma_hd,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return dict(order_info), items


# 5. Khối nghiệp vụ Báo cáo - Thống kê
def get_revenue_report():
    """Báo cáo Doanh thu tổng hợp theo ngày, tháng, tổng quan."""
    conn = get_connection()
    cursor = conn.cursor()

    # Tổng doanh thu & tổng số hóa đơn
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(TongTien), 0) FROM HoaDon")
    total_orders, total_revenue = cursor.fetchone()

    # Doanh thu theo tháng
    cursor.execute("""
        SELECT strftime('%Y-%m', NgayLap) AS Thang, COUNT(*) AS SoDon, SUM(TongTien) AS DoanhThu
        FROM HoaDon
        GROUP BY Thang
        ORDER BY Thang DESC
    """)
    monthly = [dict(r) for r in cursor.fetchall()]

    # Doanh thu theo ngày (7 ngày gần nhất)
    cursor.execute("""
        SELECT strftime('%Y-%m-%d', NgayLap) AS Ngay, COUNT(*) AS SoDon, SUM(TongTien) AS DoanhThu
        FROM HoaDon
        GROUP BY Ngay
        ORDER BY Ngay DESC
        LIMIT 10
    """)
    daily = [dict(r) for r in cursor.fetchall()]

    conn.close()
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "monthly": monthly,
        "daily": daily
    }


def get_top_selling_books(limit=10):
    """Thống kê sách bán chạy nhất."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.MaSach, s.TenSach, s.TheLoai,
               COALESCE(SUM(ct.SoLuong), 0) AS TongDaBan,
               COALESCE(SUM(ct.SoLuong * ct.GiaMua), 0) AS TongDoanhThu
        FROM Sach s
        JOIN ChiTietHoaDon ct ON s.MaSach = ct.MaSach
        GROUP BY s.MaSach, s.TenSach, s.TheLoai
        ORDER BY TongDaBan DESC
        LIMIT ?
    """, (limit,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_low_stock_books(threshold=5):
    """Kiểm soát Tồn kho: Cảnh báo các đầu sách sắp hết hàng (tồn <= ngưỡng)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT MaSach, TenSach, TacGia, TheLoai, GiaBan, TonKho
        FROM Sach
        WHERE TonKho <= ?
        ORDER BY TonKho ASC
    """, (threshold,))
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_employee_sales_stats():
    """Doanh số theo Nhân viên: Thống kê số hóa đơn và tổng tiền do từng nhân viên bán."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT n.MaNV, n.TenNV, n.TenDangNhap,
               COUNT(h.MaHD) AS TongSoDon,
               COALESCE(SUM(h.TongTien), 0) AS TongDoanhThu
        FROM NhanVien n
        LEFT JOIN HoaDon h ON n.MaNV = h.MaNV
        GROUP BY n.MaNV, n.TenNV, n.TenDangNhap
        ORDER BY TongDoanhThu DESC
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


if __name__ == "__main__":
    init_db()
    print("Khoi tao Co so du lieu thanh cong! (DB Initialized Successfully)")
