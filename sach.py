import luu_tru

TABLE_SACH = "sach"
TABLE_THE_LOAI = "the_loai_sach"


# ==========================================
# CÁC HÀM XỬ LÝ THỂ LOẠI SÁCH
# ==========================================
def lay_danh_sach_the_loai():
    """Lấy danh sách các thể loại sách."""
    return luu_tru.doc_csv(TABLE_THE_LOAI)


def sinh_ma_the_loai_moi():
    """Tự động sinh mã thể loại mới định dạng TL01, TL02,..."""
    ds = luu_tru.doc_csv(TABLE_THE_LOAI)
    max_num = 0
    for tl in ds:
        ma = tl.get("ma_the_loai", "").strip().upper()
        if ma.startswith("TL"):
            try:
                num = int(ma[2:])
                if num > max_num:
                    max_num = num
            except ValueError:
                pass
    next_num = max_num + 1
    return f"TL{next_num:02d}"


def them_the_loai(ten_the_loai, mo_ta="", trang_thai="Hoạt động", ma_the_loai=None):
    """Thêm thể loại sách mới, tự động sinh mã nếu không cung cấp."""
    if not ten_the_loai.strip():
        return False, "Tên thể loại là bắt buộc!"

    ds = luu_tru.doc_csv(TABLE_THE_LOAI)
    # Kiểm tra trùng tên thể loại
    for tl in ds:
        if tl.get("ten_the_loai", "").strip().lower() == ten_the_loai.strip().lower():
            return False, f"Thể loại '{ten_the_loai}' đã tồn tại!"

    if not ma_the_loai or not str(ma_the_loai).strip():
        ma_the_loai = sinh_ma_the_loai_moi()
    else:
        ma_the_loai = ma_the_loai.strip()

    tl_moi = {
        "ma_the_loai": ma_the_loai,
        "ten_the_loai": ten_the_loai.strip(),
        "mo_ta": mo_ta.strip(),
        "trang_thai": trang_thai.strip()
    }
    ds.append(tl_moi)
    luu_tru.ghi_csv(TABLE_THE_LOAI, ds)
    return True, tl_moi


def cap_nhat_the_loai(ma_the_loai, ten_the_loai, mo_ta, trang_thai):
    """Cập nhật thông tin thể loại sách."""
    if not ten_the_loai.strip():
        return False, "Tên thể loại không được để trống!"

    ds = luu_tru.doc_csv(TABLE_THE_LOAI)
    tim_thay = False
    for tl in ds:
        if tl.get("ma_the_loai") == ma_the_loai:
            tl["ten_the_loai"] = ten_the_loai.strip()
            tl["mo_ta"] = mo_ta.strip()
            tl["trang_thai"] = trang_thai.strip()
            tim_thay = True
            break
    if not tim_thay:
        return False, "Không tìm thấy thể loại cần cập nhật!"

    luu_tru.ghi_csv(TABLE_THE_LOAI, ds)
    return True, "Cập nhật thể loại thành công!"


def xoa_the_loai(ma_the_loai):
    """Xóa thể loại sách nếu chưa có sách nào thuộc thể loại này."""
    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    da_dung = any(s.get("ma_the_loai") == ma_the_loai for s in ds_sach)
    if da_dung:
        return False, f"Không thể xóa thể loại '{ma_the_loai}' vì đang có sách thuộc thể loại này trong kho!"

    ds = luu_tru.doc_csv(TABLE_THE_LOAI)
    ds_moi = [tl for tl in ds if tl.get("ma_the_loai") != ma_the_loai]
    if len(ds_moi) == len(ds):
        return False, "Không tìm thấy thể loại để xóa!"

    luu_tru.ghi_csv(TABLE_THE_LOAI, ds_moi)
    return True, "Đã xóa thể loại sách thành công!"


# ==========================================
# CÁC HÀM XỬ LÝ SÁCH (KHO SÁCH)
# ==========================================
def lay_danh_sach_sach(tu_khoa="", ma_the_loai_loc=""):
    """Lấy danh sách sách, hỗ trợ tìm kiếm theo tên, tác giả, NXB và lọc theo thể loại."""
    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    ds_tl = {tl["ma_the_loai"]: tl["ten_the_loai"] for tl in lay_danh_sach_the_loai()}

    ket_qua = []
    kw = tu_khoa.strip().lower() if tu_khoa else ""

    for s in ds_sach:
        # Bổ sung tên thể loại vào dict để hiển thị đẹp hơn
        s_full = dict(s)
        s_full["ten_the_loai"] = ds_tl.get(s.get("ma_the_loai"), s.get("ma_the_loai", ""))

        # Lọc thể loại nếu có chọn
        if ma_the_loai_loc and s.get("ma_the_loai") != ma_the_loai_loc:
            continue

        # Lọc từ khóa
        if kw:
            if not (kw in s.get("ten_sach", "").lower() or
                    kw in s.get("tac_gia", "").lower() or
                    kw in s.get("nha_xuat_ban", "").lower() or
                    kw in s.get("ma_sach", "").lower()):
                continue

        ket_qua.append(s_full)
    return ket_qua


def tim_sach_theo_ma(ma_sach):
    """Tìm một cuốn sách theo mã định danh ma_sach."""
    ds = luu_tru.doc_csv(TABLE_SACH)
    for s in ds:
        if str(s.get("ma_sach")) == str(ma_sach):
            return s
    return None


def sinh_ma_sach_moi():
    """Tự động sinh mã sách tự tăng."""
    ds = luu_tru.doc_csv(TABLE_SACH)
    max_id = 0
    for s in ds:
        try:
            val = int(s.get("ma_sach", 0))
            if val > max_id:
                max_id = val
        except ValueError:
            pass
    return str(max_id + 1)


def them_sach(ten_sach, tac_gia, nha_xuat_ban, ma_the_loai, nam_xuat_ban, gia_nhap, gia_ban, so_luong_ton, muc_ton_toi_thieu=5, trang_thai="Đang kinh doanh", mo_ta=""):
    """Thêm một cuốn sách mới vào kho."""
    if not ten_sach.strip():
        return False, "Tên sách là trường bắt buộc!"

    try:
        g_nhap = float(gia_nhap)
        g_ban = float(gia_ban)
        sl_ton = int(so_luong_ton)
        muc_min = int(muc_ton_toi_thieu)
        if g_nhap < 0 or g_ban < 0 or sl_ton < 0 or muc_min < 0:
            return False, "Giá và số lượng tồn kho không được âm!"
    except ValueError:
        return False, "Giá bán, giá nhập, số lượng tồn và mức tồn tối thiểu phải là số hợp lệ!"

    ma_sach = sinh_ma_sach_moi()
    ds = luu_tru.doc_csv(TABLE_SACH)

    sach_moi = {
        "ma_sach": ma_sach,
        "ten_sach": ten_sach.strip(),
        "tac_gia": tac_gia.strip(),
        "nha_xuat_ban": nha_xuat_ban.strip(),
        "ma_the_loai": ma_the_loai.strip(),
        "nam_xuat_ban": str(nam_xuat_ban).strip(),
        "gia_nhap": str(int(g_nhap)),
        "gia_ban": str(int(g_ban)),
        "so_luong_ton": str(sl_ton),
        "muc_ton_toi_thieu": str(muc_min),
        "trang_thai": trang_thai.strip(),
        "mo_ta": mo_ta.strip()
    }
    ds.append(sach_moi)
    luu_tru.ghi_csv(TABLE_SACH, ds)
    return True, sach_moi


def cap_nhat_sach(ma_sach, ten_sach, tac_gia, nha_xuat_ban, ma_the_loai, nam_xuat_ban, gia_nhap, gia_ban, so_luong_ton, muc_ton_toi_thieu, trang_thai, mo_ta):
    """Cập nhật thông tin chi tiết một cuốn sách."""
    if not ten_sach.strip():
        return False, "Tên sách không được để trống!"

    try:
        g_nhap = float(gia_nhap)
        g_ban = float(gia_ban)
        sl_ton = int(so_luong_ton)
        muc_min = int(muc_ton_toi_thieu)
        if g_nhap < 0 or g_ban < 0 or sl_ton < 0 or muc_min < 0:
            return False, "Giá và số lượng tồn kho không được là số âm!"
    except ValueError:
        return False, "Giá bán, giá nhập và số lượng tồn phải là số hợp lệ!"

    ds = luu_tru.doc_csv(TABLE_SACH)
    tim_thay = False
    for s in ds:
        if str(s.get("ma_sach")) == str(ma_sach):
            s["ten_sach"] = ten_sach.strip()
            s["tac_gia"] = tac_gia.strip()
            s["nha_xuat_ban"] = nha_xuat_ban.strip()
            s["ma_the_loai"] = ma_the_loai.strip()
            s["nam_xuat_ban"] = str(nam_xuat_ban).strip()
            s["gia_nhap"] = str(int(g_nhap))
            s["gia_ban"] = str(int(g_ban))
            s["so_luong_ton"] = str(sl_ton)
            s["muc_ton_toi_thieu"] = str(muc_min)
            s["trang_thai"] = trang_thai.strip()
            s["mo_ta"] = mo_ta.strip()
            tim_thay = True
            break

    if not tim_thay:
        return False, "Không tìm thấy cuốn sách cần sửa!"

    luu_tru.ghi_csv(TABLE_SACH, ds)
    return True, "Cập nhật thông tin sách thành công!"


def xoa_sach(ma_sach):
    """Xóa sách nếu chưa từng xuất hiện trong chi tiết hóa đơn."""
    ds_cthd = luu_tru.doc_csv("chi_tiet_hoa_don")
    da_ban = any(str(ct.get("ma_sach")) == str(ma_sach) for ct in ds_cthd)
    if da_ban:
        return False, "Không thể xóa sách này vì đã phát sinh trong các hóa đơn bán hàng! Vui lòng chuyển trạng thái sang 'Ngừng kinh doanh'."

    ds = luu_tru.doc_csv(TABLE_SACH)
    ds_moi = [s for s in ds if str(s.get("ma_sach")) != str(ma_sach)]
    if len(ds_moi) == len(ds):
        return False, "Không tìm thấy cuốn sách để xóa!"

    luu_tru.ghi_csv(TABLE_SACH, ds_moi)
    return True, "Đã xóa sách thành công!"
