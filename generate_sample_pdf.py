#!/usr/bin/env python3
"""
Генератор примера PDF сметы для демо.
В реальном продукте этот же шаблон используется на выходе после оплаты,
данные подставляются из расчёта движка.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from datetime import datetime, timedelta
import os

pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuOblique', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'))

INK = colors.HexColor('#1a1a1a')
MUTED = colors.HexColor('#6b6a64')
DIM = colors.HexColor('#9b9a94')
BORDER = colors.HexColor('#d4d2c8')
SOFT_BG = colors.HexColor('#f4f3ee')
ACCENT = colors.HexColor('#6d4eff')
ACCENT_LIGHT = colors.HexColor('#efeafe')
WHITE = colors.white


def make_styles():
    styles = {}
    styles['h1'] = ParagraphStyle('h1', fontName='DejaVuBold', fontSize=22,
                                   textColor=INK, leading=26, spaceAfter=4)
    styles['h2'] = ParagraphStyle('h2', fontName='DejaVuBold', fontSize=13,
                                   textColor=INK, leading=16, spaceAfter=4)
    styles['h3'] = ParagraphStyle('h3', fontName='DejaVuBold', fontSize=10,
                                   textColor=MUTED, leading=12, spaceAfter=6)
    styles['body'] = ParagraphStyle('body', fontName='DejaVu', fontSize=9.5,
                                     textColor=INK, leading=13, spaceAfter=4)
    styles['bodyMuted'] = ParagraphStyle('bodyMuted', fontName='DejaVu', fontSize=9,
                                          textColor=MUTED, leading=12, spaceAfter=3)
    styles['small'] = ParagraphStyle('small', fontName='DejaVu', fontSize=8,
                                      textColor=DIM, leading=10)
    styles['big'] = ParagraphStyle('big', fontName='DejaVuBold', fontSize=18,
                                    textColor=INK, leading=22, alignment=TA_RIGHT)
    styles['accentNum'] = ParagraphStyle('accentNum', fontName='DejaVuBold', fontSize=28,
                                          textColor=INK, leading=32, alignment=TA_RIGHT)
    styles['right'] = ParagraphStyle('right', fontName='DejaVu', fontSize=9.5,
                                      textColor=INK, leading=12, alignment=TA_RIGHT)
    styles['italic'] = ParagraphStyle('italic', fontName='DejaVuOblique', fontSize=9,
                                       textColor=MUTED, leading=12)
    styles['intro'] = ParagraphStyle('intro', fontName='DejaVu', fontSize=10,
                                      textColor=INK, leading=15, spaceAfter=8, alignment=TA_JUSTIFY)
    return styles


def fmt_rub(n):
    return f"{int(round(n)):,}".replace(',', '\u00A0') + ' ₽'


def build_header(styles, contractor_name, contractor_phone, doc_no, doc_date):
    brand_cell = Table([
        [Paragraph(f'<font face="DejaVuBold" size="13" color="#ffffff">С</font>',
                   ParagraphStyle('m', alignment=TA_CENTER))]
    ], colWidths=[12*mm], rowHeights=[12*mm])
    brand_cell.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), INK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('ROUNDEDCORNERS', [3, 3, 3, 3]),
    ]))

    left = Table([
        [brand_cell, Paragraph(
            f'<font face="DejaVuBold" size="13">Смета.AI</font><br/>'
            f'<font face="DejaVu" size="8" color="#6b6a64">черновик сметы за 5 минут</font>',
            styles['body'])]
    ], colWidths=[15*mm, 60*mm])
    left.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))

    right = Paragraph(
        f'<font face="DejaVuBold" size="9">{contractor_name}</font><br/>'
        f'<font face="DejaVu" size="8" color="#6b6a64">{contractor_phone}</font><br/>'
        f'<font face="DejaVu" size="8" color="#6b6a64">Смета № {doc_no} · {doc_date}</font>',
        styles['right'])

    header = Table([[left, right]], colWidths=[95*mm, 80*mm])
    header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, BORDER),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
    ]))
    return header


def build_summary_block(styles, client_name, object_descr, area, region, total):
    left_cell = Paragraph(
        f'<font face="DejaVuBold" size="10" color="#6b6a64">ЗАКАЗЧИК</font><br/>'
        f'<font face="DejaVu" size="11">{client_name}</font><br/><br/>'
        f'<font face="DejaVuBold" size="10" color="#6b6a64">ОБЪЕКТ</font><br/>'
        f'<font face="DejaVu" size="10">{object_descr}</font><br/>'
        f'<font face="DejaVu" size="9" color="#6b6a64">Площадь {area} м² · {region}</font>',
        styles['body'])

    right_cell = Paragraph(
        f'<font face="DejaVu" size="9" color="#6b6a64">Сметная стоимость</font><br/><br/>'
        f'<font face="DejaVuBold" size="20">{fmt_rub(total)}</font><br/><br/>'
        f'<font face="DejaVu" size="8" color="#9b9a94">включая НДС, накладные<br/>и плановую прибыль</font>',
        styles['right'])

    block = Table([[left_cell, right_cell]], colWidths=[100*mm, 75*mm])
    block.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), SOFT_BG),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 14),
        ('RIGHTPADDING', (0, 0), (-1, -1), 14),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
    ]))
    return block


def build_intro(styles):
    text = (
        'Сметная документация подготовлена на основе типовых норм ФЕР с применением '
        'регионального коэффициента и актуальных рыночных цен материалов на дату расчёта. '
        'Сметная стоимость включает все основные виды работ по возведению одноэтажного '
        'жилого дома из газобетонных блоков на ленточном фундаменте, с двускатной кровлей '
        'из металлочерепицы, без выполнения внутренней отделки и благоустройства территории.'
    )
    return Paragraph(text, styles['intro'])


def build_smeta_table(styles, rows):
    header_row = [
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">№</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">Наименование работ</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">Ед.</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">Кол-во</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">Цена за ед.</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8">Сумма, ₽</font>', styles['body']),
    ]

    table_data = [header_row]

    current_section = None
    section_starts = []

    for row in rows:
        if row.get('section'):
            section_starts.append(len(table_data))
            table_data.append([
                '', Paragraph(f'<font face="DejaVuBold" size="9">{row["section"]}</font>',
                              styles['body']), '', '', '', ''
            ])
        else:
            table_data.append([
                Paragraph(f'<font face="DejaVu" size="8">{row["n"]}</font>', styles['body']),
                Paragraph(f'<font face="DejaVu" size="8.5">{row["name"]}</font>', styles['body']),
                Paragraph(f'<font face="DejaVu" size="8">{row["unit"]}</font>', styles['body']),
                Paragraph(f'<font face="DejaVu" size="8">{row["qty"]}</font>', styles['body']),
                Paragraph(f'<font face="DejaVu" size="8">{fmt_rub(row["price"])}</font>', styles['body']),
                Paragraph(f'<font face="DejaVu" size="8.5">{fmt_rub(row["sum"])}</font>', styles['body']),
            ])

    t = Table(table_data, colWidths=[10*mm, 76*mm, 14*mm, 16*mm, 26*mm, 28*mm], repeatRows=1)

    style = [
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('TEXTCOLOR', (0, 0), (-1, 0), WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'DejaVuBold'),
        ('ALIGN', (2, 0), (5, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, BORDER),
        ('LINEBELOW', (0, 0), (-1, 0), 0.7, INK),
    ]

    for s_idx in section_starts:
        style.append(('BACKGROUND', (0, s_idx), (-1, s_idx), SOFT_BG))
        style.append(('LINEABOVE', (0, s_idx), (-1, s_idx), 0.5, BORDER))

    t.setStyle(TableStyle(style))
    return t


def build_totals(styles, subtotal, overhead, profit, total):
    rows = [
        [Paragraph('<font face="DejaVu" size="9.5" color="#6b6a64">Прямые затраты</font>', styles['body']),
         Paragraph(f'<font face="DejaVu" size="9.5">{fmt_rub(subtotal)}</font>', styles['right'])],
        [Paragraph('<font face="DejaVu" size="9.5" color="#6b6a64">Накладные расходы (15%)</font>', styles['body']),
         Paragraph(f'<font face="DejaVu" size="9.5">{fmt_rub(overhead)}</font>', styles['right'])],
        [Paragraph('<font face="DejaVu" size="9.5" color="#6b6a64">Плановая прибыль (8%)</font>', styles['body']),
         Paragraph(f'<font face="DejaVu" size="9.5">{fmt_rub(profit)}</font>', styles['right'])],
        [Paragraph('<font face="DejaVuBold" size="11">ИТОГО</font>', styles['body']),
         Paragraph(f'<font face="DejaVuBold" size="13">{fmt_rub(total)}</font>', styles['right'])],
    ]
    t = Table(rows, colWidths=[140*mm, 35*mm])
    t.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, BORDER),
        ('LINEABOVE', (0, -1), (-1, -1), 1.5, INK),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def build_payment_schedule(styles, total):
    stages = [
        ('Подготовительные работы и фундамент', 0.25, '7–10 дней'),
        ('Возведение коробки дома', 0.35, '20–25 дней'),
        ('Кровля и заполнение проёмов', 0.20, '12–15 дней'),
        ('Финальные работы и сдача объекта', 0.20, '7–10 дней'),
    ]
    rows = [[
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8.5">Этап</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8.5">% от стоимости</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8.5">Сумма</font>', styles['body']),
        Paragraph('<font face="DejaVuBold" color="#ffffff" size="8.5">Срок</font>', styles['body']),
    ]]
    for name, pct, period in stages:
        rows.append([
            Paragraph(f'<font face="DejaVu" size="9">{name}</font>', styles['body']),
            Paragraph(f'<font face="DejaVu" size="9">{int(pct*100)}%</font>', styles['body']),
            Paragraph(f'<font face="DejaVu" size="9">{fmt_rub(total * pct)}</font>', styles['body']),
            Paragraph(f'<font face="DejaVu" size="9">{period}</font>', styles['body']),
        ])
    t = Table(rows, colWidths=[80*mm, 30*mm, 35*mm, 30*mm])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), INK),
        ('ALIGN', (1, 0), (3, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return t


def build_terms(styles):
    items = [
        ('Сроки', 'Общий срок строительства — 50–60 рабочих дней с момента начала работ.'),
        ('Гарантия', 'Гарантия на коробку дома — 5 лет, на инженерные системы — 2 года.'),
        ('Изменения', 'Изменение стоимости возможно при отклонении геологии участка или удорожании материалов более 10%.'),
        ('Сметная стоимость', 'Действует 30 дней с даты составления.'),
    ]
    rows = []
    for title, text in items:
        rows.append([
            Paragraph(f'<font face="DejaVuBold" size="9">{title}</font>', styles['body']),
            Paragraph(f'<font face="DejaVu" size="9" color="#3a3a3a">{text}</font>', styles['body']),
        ])
    t = Table(rows, colWidths=[35*mm, 140*mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), 0.3, BORDER),
    ]))
    return t


def build_footer_signature(styles, contractor_name):
    today = datetime.now().strftime('%d.%m.%Y')
    rows = [[
        Paragraph(
            f'<font face="DejaVu" size="9" color="#6b6a64">Исполнитель</font><br/>'
            f'<font face="DejaVuBold" size="10">{contractor_name}</font><br/><br/>'
            f'<font face="DejaVu" size="9">_______________________</font><br/>'
            f'<font face="DejaVu" size="8" color="#9b9a94">подпись · {today}</font>',
            styles['body']),
        Paragraph(
            f'<font face="DejaVu" size="9" color="#6b6a64">Заказчик</font><br/>'
            f'<font face="DejaVuBold" size="10">Иванов И.И.</font><br/><br/>'
            f'<font face="DejaVu" size="9">_______________________</font><br/>'
            f'<font face="DejaVu" size="8" color="#9b9a94">подпись · {today}</font>',
            styles['body']),
    ]]
    t = Table(rows, colWidths=[88*mm, 88*mm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 14),
    ]))
    return t


def build_branding_footer(styles):
    txt = (
        '<font face="DejaVu" size="7" color="#9b9a94">Документ сгенерирован сервисом '
        '<font face="DejaVuBold">Смета.AI</font> — черновик сметы за 5 минут для подрядчиков ИЖС. '
        'Каждый расчёт сверяется со сметчиком-консультантом. '
        'Точность ±10%. Документ носит ознакомительный характер до подписания договора подряда.</font>'
    )
    return Paragraph(txt, styles['small'])


def main():
    output = os.path.join(os.path.dirname(__file__), 'sample-smeta.pdf')

    doc = SimpleDocTemplate(
        output, pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=15*mm, bottomMargin=15*mm,
        title='Смета на строительство ИЖС',
        author='Смета.AI'
    )

    styles = make_styles()
    story = []

    story.append(build_header(
        styles,
        contractor_name='ООО «СтройДом-Подмосковье»',
        contractor_phone='+7 (495) 555-12-34',
        doc_no='2026-0247',
        doc_date='17 мая 2026'
    ))
    story.append(Spacer(1, 10*mm))

    story.append(Paragraph('Локальная смета на строительство', styles['h1']))
    story.append(Paragraph(
        'Одноэтажный жилой дом из газобетонных блоков · с ленточным фундаментом и металлочерепицей',
        styles['bodyMuted']))
    story.append(Spacer(1, 8*mm))

    rows_data = [
        {'section': '1. Земляные работы и подготовка'},
        {'n': '1.1', 'name': 'Разметка осей и планировка участка', 'unit': 'м²', 'qty': '120', 'price': 180, 'sum': 21_600},
        {'n': '1.2', 'name': 'Разработка грунта вручную и механизировано', 'unit': 'м³', 'qty': '38', 'price': 1_200, 'sum': 45_600},

        {'section': '2. Устройство фундамента'},
        {'n': '2.1', 'name': 'Песчано-щебёночная подготовка', 'unit': 'м³', 'qty': '7,2', 'price': 2_400, 'sum': 17_280},
        {'n': '2.2', 'name': 'Армирование сеткой A-III', 'unit': 'т', 'qty': '1,2', 'price': 88_000, 'sum': 105_600},
        {'n': '2.3', 'name': 'Заливка фундамента бетоном B22.5', 'unit': 'м³', 'qty': '18', 'price': 12_500, 'sum': 225_000},
        {'n': '2.4', 'name': 'Гидроизоляция обмазочная', 'unit': 'м²', 'qty': '64', 'price': 820, 'sum': 52_480},

        {'section': '3. Возведение коробки дома'},
        {'n': '3.1', 'name': 'Кладка стен из газобетона D500, 300 мм', 'unit': 'м³', 'qty': '42', 'price': 13_500, 'sum': 567_000},
        {'n': '3.2', 'name': 'Армопояс по верху стен, монолит', 'unit': 'м.п.', 'qty': '38', 'price': 4_200, 'sum': 159_600},
        {'n': '3.3', 'name': 'Перегородки 100 мм', 'unit': 'м²', 'qty': '36', 'price': 2_400, 'sum': 86_400},
        {'n': '3.4', 'name': 'Кладочный раствор, материалы', 'unit': 'компл', 'qty': '1', 'price': 145_000, 'sum': 145_000},

        {'section': '4. Перекрытия'},
        {'n': '4.1', 'name': 'Перекрытие монолитное по балкам', 'unit': 'м²', 'qty': '120', 'price': 2_400, 'sum': 288_000},

        {'section': '5. Кровля'},
        {'n': '5.1', 'name': 'Стропильная система, обрешётка', 'unit': 'м²', 'qty': '156', 'price': 1_200, 'sum': 187_200},
        {'n': '5.2', 'name': 'Гидро- и пароизоляция, утепление', 'unit': 'м²', 'qty': '156', 'price': 850, 'sum': 132_600},
        {'n': '5.3', 'name': 'Покрытие металлочерепицей', 'unit': 'м²', 'qty': '156', 'price': 1_950, 'sum': 304_200},
        {'n': '5.4', 'name': 'Водосточная система', 'unit': 'компл', 'qty': '1', 'price': 48_000, 'sum': 48_000},

        {'section': '6. Окна, двери, фасад'},
        {'n': '6.1', 'name': 'Окна ПВХ двухкамерные с монтажом', 'unit': 'м²', 'qty': '20', 'price': 8_500, 'sum': 170_000},
        {'n': '6.2', 'name': 'Двери входные металлические', 'unit': 'шт', 'qty': '1', 'price': 32_000, 'sum': 32_000},
        {'n': '6.3', 'name': 'Двери межкомнатные', 'unit': 'шт', 'qty': '5', 'price': 10_500, 'sum': 52_500},
        {'n': '6.4', 'name': 'Штукатурка фасада с покраской', 'unit': 'м²', 'qty': '110', 'price': 920, 'sum': 101_200},

        {'section': '7. Инженерные сети'},
        {'n': '7.1', 'name': 'Электрика — разводка, щит, освещение', 'unit': 'м²', 'qty': '120', 'price': 1_650, 'sum': 198_000},
        {'n': '7.2', 'name': 'Водопровод и канализация', 'unit': 'м²', 'qty': '120', 'price': 1_200, 'sum': 144_000},
        {'n': '7.3', 'name': 'Котёл газовый, монтаж отопления', 'unit': 'компл', 'qty': '1', 'price': 215_000, 'sum': 215_000},

        {'section': '8. Прочее'},
        {'n': '8.1', 'name': 'Доставка материалов и логистика', 'unit': 'мес', 'qty': '2,5', 'price': 14_000, 'sum': 35_000},
        {'n': '8.2', 'name': 'Вывоз строительного мусора', 'unit': 'м³', 'qty': '12', 'price': 2_500, 'sum': 30_000},
    ]

    subtotal = sum(r['sum'] for r in rows_data if 'sum' in r)
    overhead = subtotal * 0.15
    profit = subtotal * 0.08
    total = subtotal + overhead + profit

    story.append(build_summary_block(
        styles,
        client_name='Иванов Иван Иванович',
        object_descr='ИЖС, дер. Лесная, уч. 47',
        area='120',
        region='Московская область',
        total=total
    ))
    story.append(Spacer(1, 6*mm))

    story.append(build_intro(styles))
    story.append(Spacer(1, 4*mm))

    story.append(build_smeta_table(styles, rows_data))
    story.append(Spacer(1, 8*mm))
    story.append(build_totals(styles, subtotal, overhead, profit, total))
    story.append(Spacer(1, 10*mm))

    story.append(PageBreak())

    story.append(Paragraph('Условия и порядок оплаты', styles['h2']))
    story.append(Spacer(1, 3*mm))
    story.append(build_payment_schedule(styles, total))
    story.append(Spacer(1, 8*mm))

    story.append(Paragraph('Гарантии и условия', styles['h2']))
    story.append(Spacer(1, 3*mm))
    story.append(build_terms(styles))
    story.append(Spacer(1, 12*mm))

    story.append(build_footer_signature(styles, 'ООО «СтройДом-Подмосковье»'))
    story.append(Spacer(1, 14*mm))
    story.append(build_branding_footer(styles))

    doc.build(story)
    print(f'PDF создан: {output}')
    print(f'Размер: {os.path.getsize(output)} байт')


if __name__ == '__main__':
    main()
