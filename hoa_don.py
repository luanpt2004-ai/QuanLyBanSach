import luu_tru
import ton_kho
import sach
import khach_hang
import nhan_vien
from datetime import datetime

TABLE_HD = "hoa_don"
TABLE_CTHD = "chi_tiet_hoa_don"


def tinh_tong_tien_gio_hang(danh_sach_muc, giam_gia_tong=0):
    """
    Tính toán tiền đơn hàng:
    - danh_sach_muc: list các dict: [{'so_luong': int, 'don_gia_ban': float, 'giam_gia': float}]
    - giam_gia_tong: số tiền giảm giá trực tiếp trên tổng đơn (VNĐ)
    Trả về dict: {
        'tam_tinh': float,
        'giam_gia_mon': float,
        'giam_gia_tong': float,
        'tong_giam_gia': float,
        'tong_thanh_toan': float
    }
    """
    tam_tinh = 0
    giam_gia_mon = 0

    for item in danh_sach_muc:
        sl = int(item.get("so_luong", 0))
        don_gia = float(item.get("don_gia_ban", 0))
        gg_mon = float(item.get("giam_gia", 0))

        tam_tinh += sl * don_gia
        giam_gia_mon += gg_mon

    giam_gia_tong = float(giam_gia_tong)
    tong_giam_gia = giam_gia_mon + giam_gia_tong
    tong_thanh_toan = max(0, tam_tinh - tong_giam_gia)

    return {
        "tam_tinh": tam_tinh,
        "giam_gia_mon": giam_gia_mon,
        "giam_gia_tong": giam_gia_tong,
        "tong_giam_gia": tong_giam_gia,
        "tong_thanh_toan": tong_thanh_toan
    }


def sinh_ma_hd_moi():
    """Tự động sinh mã hóa đơn tự tăng và mã chuỗi HDxxxxx."""
    ds = luu_tru.doc_csv(TABLE_HD)
    max_id = 0
    for row in ds:
        try:
            val = int(row.get("ma_hd", 0))
            if val > max_id:
                max_id = val
        except ValueError:
            pass
    next_id = max_id + 1
    return str(next_id), f"HD{next_id:05d}"


def lay_danh_sach_hoa_don(tu_khoa="", trang_thai_loc=""):
    """
    Lấy danh sách tất cả hóa đơn, bổ sung tên khách hàng và tên nhân viên.
    Có hỗ trợ lọc theo trạng thái (Hoàn thành, Nháp, Đã hủy) hoặc tìm kiếm.
    """
    ds_hd = luu_tru.doc_csv(TABLE_HD)
    ds_cthd = luu_tru.doc_csv(TABLE_CTHD)
    ds_kh = {kh["ma_kh"]: kh["ho_ten"] for kh in khach_hang.lay_danh_sach_khach_hang()}
    ds_nv = {nv["ma_nv"]: nv["ho_ten"] for nv in nhan_vien.lay_danh_sach_nhan_vien()}

    # Tính tổng tiền của từng hóa đơn từ chi_tiet_hoa_don và giam_gia của hoa_don
    tien_theo_hd = {}
    for ct in ds_cthd:
        mhd = str(ct.get("ma_hd"))
        thanh_tien_mon = (int(ct.get("so_luong", 0)) * float(ct.get("don_gia_ban", 0))) - float(ct.get("giam_gia", 0))
        tien_theo_hd[mhd] = tien_theo_hd.get(mhd, 0) + max(0, thanh_tien_mon)

    ket_qua = []
    kw = tu_khoa.strip().lower() if tu_khoa else ""

    for hd in reversed(ds_hd): # Mới nhất xếp trước
        mhd = str(hd.get("ma_hd"))
        tt = hd.get("trang_thai", "Hoàn thành")

        if trang_thai_loc and tt != trang_thai_loc:
            continue

        raw_sum = tien_theo_hd.get(mhd, 0)
        gg_tong = float(hd.get("giam_gia", 0))
        tong_tien = max(0, raw_sum - gg_tong)

        hd_full = dict(hd)
        hd_full["ten_kh"] = ds_kh.get(str(hd.get("ma_kh")), "Khách lẻ vãng lai")
        hd_full["ten_nv"] = ds_nv.get(str(hd.get("ma_nv")), "Nhân viên")
        hd_full["tong_tien"] = tong_tien

        if kw:
            if not (kw in hd.get("ma_hoa_don", "").lower() or
                    kw in hd_full["ten_kh"].lower() or
                    kw in hd_full["ten_nv"].lower()):
                continue

        ket_qua.append(hd_full)
    return ket_qua


def lay_chi_tiet_hoa_don(ma_hd):
    """Lấy thông tin đầy đủ của một hóa đơn kèm danh sách sách đã mua."""
    ds_hd = luu_tru.doc_csv(TABLE_HD)
    ds_cthd = luu_tru.doc_csv(TABLE_CTHD)

    hd_tim_thay = None
    for h in ds_hd:
        if str(h.get("ma_hd")) == str(ma_hd):
            hd_tim_thay = dict(h)
            break

    if not hd_tim_thay:
        return None, []

    # Thông tin bổ sung
    kh = khach_hang.tim_khach_hang_theo_ma(hd_tim_thay.get("ma_kh"))
    nv = nhan_vien.tim_nhan_vien_theo_ma(hd_tim_thay.get("ma_nv"))
    hd_tim_thay["khach_hang_info"] = kh if kh else {"ho_ten": "Khách lẻ vãng lai", "so_dien_thoai": "", "dia_chi": ""}
    hd_tim_thay["nhan_vien_info"] = nv if nv else {"ho_ten": "Nhân viên trực"}

    # Các món hàng
    items = []
    tam_tinh = 0
    giam_gia_cac_mon = 0

    for ct in ds_cthd:
        if str(ct.get("ma_hd")) == str(ma_hd):
            s = sach.tim_sach_theo_ma(ct.get("ma_sach"))
            sl = int(ct.get("so_luong", 0))
            don_gia = float(ct.get("don_gia_ban", 0))
            gg = float(ct.get("giam_gia", 0))
            thanh_tien = max(0, (sl * don_gia) - gg)

            tam_tinh += sl * don_gia
            giam_gia_cac_mon += gg

            items.append({
                "ma_sach": ct.get("ma_sach"),
                "ten_sach": s.get("ten_sach") if s else f"Sách #{ct.get('ma_sach')}",
                "so_luong": sl,
                "don_gia_ban": don_gia,
                "giam_gia": gg,
                "thanh_tien": thanh_tien
            })

    gg_tong = float(hd_tim_thay.get("giam_gia", 0))
    hd_tim_thay["tam_tinh"] = tam_tinh
    hd_tim_thay["tong_giam_gia"] = giam_gia_cac_mon + gg_tong
    hd_tim_thay["tong_tien"] = max(0, tam_tinh - hd_tim_thay["tong_giam_gia"])

    return hd_tim_thay, items


def lap_hoa_don(ma_kh, ma_nv, danh_sach_muc, giam_gia=0, trang_thai="Hoàn thành", ghi_chu=""):
    """
    Quy trình lập hóa đơn bán sách:
    - danh_sach_muc: [{'ma_sach': '1', 'so_luong': 2, 'don_gia_ban': 125000, 'giam_gia': 0}]
    - trang_thai: 'Hoàn thành' hoặc 'Nháp'
    - Kiểm tra số lượng tồn kho trước khi hoàn thành, không bán vượt tồn
    - Cập nhật trừ tồn kho và ghi lịch sử (chỉ khi trạng thái là 'Hoàn thành')
    """
    if not danh_sach_muc:
        return False, "Hóa đơn phải có ít nhất 1 cuốn sách!"

    # 1. Kiểm tra tồn kho của tất cả các mặt hàng nếu xuất bán 'Hoàn thành'
    if trang_thai == "Hoàn thành":
        for item in danh_sach_muc:
            ms = item.get("ma_sach")
            sl = int(item.get("so_luong", 0))
            if sl <= 0:
                return False, f"Số lượng mua của cuốn sách #{ms} phải lớn hơn 0!"

            du_ton, ton_hien_tai, ten_s = ton_kho.kiem_tra_du_ton_kho(ms, sl)
            if not du_ton:
                return False, f"Sách '{ten_s}' chỉ còn tồn {ton_hien_tai} cuốn, không đủ để bán {sl} cuốn!"

    # 2. Sinh mã hóa đơn mới
    ma_hd, ma_hoa_don = sinh_ma_hd_moi()
    ngay_lap = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. Lưu vào hoa_don.csv
    ds_hd = luu_tru.doc_csv(TABLE_HD)
    hd_moi = {
        "ma_hd": ma_hd,
        "ma_hoa_don": ma_hoa_don,
        "ma_kh": str(ma_kh) if ma_kh else "1",
        "ma_nv": str(ma_nv),
        "ngay_lap": ngay_lap,
        "giam_gia": str(float(giam_gia)),
        "trang_thai": str(trang_thai),
        "ghi_chu": str(ghi_chu)
    }
    ds_hd.append(hd_moi)
    luu_tru.ghi_csv(TABLE_HD, ds_hd)

    # 4. Lưu vào chi_tiet_hoa_don.csv
    ds_cthd = luu_tru.doc_csv(TABLE_CTHD)
    for item in danh_sach_muc:
        ct_row = {
            "ma_hd": ma_hd,
            "ma_sach": str(item.get("ma_sach")),
            "so_luong": str(int(item.get("so_luong", 1))),
            "don_gia_ban": str(float(item.get("don_gia_ban", 0))),
            "giam_gia": str(float(item.get("giam_gia", 0)))
        }
        ds_cthd.append(ct_row)
    luu_tru.ghi_csv(TABLE_CTHD, ds_cthd)

    # 5. Cập nhật trừ tồn kho và ghi lịch sử nếu là đơn Hoàn thành
    if trang_thai == "Hoàn thành":
        for item in danh_sach_muc:
            ton_kho.cap_nhat_tru_ton_kho(
                ma_sach=item.get("ma_sach"),
                so_luong_ban=int(item.get("so_luong")),
                ma_nv=ma_nv,
                ma_hoa_don=ma_hoa_don
            )

    return True, hd_moi


def huy_hoa_don(ma_hd, ma_nv_thuc_hien, ly_do="Khách yêu cầu hủy đơn"):
    """
    Hủy hóa đơn:
    - Nếu hóa đơn đang ở trạng thái 'Hoàn thành', phải hoàn lại số lượng sách vào kho có kiểm soát và ghi lịch sử.
    - Không xóa lịch sử cũ, chỉ cập nhật trạng thái hóa đơn sang 'Đã hủy'.
    """
    ds_hd = luu_tru.doc_csv(TABLE_HD)
    hd_tim = None
    for h in ds_hd:
        if str(h.get("ma_hd")) == str(ma_hd):
            hd_tim = h
            break

    if not hd_tim:
        return False, "Không tìm thấy hóa đơn cần hủy!"

    trang_thai_cu = hd_tim.get("trang_thai")
    if trang_thai_cu == "Đã hủy":
        return False, "Hóa đơn này đã được hủy trước đó rồi!"

    # Nếu hóa đơn đã hoàn thành, thực hiện hoàn lại tồn kho
    if trang_thai_cu == "Hoàn thành":
        ds_cthd = luu_tru.doc_csv(TABLE_CTHD)
        for ct in ds_cthd:
            if str(ct.get("ma_hd")) == str(ma_hd):
                ton_kho.cap_nhat_hoan_ton_kho(
                    ma_sach=ct.get("ma_sach"),
                    so_luong_hoan=int(ct.get("so_luong")),
                    ma_nv=ma_nv_thuc_hien,
                    ma_hoa_don=hd_tim.get("ma_hoa_don"),
                    ly_do=ly_do
                )

    # Cập nhật trạng thái sang Đã hủy
    hd_tim["trang_thai"] = "Đã hủy"
    hd_tim["ghi_chu"] = f"{hd_tim.get('ghi_chu', '')} [Đã hủy: {ly_do}]".strip()
    luu_tru.ghi_csv(TABLE_HD, ds_hd)
    return True, "Đã hủy hóa đơn và hoàn kho thành công!"
