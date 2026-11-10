import os
import luu_tru
import hoa_don
import ton_kho
import sach
import nhan_vien
from datetime import datetime

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ==========================================
# CÁC HÀM TRUY VẤN DỮ LIỆU TỔNG HỢP BÁO CÁO
# ==========================================
def thong_ke_doanh_thu(tu_ngay=None, den_ngay=None):
    """
    Thống kê doanh thu bán sách:
    - Chỉ tính các hóa đơn ở trạng thái 'Hoàn thành'.
    - Lọc theo khoảng ngày (YYYY-MM-DD) nếu được cung cấp.
    """
    ds_hd = luu_tru.doc_csv("hoa_don")
    ds_cthd = luu_tru.doc_csv("chi_tiet_hoa_don")

    # Bản đồ tính tổng tiền mỗi hóa đơn
    tien_hd = {}
    for ct in ds_cthd:
        mhd = str(ct.get("ma_hd"))
        sl = int(ct.get("so_luong", 0))
        dg = float(ct.get("don_gia_ban", 0))
        gg = float(ct.get("giam_gia", 0))
        tien_hd[mhd] = tien_hd.get(mhd, 0) + max(0, (sl * dg) - gg)

    tong_doanh_thu = 0
    tong_so_don = 0
    theo_ngay = {}
    theo_thang = {}

    for hd in ds_hd:
        if hd.get("trang_thai") != "Hoàn thành":
            continue

        ngay_gio = hd.get("ngay_lap", "")
        ngay = ngay_gio.split(" ")[0] if " " in ngay_gio else ngay_gio
        thang = ngay[:7] if len(ngay) >= 7 else ngay

        # Kiểm tra khoảng ngày
        if tu_ngay and ngay < tu_ngay:
            continue
        if den_ngay and ngay > den_ngay:
            continue

        mhd = str(hd.get("ma_hd"))
        gg_tong = float(hd.get("giam_gia", 0))
        tien_don = max(0, tien_hd.get(mhd, 0) - gg_tong)

        tong_so_don += 1
        tong_doanh_thu += tien_don

        # Thống kê ngày
        if ngay not in theo_ngay:
            theo_ngay[ngay] = {"so_don": 0, "doanh_thu": 0}
        theo_ngay[ngay]["so_don"] += 1
        theo_ngay[ngay]["doanh_thu"] += tien_don

        # Thống kê tháng
        if thang not in theo_thang:
            theo_thang[thang] = {"so_don": 0, "doanh_thu": 0}
        theo_thang[thang]["so_don"] += 1
        theo_thang[thang]["doanh_thu"] += tien_don

    ds_ngay = [{"ngay": k, "so_don": v["so_don"], "doanh_thu": v["doanh_thu"]} for k, v in sorted(theo_ngay.items(), reverse=True)]
    ds_thang = [{"thang": k, "so_don": v["so_don"], "doanh_thu": v["doanh_thu"]} for k, v in sorted(theo_thang.items(), reverse=True)]

    return {
        "tong_so_don": tong_so_don,
        "tong_doanh_thu": tong_doanh_thu,
        "theo_ngay": ds_ngay,
        "theo_thang": ds_thang
    }


def thong_ke_sach_ban_chay(limit=10):
    """Xếp hạng các cuốn sách có số lượng bán nhiều nhất từ các hóa đơn 'Hoàn thành'."""
    ds_hd = {str(hd.get("ma_hd")): hd.get("trang_thai") for hd in luu_tru.doc_csv("hoa_don")}
    ds_cthd = luu_tru.doc_csv("chi_tiet_hoa_don")
    ds_sach = {str(s.get("ma_sach")): s for s in sach.lay_danh_sach_sach()}

    ban_sach = {}
    for ct in ds_cthd:
        mhd = str(ct.get("ma_hd"))
        if ds_hd.get(mhd) != "Hoàn thành":
            continue

        ms = str(ct.get("ma_sach"))
        sl = int(ct.get("so_luong", 0))
        dg = float(ct.get("don_gia_ban", 0))
        gg = float(ct.get("giam_gia", 0))
        tt = max(0, (sl * dg) - gg)

        if ms not in ban_sach:
            ban_sach[ms] = {"so_luong": 0, "thanh_tien": 0}
        ban_sach[ms]["so_luong"] += sl
        ban_sach[ms]["thanh_tien"] += tt

    ket_qua = []
    for ms, val in ban_sach.items():
        s_info = ds_sach.get(ms, {})
        ket_qua.append({
            "ma_sach": ms,
            "ten_sach": s_info.get("ten_sach", f"Sách #{ms}"),
            "the_loai": s_info.get("ten_the_loai", ""),
            "so_luong_ban": val["so_luong"],
            "tong_tien": val["thanh_tien"]
        })

    ket_qua.sort(key=lambda x: x["so_luong_ban"], reverse=True)
    return ket_qua[:limit]


def thong_ke_sach_ton_kho_canh_bao():
    """Kiểm soát tồn kho: Lấy danh sách các đầu sách có số lượng tồn <= mức tồn tối thiểu."""
    ds_sach = sach.lay_danh_sach_sach()
    ket_qua = []
    for s in ds_sach:
        sl_ton = int(s.get("so_luong_ton", 0))
        min_ton = int(s.get("muc_ton_toi_thieu", 5))
        if sl_ton <= min_ton:
            ket_qua.append(s)

    ket_qua.sort(key=lambda x: int(x.get("so_luong_ton", 0)))
    return ket_qua


def thong_ke_doanh_so_nhan_vien():
    """Thống kê doanh số và số hóa đơn theo từng nhân viên."""
    ds_hd = luu_tru.doc_csv("hoa_don")
    ds_cthd = luu_tru.doc_csv("chi_tiet_hoa_don")
    ds_nv = luu_tru.doc_csv("nhan_vien")

    tien_hd = {}
    for ct in ds_cthd:
        mhd = str(ct.get("ma_hd"))
        sl = int(ct.get("so_luong", 0))
        dg = float(ct.get("don_gia_ban", 0))
        gg = float(ct.get("giam_gia", 0))
        tien_hd[mhd] = tien_hd.get(mhd, 0) + max(0, (sl * dg) - gg)

    nv_stats = {str(nv.get("ma_nv")): {
        "ma_nv": nv.get("ma_nv"),
        "ma_nhan_vien": nv.get("ma_nhan_vien"),
        "ho_ten": nv.get("ho_ten"),
        "ten_dang_nhap": nv.get("ten_dang_nhap"),
        "so_don": 0,
        "doanh_thu": 0
    } for nv in ds_nv}

    for hd in ds_hd:
        if hd.get("trang_thai") != "Hoàn thành":
            continue
        mnv = str(hd.get("ma_nv"))
        mhd = str(hd.get("ma_hd"))
        gg_tong = float(hd.get("giam_gia", 0))
        tien_don = max(0, tien_hd.get(mhd, 0) - gg_tong)

        if mnv in nv_stats:
            nv_stats[mnv]["so_don"] += 1
            nv_stats[mnv]["doanh_thu"] += tien_don

    ket_qua = list(nv_stats.values())
    ket_qua.sort(key=lambda x: x["doanh_thu"], reverse=True)
    return ket_qua


# ==========================================
# XUẤT BÁO CÁO EXCEL VỚI OPENPYXL
# ==========================================
def xuat_bao_cao_excel(file_path):
    """Xuất báo cáo tổng hợp (Doanh thu, Sách bán chạy, Cảnh báo kho) ra file Excel."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    wb = Workbook()

    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    # 1. Sheet Doanh Thu
    ws_rev = wb.active
    ws_rev.title = "Doanh thu ban sach"
    ws_rev.views.sheetView[0].showGridLines = True

    ws_rev.merge_cells("A1:C1")
    ws_rev["A1"] = "BÁO CÁO DOANH THU BÁN SÁCH"
    ws_rev["A1"].font = Font(name="Calibri", size=15, bold=True, color="1F497D")
    ws_rev["A1"].alignment = center_align

    rev_data = thong_ke_doanh_thu()
    ws_rev["A2"] = f"Tổng số đơn: {rev_data['tong_so_don']} | Tổng doanh thu: {rev_data['tong_doanh_thu']:,.0f} VNĐ"
    ws_rev["A2"].font = Font(name="Calibri", size=11, italic=True)

    headers_rev = ["Ngày giao dịch", "Số đơn hoàn thành", "Doanh thu (VNĐ)"]
    for col_idx, h in enumerate(headers_rev, 1):
        c = ws_rev.cell(row=4, column=col_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center_align

    r_idx = 5
    for item in rev_data["theo_ngay"]:
        ws_rev.cell(row=r_idx, column=1, value=item["ngay"]).alignment = center_align
        ws_rev.cell(row=r_idx, column=2, value=item["so_don"]).alignment = center_align
        c_rev = ws_rev.cell(row=r_idx, column=3, value=item["doanh_thu"])
        c_rev.number_format = '#,##0'
        c_rev.alignment = right_align
        for c in range(1, 4):
            ws_rev.cell(row=r_idx, column=c).border = thin_border
        r_idx += 1

    # 2. Sheet Sách bán chạy
    ws_top = wb.create_sheet(title="Top sach ban chay")
    ws_top.views.sheetView[0].showGridLines = True

    ws_top.merge_cells("A1:D1")
    ws_top["A1"] = "TOP SÁCH BÁN CHẠY NHẤT"
    ws_top["A1"].font = Font(name="Calibri", size=15, bold=True, color="1F497D")
    ws_top["A1"].alignment = center_align

    headers_top = ["Mã sách", "Tên sách", "Số lượng bán", "Doanh thu (VNĐ)"]
    for col_idx, h in enumerate(headers_top, 1):
        c = ws_top.cell(row=3, column=col_idx, value=h)
        c.font = header_font
        c.fill = header_fill
        c.alignment = center_align

    top_books = thong_ke_sach_ban_chay(20)
    r_idx = 4
    for b in top_books:
        ws_top.cell(row=r_idx, column=1, value=b["ma_sach"]).alignment = center_align
        ws_top.cell(row=r_idx, column=2, value=b["ten_sach"])
        ws_top.cell(row=r_idx, column=3, value=b["so_luong_ban"]).alignment = center_align
        c_t = ws_top.cell(row=r_idx, column=4, value=b["tong_tien"])
        c_t.number_format = '#,##0'
        c_t.alignment = right_align
        for c in range(1, 5):
            ws_top.cell(row=r_idx, column=c).border = thin_border
        r_idx += 1

    # 3. Sheet Cảnh báo tồn kho
    ws_warn = wb.create_sheet(title="Canh bao ton kho")
    ws_warn.views.sheetView[0].showGridLines = True

    ws_warn.merge_cells("A1:E1")
    ws_warn["A1"] = "DANH SÁCH SÁCH SẮP HẾT HÀNG (TỒN KHO THẤP)"
    ws_warn["A1"].font = Font(name="Calibri", size=15, bold=True, color="C00000")
    ws_warn["A1"].alignment = center_align

    headers_warn = ["Mã sách", "Tên sách", "Tác giả", "Tồn kho thực tế", "Mức tối thiểu"]
    for col_idx, h in enumerate(headers_warn, 1):
        c = ws_warn.cell(row=3, column=col_idx, value=h)
        c.font = header_font
        c.fill = PatternFill(start_color="C00000", end_color="C00000", fill_type="solid")
        c.alignment = center_align

    low_books = thong_ke_sach_ton_kho_canh_bao()
    r_idx = 4
    for b in low_books:
        ws_warn.cell(row=r_idx, column=1, value=b["ma_sach"]).alignment = center_align
        ws_warn.cell(row=r_idx, column=2, value=b["ten_sach"])
        ws_warn.cell(row=r_idx, column=3, value=b.get("tac_gia", ""))
        ws_warn.cell(row=r_idx, column=4, value=int(b.get("so_luong_ton", 0))).alignment = center_align
        ws_warn.cell(row=r_idx, column=5, value=int(b.get("muc_ton_toi_thieu", 5))).alignment = center_align
        for c in range(1, 6):
            ws_warn.cell(row=r_idx, column=c).border = thin_border
        r_idx += 1

    # Điều chỉnh độ rộng cột
    for ws in [ws_rev, ws_top, ws_warn]:
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row in range(1, ws.max_row + 1):
                cell_val = ws.cell(row=row, column=col_idx).value
                if cell_val is not None:
                    max_len = max(max_len, len(str(cell_val)))
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    wb.save(file_path)
    return True


# ==========================================
# XUẤT HÓA ĐƠN PDF VỚI REPORTLAB (HỖ TRỢ TIẾNG VIỆT)
# ==========================================
def xuat_hoa_don_pdf(file_path, ma_hd):
    """Xuất hóa đơn bán lẻ ra file PDF với ReportLab, hỗ trợ Unicode tiếng Việt."""
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    hd_info, items = hoa_don.lay_chi_tiet_hoa_don(ma_hd)
    if not hd_info:
        return False, "Không tìm thấy hóa đơn!"

    font_name = "Helvetica"
    font_bold = "Helvetica-Bold"
    font_paths = [
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\tahoma.ttf",
        "C:\\Windows\\Fonts\\times.ttf"
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                pdfmetrics.registerFont(TTFont("VNFont", fp))
                font_name = "VNFont"
                font_bold = "VNFont"
                break
            except Exception:
                pass

    doc = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'],
        fontName=font_bold, fontSize=18, alignment=1, textColor=colors.HexColor('#1F497D')
    )
    normal_style = ParagraphStyle(
        'NormalVN', parent=styles['Normal'],
        fontName=font_name, fontSize=10, leading=15
    )

    story = []
    story.append(Paragraph("NHÀ SÁCH TRI THỨC NAM CẦN THƠ", title_style))
    story.append(Paragraph("HÓA ĐƠN BÁN LẺ SÁCH", ParagraphStyle('Sub', parent=normal_style, alignment=1, fontSize=13, fontName=font_bold)))
    story.append(Paragraph(f"Mã hóa đơn: <b>{hd_info.get('ma_hoa_don')}</b> | Ngày lập: {hd_info.get('ngay_lap')}", ParagraphStyle('Sub2', parent=normal_style, alignment=1, textColor=colors.gray)))
    story.append(Spacer(1, 15))

    kh = hd_info.get("khach_hang_info", {})
    nv = hd_info.get("nhan_vien_info", {})
    info_p = f"""
    <b>Khách hàng:</b> {kh.get('ho_ten', 'Khách lẻ vãng lai')}<br/>
    <b>Số điện thoại:</b> {kh.get('so_dien_thoai') or '---'} | <b>Địa chỉ:</b> {kh.get('dia_chi') or '---'}<br/>
    <b>Nhân viên thu ngân:</b> {nv.get('ho_ten', 'Nhân viên')} | <b>Trạng thái:</b> {hd_info.get('trang_thai')}
    """
    story.append(Paragraph(info_p, normal_style))
    story.append(Spacer(1, 15))

    table_data = [["STT", "Tên sách", "Số lượng", "Đơn giá", "Giảm giá", "Thành tiền"]]
    for idx, it in enumerate(items, 1):
        table_data.append([
            str(idx),
            it["ten_sach"],
            str(it["so_luong"]),
            f"{it['don_gia_ban']:,.0f}",
            f"{it['giam_gia']:,.0f}",
            f"{it['thanh_tien']:,.0f}"
        ])

    table_data.append(["", "", "", "", "Tạm tính:", f"{hd_info.get('tam_tinh', 0):,.0f} đ"])
    table_data.append(["", "", "", "", "Tổng giảm giá:", f"{hd_info.get('tong_giam_gia', 0):,.0f} đ"])
    table_data.append(["", "", "", "", "THANH TOÁN:", f"{hd_info.get('tong_tien', 0):,.0f} VNĐ"])

    col_w = [30, 200, 50, 80, 70, 95]
    t = Table(table_data, colWidths=col_w)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -4), 0.5, colors.HexColor('#DDDDDD')),
        ('FONTNAME', (0, -1), (-1, -1), font_bold),
        ('FONTSIZE', (4, -1), (-1, -1), 10),
        ('TEXTCOLOR', (4, -1), (-1, -1), colors.HexColor('#B22222')),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))

    footer_text = "Cảm ơn Quý khách đã mua sách tại Nhà sách Tri Thức!<br/>Chúc Quý khách một ngày tốt lành và tràn đầy niềm vui!"
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, alignment=1, italic=True)))

    doc.build(story)
    return True, file_path
