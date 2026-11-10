import luu_tru

TABLE_NAME = "nhan_vien"


def lay_danh_sach_nhan_vien(tu_khoa=""):
    """Lấy danh sách tất cả nhân viên, có lọc theo từ khóa nếu có."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    if not tu_khoa:
        return ds

    kw = tu_khoa.strip().lower()
    ket_qua = []
    for nv in ds:
        if (kw in nv.get("ma_nhan_vien", "").lower() or
            kw in nv.get("ho_ten", "").lower() or
            kw in nv.get("so_dien_thoai", "").lower() or
            kw in nv.get("ten_dang_nhap", "").lower()):
            ket_qua.append(nv)
    return ket_qua


def tim_nhan_vien_theo_ma(ma_nv):
    """Tìm nhân viên theo ma_nv (ID số tự tăng)."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    for nv in ds:
        if str(nv.get("ma_nv")) == str(ma_nv):
            return nv
    return None


def xac_thuc_dang_nhap(ten_dang_nhap, mat_khau):
    """Xác thực đăng nhập tài khoản nhân viên."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    for nv in ds:
        if nv.get("ten_dang_nhap") == ten_dang_nhap and nv.get("mat_khau") == mat_khau:
            if nv.get("trang_thai") == "Đã nghỉ việc":
                return None, "Tài khoản nhân viên này đã ngừng hoạt động!"
            return nv, "Đăng nhập thành công"
    return None, "Sai tên đăng nhập hoặc mật khẩu!"


def sinh_ma_nv_moi():
    """Tự động sinh ma_nv (số tự tăng) và mã hiển thị NVxxx."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    max_id = 0
    for nv in ds:
        try:
            val = int(nv.get("ma_nv", 0))
            if val > max_id:
                max_id = val
        except ValueError:
            pass
    next_id = max_id + 1
    return str(next_id), f"NV{next_id:03d}"


def kiem_tra_trung_ma(ma_nhan_vien, ten_dang_nhap, bo_qua_ma_nv=None):
    """Kiểm tra mã nhân viên hoặc tên đăng nhập đã tồn tại chưa."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    for nv in ds:
        if bo_qua_ma_nv and str(nv.get("ma_nv")) == str(bo_qua_ma_nv):
            continue
        if nv.get("ma_nhan_vien", "").strip().lower() == ma_nhan_vien.strip().lower():
            return True, f"Mã nhân viên '{ma_nhan_vien}' đã tồn tại!"
        if nv.get("ten_dang_nhap", "").strip().lower() == ten_dang_nhap.strip().lower():
            return True, f"Tên đăng nhập '{ten_dang_nhap}' đã tồn tại!"
    return False, ""


def them_nhan_vien(ho_ten, ngay_sinh, gioi_tinh, so_dien_thoai, email, dia_chi, ten_dang_nhap, mat_khau, trang_thai="Hoạt động", ma_nhan_vien_tuy_chinh=None):
    """Thêm nhân viên mới vào file CSV."""
    if not ho_ten or not ten_dang_nhap or not mat_khau:
        return False, "Họ tên, tên đăng nhập và mật khẩu là các trường bắt buộc!"

    ma_nv, ma_nhan_vien_auto = sinh_ma_nv_moi()
    ma_nhan_vien = ma_nhan_vien_tuy_chinh.strip() if ma_nhan_vien_tuy_chinh else ma_nhan_vien_auto

    trung, msg = kiem_tra_trung_ma(ma_nhan_vien, ten_dang_nhap)
    if trung:
        return False, msg

    ds = luu_tru.doc_csv(TABLE_NAME)
    nv_moi = {
        "ma_nv": ma_nv,
        "ma_nhan_vien": ma_nhan_vien,
        "ho_ten": ho_ten.strip(),
        "ngay_sinh": ngay_sinh.strip(),
        "gioi_tinh": gioi_tinh.strip(),
        "so_dien_thoai": so_dien_thoai.strip(),
        "email": email.strip(),
        "dia_chi": dia_chi.strip(),
        "ten_dang_nhap": ten_dang_nhap.strip(),
        "mat_khau": mat_khau.strip(),
        "trang_thai": trang_thai.strip()
    }
    ds.append(nv_moi)
    luu_tru.ghi_csv(TABLE_NAME, ds)
    return True, nv_moi


def cap_nhat_nhan_vien(ma_nv, ho_ten, ngay_sinh, gioi_tinh, so_dien_thoai, email, dia_chi, mat_khau, trang_thai):
    """Cập nhật thông tin nhân viên theo ma_nv."""
    ds = luu_tru.doc_csv(TABLE_NAME)
    tim_thay = False
    for nv in ds:
        if str(nv.get("ma_nv")) == str(ma_nv):
            nv["ho_ten"] = ho_ten.strip()
            nv["ngay_sinh"] = ngay_sinh.strip()
            nv["gioi_tinh"] = gioi_tinh.strip()
            nv["so_dien_thoai"] = so_dien_thoai.strip()
            nv["email"] = email.strip()
            nv["dia_chi"] = dia_chi.strip()
            if mat_khau.strip():
                nv["mat_khau"] = mat_khau.strip()
            nv["trang_thai"] = trang_thai.strip()
            tim_thay = True
            break

    if not tim_thay:
        return False, "Không tìm thấy nhân viên cần sửa!"

    luu_tru.ghi_csv(TABLE_NAME, ds)
    return True, "Cập nhật nhân viên thành công!"


def xoa_nhan_vien(ma_nv):
    """Xóa hoặc chuyển trạng thái nghỉ việc nếu nhân viên đã có hóa đơn."""
    # Kiểm tra liên kết trong hóa đơn
    ds_hd = luu_tru.doc_csv("hoa_don")
    da_lap_hd = any(str(hd.get("ma_nv")) == str(ma_nv) for hd in ds_hd)
    if da_lap_hd:
        return False, "Không thể xóa nhân viên này vì đã có dữ liệu hóa đơn liên quan! Bạn có thể chuyển trạng thái sang 'Đã nghỉ việc'."

    ds = luu_tru.doc_csv(TABLE_NAME)
    ds_moi = [nv for nv in ds if str(nv.get("ma_nv")) != str(ma_nv)]
    if len(ds_moi) == len(ds):
        return False, "Không tìm thấy nhân viên để xóa!"

    luu_tru.ghi_csv(TABLE_NAME, ds_moi)
    return True, "Đã xóa nhân viên thành công!"
