import os
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def export_revenue_to_excel(file_path, report_data):
    """Xuất báo cáo doanh thu ra file Excel."""
    wb = Workbook()

    # Sheet 1: Tổng quan & Theo ngày
    ws1 = wb.active
    ws1.title = "Doanh thu theo ngay"
    ws1.views.sheetView[0].showGridLines = True

    header_font = Font(name="Calibri", size=12, bold=True, color="FFFFFF")
    header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='DDDDDD'),
        right=Side(style='thin', color='DDDDDD'),
        top=Side(style='thin', color='DDDDDD'),
        bottom=Side(style='thin', color='DDDDDD')
    )

    # Tiêu đề
    ws1.merge_cells("A1:C1")
    ws1["A1"] = "BÁO CÁO DOANH THU BÁN SÁCH"
    ws1["A1"].font = Font(name="Calibri", size=16, bold=True, color="1F497D")
    ws1["A1"].alignment = center_align

    # Header bảng
    headers = ["Ngày giao dịch", "Số đơn hàng", "Doanh thu (VNĐ)"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws1.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    row_idx = 4
    for item in report_data.get("daily", []):
        ws1.cell(row=row_idx, column=1, value=item["Ngay"]).alignment = center_align
        ws1.cell(row=row_idx, column=2, value=item["SoDon"]).alignment = center_align
        cell_rev = ws1.cell(row=row_idx, column=3, value=item["DoanhThu"])
        cell_rev.number_format = '#,##0'
        cell_rev.alignment = right_align

        for c in range(1, 4):
            ws1.cell(row=row_idx, column=c).border = thin_border
        row_idx += 1

    # Sheet 2: Doanh thu theo tháng
    ws2 = wb.create_sheet(title="Doanh thu theo thang")
    ws2.views.sheetView[0].showGridLines = True

    ws2.merge_cells("A1:C1")
    ws2["A1"] = "DOANH THU THEO THÁNG"
    ws2["A1"].font = Font(name="Calibri", size=14, bold=True, color="1F497D")
    ws2["A1"].alignment = center_align

    headers_m = ["Tháng", "Số đơn hàng", "Doanh thu (VNĐ)"]
    for col_idx, h in enumerate(headers_m, 1):
        cell = ws2.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = center_align

    row_idx = 4
    for item in report_data.get("monthly", []):
        ws2.cell(row=row_idx, column=1, value=item["Thang"]).alignment = center_align
        ws2.cell(row=row_idx, column=2, value=item["SoDon"]).alignment = center_align
        cell_rev = ws2.cell(row=row_idx, column=3, value=item["DoanhThu"])
        cell_rev.number_format = '#,##0'
        cell_rev.alignment = right_align

        for c in range(1, 4):
            ws2.cell(row=row_idx, column=c).border = thin_border
        row_idx += 1

    # Tự động căn chỉnh độ rộng cột
    for ws in [ws1, ws2]:
        for col_idx in range(1, ws.max_column + 1):
            col_letter = get_column_letter(col_idx)
            max_len = 0
            for row in range(1, ws.max_row + 1):
                cell_val = ws.cell(row=row, column=col_idx).value
                if cell_val is not None:
                    max_len = max(max_len, len(str(cell_val)))
            ws.column_dimensions[col_letter].width = max(max_len + 5, 15)

    wb.save(file_path)
    return True


def export_invoice_to_pdf(file_path, order_info, items):
    """Xuất hóa đơn bán hàng ra file PDF chuẩn khổ A4."""
    # Đăng ký font hỗ trợ tiếng Việt nếu có trong hệ thống Windows
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
                pdfmetrics.registerFont(TTFont("CustomVN", fp))
                font_name = "CustomVN"
                font_bold = "CustomVN"
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
        'InvoiceTitle',
        parent=styles['Heading1'],
        fontName=font_bold,
        fontSize=20,
        alignment=1, # Center
        spaceAfter=15,
        textColor=colors.HexColor('#1F497D')
    )

    normal_style = ParagraphStyle(
        'InvoiceNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=11,
        leading=16
    )

    story = []

    # Tiêu đề
    story.append(Paragraph("HÓA ĐƠN BÁN SÁCH", title_style))
    story.append(Paragraph("NHÀ SÁCH TRI THỨC NAM CẦN THƠ", ParagraphStyle('Sub', parent=normal_style, alignment=1, fontSize=12)))
    story.append(Paragraph(f"Mã hóa đơn: HD{order_info['MaHD']:05d} - Ngày lập: {order_info['NgayLap']}", ParagraphStyle('Sub2', parent=normal_style, alignment=1, fontSize=10, textColor=colors.gray)))
    story.append(Spacer(1, 15))

    # Thông tin khách hàng & nhân viên
    info_text = f"""
    <b>Khách hàng:</b> {order_info.get('TenKH') or 'Khách vãng lai'}<br/>
    <b>Số điện thoại:</b> {order_info.get('SDTKhach') or '---'}<br/>
    <b>Thu ngân:</b> {order_info.get('TenNV') or '---'}
    """
    story.append(Paragraph(info_text, normal_style))
    story.append(Spacer(1, 15))

    # Bảng chi tiết sách
    table_data = [["STT", "Tên sách", "Số lượng", "Đơn giá (VNĐ)", "Thành tiền (VNĐ)"]]
    for idx, it in enumerate(items, 1):
        table_data.append([
            str(idx),
            it['TenSach'],
            str(it['SoLuong']),
            f"{it['GiaMua']:,.0f}",
            f"{it['ThanhTien']:,.0f}"
        ])

    table_data.append(["", "", "", "TỔNG TIỀN:", f"{order_info['TongTien']:,.0f} VNĐ"])

    col_widths = [35, 230, 60, 95, 110]
    t = Table(table_data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F497D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'CENTER'),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -2), 0.5, colors.HexColor('#DDDDDD')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#1F497D')),
        ('FONTNAME', (0, -1), (-1, -1), font_bold),
        ('FONTSIZE', (0, -1), (-1, -1), 11),
        ('TEXTCOLOR', (3, -1), (-1, -1), colors.HexColor('#B22222')),
    ]))
    story.append(t)
    story.append(Spacer(1, 25))

    footer_text = "Cảm ơn Quý khách đã mua sách! Hẹn gặp lại Quý khách."
    story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=normal_style, alignment=1, fontSize=10, italic=True)))

    doc.build(story)
    return True
