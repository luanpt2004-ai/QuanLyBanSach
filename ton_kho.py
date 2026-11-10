import luu_tru
from datetime import datetime

TABLE_LS = "lich_su_ton_kho"
TABLE_SACH = "sach"


def sinh_ma_ls_moi():
    """Tự sinh mã lịch sử tồn kho tự tăng."""
    ds = luu_tru.doc_csv(TABLE_LS)
    max_id = 0
    for row in ds:
        try:
            val = int(row.get("ma_ls", 0))
            if val > max_id:
                max_id = val
        except ValueError:
            pass
    return str(max_id + 1)


def lay_lich_su_ton_kho(ma_sach=None):
    """
    Lấy danh sách biến động tồn kho, kết hợp thông tin tựa sách và nhân viên.
    Có thể lọc theo mã cuốn sách cụ thể.
    """
    ds_ls = luu_tru.doc_csv(TABLE_LS)
    ds_sach = {s["ma_sach"]: s["ten_sach"] for s in luu_tru.doc_csv(TABLE_SACH)}
    ds_nv = {nv["ma_nv"]: nv["ho_ten"] for nv in luu_tru.doc_csv("nhan_vien")}

    ket_qua = []
    # Sắp xếp bản ghi mới nhất lên đầu
    for row in reversed(ds_ls):
        if ma_sach and str(row.get("ma_sach")) != str(ma_sach):
            continue
        row_full = dict(row)
        row_full["ten_sach"] = ds_sach.get(row.get("ma_sach"), f"Sách #{row.get('ma_sach')}")
        row_full["ten_nhan_vien"] = ds_nv.get(row.get("ma_nv"), f"NV #{row.get('ma_nv')}")
        ket_qua.append(row_full)
    return ket_qua


def ghi_lich_su_bien_dong(ma_sach, ma_nv, loai_giao_dich, so_luong_thay_doi, ton_truoc, ton_sau, ma_tham_chieu="", ghi_chu=""):
    """Ghi nhận một dòng nhật ký lịch sử tồn kho."""
    ds = luu_tru.doc_csv(TABLE_LS)
    ma_ls = sinh_ma_ls_moi()
    thoi_gian = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    ban_ghi = {
        "ma_ls": ma_ls,
        "ma_sach": str(ma_sach),
        "ma_nv": str(ma_nv),
        "thoi_gian": thoi_gian,
        "loai_giao_dich": str(loai_giao_dich),
        "so_luong_thay_doi": str(so_luong_thay_doi),
        "ton_truoc": str(ton_truoc),
        "ton_sau": str(ton_sau),
        "ma_tham_chieu": str(ma_tham_chieu),
        "ghi_chu": str(ghi_chu)
    }
    ds.append(ban_ghi)
    luu_tru.ghi_csv(TABLE_LS, ds)
    return ban_ghi


def kiem_tra_du_ton_kho(ma_sach, so_luong_can_mua):
    """
    Kiểm tra xem số lượng sách trong kho có đủ để bán hay không.
    Trả về (True/False, số lượng tồn hiện tại, tên sách).
    """
    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    for s in ds_sach:
        if str(s.get("ma_sach")) == str(ma_sach):
            ton_hien_tai = int(s.get("so_luong_ton", 0))
            if ton_hien_tai >= int(so_luong_can_mua):
                return True, ton_hien_tai, s.get("ten_sach", "")
            else:
                return False, ton_hien_tai, s.get("ten_sach", "")
    return False, 0, "Không tìm thấy sách"


def cap_nhat_tru_ton_kho(ma_sach, so_luong_ban, ma_nv, ma_hoa_don):
    """
    Trừ tồn kho khi hoàn thành hóa đơn và ghi lịch sử.
    """
    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    for s in ds_sach:
        if str(s.get("ma_sach")) == str(ma_sach):
            ton_truoc = int(s.get("so_luong_ton", 0))
            so_luong_ban = int(so_luong_ban)
            if ton_truoc < so_luong_ban:
                return False, f"Không đủ số lượng trong kho cho sách {s.get('ten_sach')}!"

            ton_sau = ton_truoc - so_luong_ban
            s["so_luong_ton"] = str(ton_sau)
            luu_tru.ghi_csv(TABLE_SACH, ds_sach)

            # Ghi lịch sử
            ghi_lich_su_bien_dong(
                ma_sach=ma_sach,
                ma_nv=ma_nv,
                loai_giao_dich="Bán hàng",
                so_luong_thay_doi=f"-{so_luong_ban}",
                ton_truoc=ton_truoc,
                ton_sau=ton_sau,
                ma_tham_chieu=ma_hoa_don,
                ghi_chu="Trừ tồn kho khi xuất bán thành công"
            )
            return True, ton_sau
    return False, "Không tìm thấy sách!"


def cap_nhat_hoan_ton_kho(ma_sach, so_luong_hoan, ma_nv, ma_hoa_don, ly_do="Hủy hóa đơn"):
    """
    Cộng hoàn lại tồn kho khi hủy hóa đơn và ghi lịch sử (không xóa lịch sử cũ).
    """
    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    for s in ds_sach:
        if str(s.get("ma_sach")) == str(ma_sach):
            ton_truoc = int(s.get("so_luong_ton", 0))
            so_luong_hoan = int(so_luong_hoan)
            ton_sau = ton_truoc + so_luong_hoan
            s["so_luong_ton"] = str(ton_sau)
            luu_tru.ghi_csv(TABLE_SACH, ds_sach)

            # Ghi lịch sử hoàn kho
            ghi_lich_su_bien_dong(
                ma_sach=ma_sach,
                ma_nv=ma_nv,
                loai_giao_dich="Hoàn kho",
                so_luong_thay_doi=f"+{so_luong_hoan}",
                ton_truoc=ton_truoc,
                ton_sau=ton_sau,
                ma_tham_chieu=ma_hoa_don,
                ghi_chu=f"Hoàn kho do: {ly_do}"
            )
            return True, ton_sau
    return False, "Không tìm thấy sách!"


def nhap_them_hang(ma_sach, so_luong_nhap, ma_nv, ghi_chu="Nhập thêm hàng vào kho"):
    """Nhập bổ sung sách vào kho và ghi lịch sử."""
    if int(so_luong_nhap) <= 0:
        return False, "Số lượng nhập thêm phải lớn hơn 0!"

    ds_sach = luu_tru.doc_csv(TABLE_SACH)
    for s in ds_sach:
        if str(s.get("ma_sach")) == str(ma_sach):
            ton_truoc = int(s.get("so_luong_ton", 0))
            ton_sau = ton_truoc + int(so_luong_nhap)
            s["so_luong_ton"] = str(ton_sau)
            luu_tru.ghi_csv(TABLE_SACH, ds_sach)

            ghi_lich_su_bien_dong(
                ma_sach=ma_sach,
                ma_nv=ma_nv,
                loai_giao_dich="Nhập kho",
                so_luong_thay_doi=f"+{so_luong_nhap}",
                ton_truoc=ton_truoc,
                ton_sau=ton_sau,
                ma_tham_chieu="",
                ghi_chu=ghi_chu
            )
            return True, ton_sau
    return False, "Không tìm thấy sách để nhập thêm!"
