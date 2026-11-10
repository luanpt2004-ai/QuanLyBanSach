import luu_tru
from datetime import datetime

TABLE_NAME = "khach_hang"


def lay_danh_sach_khach_hang(tu_khoa=""):
    """Lấy toàn bộ danh sách khách hàng, có lọc theo từ khóa."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    if not tu_khoa:
        return ds

    kw = tu_khoa.strip().lower()
    ket_qua = []
    for kh in ds:
        if (kw in kh.get("ma_khach_hang", "").lower() or
            kw in kh.get("ho_ten", "").lower() or
            kw in kh.get("so_dien_thoai", "").lower() or
            kw in kh.get("dia_chi", "").lower()):
            ket_qua.append(kh)
    return ket_qua


def tim_khach_hang_theo_ma(ma_kh):
    """Tìm khách hàng theo ID số ma_kh."""
    if not ma_kh:
        return None
    ds = luu_tru.doc_csv(TABLE_NAME)
    for kh in ds:
        if str(kh.get("ma_kh")) == str(ma_kh):
            return kh
    return None


def sinh_ma_kh_moi():
    """Tự động sinh ma_kh tự tăng và mã KHxxx."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    max_id = 0
    for kh in ds:
        try:
            val = int(kh.get("ma_kh", 0))
            if val > max_id:
                max_id = val
        except ValueError:
            pass
    next_id = max_id + 1
    return str(next_id), f"KH{next_id:03d}"


def them_khach_hang(ho_ten, so_dien_thoai="", email="", dia_chi="", trang_thai="Hoạt động"):
    """Thêm khách hàng mới vào cơ sở dữ liệu CSV."""
    if not ho_ten.strip():
        return False, "Họ tên khách hàng là trường bắt buộc!"

    ma_kh, ma_khach_hang = sinh_ma_kh_moi()
    ngay_tao = datetime.now().strftime("%Y-%m-%d")

    ds = luu_tru.doc_csv(TABLE_NAME)
    kh_moi = {
        "ma_kh": ma_kh,
        "ma_khach_hang": ma_khach_hang,
        "ho_ten": ho_ten.strip(),
        "so_dien_thoai": so_dien_thoai.strip(),
        "email": email.strip(),
        "dia_chi": dia_chi.strip(),
        "ngay_tao": ngay_tao,
        "trang_thai": trang_thai.strip()
    }
    ds.append(kh_moi)
    luu_tru.ghi_csv(TABLE_NAME, ds)
    return True, kh_moi


def cap_nhat_khach_hang(ma_kh, ho_ten, so_dien_thoai, email, dia_chi, trang_thai):
    """Cập nhật thông tin khách hàng."""
    if not ho_ten.strip():
        return False, "Họ tên khách hàng không được để trống!"

    ds = luu_tru.doc_csv(TABLE_NAME)
    tim_thay = False
    for kh in ds:
        if str(kh.get("ma_kh")) == str(ma_kh):
            kh["ho_ten"] = ho_ten.strip()
            kh["so_dien_thoai"] = so_dien_thoai.strip()
            kh["email"] = email.strip()
            kh["dia_chi"] = dia_chi.strip()
            kh["trang_thai"] = trang_thai.strip()
            tim_thay = True
            break

    if not tim_thay:
        return False, "Không tìm thấy khách hàng cần sửa!"

    luu_tru.ghi_csv(TABLE_NAME, ds)
    return True, "Cập nhật thông tin khách hàng thành công!"


def xoa_khach_hang(ma_kh):
    """Xóa khách hàng nếu chưa từng phát sinh hóa đơn."""
    if str(ma_kh) == "1":
        return False, "Không thể xóa hồ sơ 'Khách lẻ vãng lai' mặc định của hệ thống!"

    # Kiểm tra hóa đơn
    ds_hd = luu_tru.doc_csv("hoa_don")
    da_mua = any(str(hd.get("ma_kh")) == str(ma_kh) for hd in ds_hd)
    if da_mua:
        return False, "Khách hàng này đã có hóa đơn giao dịch, không thể xóa! Vui lòng chuyển trạng thái sang 'Ngừng hoạt động'."

    ds = luu_tru.doc_csv(TABLE_NAME)
    ds_moi = [kh for kh in ds if str(kh.get("ma_kh")) != str(ma_kh)]
    if len(ds_moi) == len(ds):
        return False, "Không tìm thấy khách hàng để xóa!"

    luu_tru.ghi_csv(TABLE_NAME, ds_moi)
    return True, "Đã xóa khách hàng thành công!"
