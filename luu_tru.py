import os
import csv

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# Định nghĩa danh sách các trường (headers) chuẩn theo tài liệu
HEADERS = {
    "nhan_vien": [
        "ma_nv", "ma_nhan_vien", "ho_ten", "ngay_sinh", "gioi_tinh",
        "so_dien_thoai", "email", "dia_chi", "ten_dang_nhap", "mat_khau", "trang_thai"
    ],
    "khach_hang": [
        "ma_kh", "ma_khach_hang", "ho_ten", "so_dien_thoai", "email",
        "dia_chi", "ngay_tao", "trang_thai"
    ],
    "the_loai_sach": [
        "ma_the_loai", "ten_the_loai", "mo_ta", "trang_thai"
    ],
    "sach": [
        "ma_sach", "ten_sach", "tac_gia", "nha_xuat_ban", "ma_the_loai",
        "nam_xuat_ban", "gia_nhap", "gia_ban", "so_luong_ton", "muc_ton_toi_thieu",
        "trang_thai", "mo_ta"
    ],
    "hoa_don": [
        "ma_hd", "ma_hoa_don", "ma_kh", "ma_nv", "ngay_lap", "giam_gia",
        "trang_thai", "ghi_chu"
    ],
    "chi_tiet_hoa_don": [
        "ma_hd", "ma_sach", "so_luong", "don_gia_ban", "giam_gia"
    ],
    "lich_su_ton_kho": [
        "ma_ls", "ma_sach", "ma_nv", "thoi_gian", "loai_giao_dich",
        "so_luong_thay_doi", "ton_truoc", "ton_sau", "ma_tham_chieu", "ghi_chu"
    ]
}


def get_file_path(table_name):
    """Lấy đường dẫn đầy đủ của file CSV tương ứng."""
    return os.path.join(DATA_DIR, f"{table_name}.csv")


def doc_csv(table_name):
    """
    Đọc dữ liệu từ file CSV sử dụng csv.DictReader.
    Nếu file chưa tồn tại, tự động tạo file rỗng với hàng tiêu đề (header).
    Trả về danh sách các Dictionary.
    """
    file_path = get_file_path(table_name)
    headers = HEADERS.get(table_name)

    if not os.path.exists(file_path):
        ghi_csv(table_name, [])
        return []

    data = []
    with open(file_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(dict(row))
    return data


def ghi_csv(table_name, data):
    """
    Ghi danh sách Dictionary vào file CSV sử dụng csv.DictWriter.
    Bảo đảm UTF-8 và thứ tự cột đúng theo quy định.
    """
    file_path = get_file_path(table_name)
    headers = HEADERS.get(table_name)
    if not headers:
        raise ValueError(f"Không tìm thấy cấu hình tiêu đề cho bảng: {table_name}")

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, mode="w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            # Chỉ ghi các trường nằm trong headers, bổ sung giá trị rỗng nếu thiếu
            clean_row = {col: row.get(col, "") for col in headers}
            writer.writerow(clean_row)
    return True


def khoi_tao_du_lieu_mau():
    """Khởi tạo các file CSV và nạp dữ liệu mẫu ban đầu nếu file còn trống."""
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Nhân viên mẫu
    ds_nv = doc_csv("nhan_vien")
    if not ds_nv:
        ds_nv = [
            {
                "ma_nv": "1",
                "ma_nhan_vien": "NV001",
                "ho_ten": "Nguyễn Văn Quản Lý",
                "ngay_sinh": "1995-05-15",
                "gioi_tinh": "Nam",
                "so_dien_thoai": "0901234567",
                "email": "quanly@bookstore.vn",
                "dia_chi": "Ninh Kiều, Cần Thơ",
                "ten_dang_nhap": "admin",
                "mat_khau": "admin123",
                "trang_thai": "Hoạt động"
            },
            {
                "ma_nv": "2",
                "ma_nhan_vien": "NV002",
                "ho_ten": "Trần Thị Thu Ngân",
                "ngay_sinh": "2000-08-20",
                "gioi_tinh": "Nữ",
                "so_dien_thoai": "0912345678",
                "email": "thungan@bookstore.vn",
                "dia_chi": "Bình Thủy, Cần Thơ",
                "ten_dang_nhap": "nhanvien",
                "mat_khau": "123456",
                "trang_thai": "Hoạt động"
            }
        ]
        ghi_csv("nhan_vien", ds_nv)

    # 2. Thể loại sách mẫu
    ds_tl = doc_csv("the_loai_sach")
    if not ds_tl:
        ds_tl = [
            {"ma_the_loai": "TL01", "ten_the_loai": "Công nghệ thông tin", "mo_ta": "Sách lập trình, thuật toán, mạng", "trang_thai": "Hoạt động"},
            {"ma_the_loai": "TL02", "ten_the_loai": "Văn học", "mo_ta": "Tiểu thuyết, truyện ngắn trong và ngoài nước", "trang_thai": "Hoạt động"},
            {"ma_the_loai": "TL03", "ten_the_loai": "Kinh tế & Quản trị", "mo_ta": "Sách đầu tư, kinh doanh, khởi nghiệp", "trang_thai": "Hoạt động"},
            {"ma_the_loai": "TL04", "ten_the_loai": "Kỹ năng sống", "mo_ta": "Phát triển bản thân, tư duy lãnh đạo", "trang_thai": "Hoạt động"},
            {"ma_the_loai": "TL05", "ten_the_loai": "Khoa học - Khám phá", "mo_ta": "Thiên văn, vật lý, lịch sử", "trang_thai": "Hoạt động"}
        ]
        ghi_csv("the_loai_sach", ds_tl)

    # 3. Khách hàng mẫu
    ds_kh = doc_csv("khach_hang")
    if not ds_kh:
        ds_kh = [
            {
                "ma_kh": "1",
                "ma_khach_hang": "KH001",
                "ho_ten": "Khách lẻ vãng lai",
                "so_dien_thoai": "",
                "email": "",
                "dia_chi": "",
                "ngay_tao": "2026-01-01",
                "trang_thai": "Hoạt động"
            },
            {
                "ma_kh": "2",
                "ma_khach_hang": "KH002",
                "ho_ten": "Lê Hoàng Nam",
                "so_dien_thoai": "0987654321",
                "email": "hoangnam@gmail.com",
                "dia_chi": "30/4 Ninh Kiều, Cần Thơ",
                "ngay_tao": "2026-01-10",
                "trang_thai": "Hoạt động"
            },
            {
                "ma_kh": "3",
                "ma_khach_hang": "KH003",
                "ho_ten": "Phạm Minh Thư",
                "so_dien_thoai": "0977889900",
                "email": "minhthu@gmail.com",
                "dia_chi": "Cách Mạng Tháng Tám, Cần Thơ",
                "ngay_tao": "2026-02-15",
                "trang_thai": "Hoạt động"
            }
        ]
        ghi_csv("khach_hang", ds_kh)

    # 4. Sách mẫu
    ds_s = doc_csv("sach")
    if not ds_s:
        ds_s = [
            {
                "ma_sach": "1",
                "ten_sach": "Lập trình Python từ cơ bản đến nâng cao",
                "tac_gia": "Nguyễn Văn A",
                "nha_xuat_ban": "NXB Thông tin và Truyền thông",
                "ma_the_loai": "TL01",
                "nam_xuat_ban": "2024",
                "gia_nhap": "90000",
                "gia_ban": "125000",
                "so_luong_ton": "50",
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Giáo trình học Python thực hành dễ hiểu"
            },
            {
                "ma_sach": "2",
                "ten_sach": "Cấu trúc dữ liệu và giải thuật trong Python",
                "tac_gia": "Trần Đình C",
                "nha_xuat_ban": "NXB Đại học Quốc gia",
                "ma_the_loai": "TL01",
                "nam_xuat_ban": "2023",
                "gia_nhap": "110000",
                "gia_ban": "150000",
                "so_luong_ton": "30",
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Hướng dẫn chi tiết các giải thuật và cấu trúc dữ liệu"
            },
            {
                "ma_sach": "3",
                "ten_sach": "Đắc Nhân Tâm",
                "tac_gia": "Dale Carnegie",
                "nha_xuat_ban": "NXB Tổng Hợp TP.HCM",
                "ma_the_loai": "TL04",
                "nam_xuat_ban": "2022",
                "gia_nhap": "55000",
                "gia_ban": "85000",
                "so_luong_ton": "80",
                "muc_ton_toi_thieu": "10",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Nghệ thuật thu phục lòng người"
            },
            {
                "ma_sach": "4",
                "ten_sach": "Nhà Giả Kim",
                "tac_gia": "Paulo Coelho",
                "nha_xuat_ban": "NXB Hội Nhà Văn",
                "ma_the_loai": "TL02",
                "nam_xuat_ban": "2021",
                "gia_nhap": "50000",
                "gia_ban": "79000",
                "so_luong_ton": "40",
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Tiểu thuyết truyền cảm hứng theo đuổi ước mơ"
            },
            {
                "ma_sach": "5",
                "ten_sach": "Kinh Tế Học Hài Hước",
                "tac_gia": "Steven Levitt",
                "nha_xuat_ban": "NXB Trẻ",
                "ma_the_loai": "TL03",
                "nam_xuat_ban": "2023",
                "gia_nhap": "75000",
                "gia_ban": "110000",
                "so_luong_ton": "25",
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Góc nhìn hài hước nhưng sâu sắc về kinh tế"
            },
            {
                "ma_sach": "6",
                "ten_sach": "Mắt Biếc",
                "tac_gia": "Nguyễn Nhật Ánh",
                "nha_xuat_ban": "NXB Trẻ",
                "ma_the_loai": "TL02",
                "nam_xuat_ban": "2020",
                "gia_nhap": "65000",
                "gia_ban": "95000",
                "so_luong_ton": "4",  # Số lượng <= 5 để test cảnh báo tồn kho
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Truyện dài cảm động về tình yêu học trò"
            },
            {
                "ma_sach": "7",
                "ten_sach": "Lược Sử Thời Gian",
                "tac_gia": "Stephen Hawking",
                "nha_xuat_ban": "NXB Trẻ",
                "ma_the_loai": "TL05",
                "nam_xuat_ban": "2022",
                "gia_nhap": "95000",
                "gia_ban": "135000",
                "so_luong_ton": "2",  # Tồn kho thấp
                "muc_ton_toi_thieu": "5",
                "trang_thai": "Đang kinh doanh",
                "mo_ta": "Khám phá bí ẩn vũ trụ và thời gian"
            }
        ]
        ghi_csv("sach", ds_s)

    # Khởi tạo các file giao dịch còn lại với header rỗng
    for tbl in ["hoa_don", "chi_tiet_hoa_don", "lich_su_ton_kho"]:
        doc_csv(tbl)


if __name__ == "__main__":
    khoi_tao_du_lieu_mau()
    print("Khoi tao cac file CSV thanh cong!")
