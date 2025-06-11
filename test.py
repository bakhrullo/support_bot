from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        pass

    def footer(self):
        pass

pdf = PDF()
pdf.add_page()

# Подключаем шрифт с кириллицей
pdf.add_font('DejaVu', '', 'DejaVuSansCondensed.ttf', uni=True)
pdf.set_font("DejaVu", "", 11)

# Настройки
left_x = 10
right_x = 110
line_height = 6

# Контент
supplier_lines = [
    'ООО «SUPPORT SAMARQAND»',
    'г.Ташкент, Чиланзарский район,',
    'ул.Арнасай, 1А',
    'Р/с 20208000904736147002',
    'МФО 01070',
    'ТОШКЕНТ Ш., "INVEST FINANCE BANK"',
    'АЖ СЕРГЕЛИ ФИЛИАЛИ',
    'ИНН 300974584   ОКЭД 46360',
    'Тел: (871) 253-11-87',
    '',
    'Директор',
    'Абдуллаев  Д.Т. __________________'
]

buyer_lines = [
    '"SUPPORT SAMARQAND" MCHJ',
    'Адрес: ГОРОД ТАШКЕНТ ЧИЛОНЗАРСКИЙ РАЙОН ARNASOY KO`',
    'Р/сч: 20208000904736147001',
    'МФО: 00444',
    'в __________________________________',
    'ИНН: 300974584   ОКЭД: 46490',
    'Тел: (____) _________________________',
    '',
    'Директор',
    'ABDULLAYEV DAVRON TOXIROVICH'
]

# Вычисляем нужную Y-координату от низа страницы
max_lines = max(len(supplier_lines), len(buyer_lines))
block_height = max_lines * line_height + 25 # +10 — на заголовок
bottom_margin = 10
y = pdf.h - block_height - bottom_margin

# Заголовок
pdf.set_font('DejaVu', '', 10, )
pdf.set_xy(left_x, y)
pdf.cell(190, line_height, "10. ЮРИДИЧЕСКИЕ АДРЕСА И ПОДПИСИ СТОРОН:", ln=True)

pdf.set_font('DejaVu', '', 10, )
pdf.set_xy(left_x, y + line_height)
pdf.cell(90, line_height, "ПОСТАВЩИК", ln=0)
pdf.set_xy(right_x, y + line_height)
pdf.cell(90, line_height, "ПОКУПАТЕЛЬ", ln=1)

# Контент
pdf.set_font("DejaVu", "", 11)
for i in range(max_lines):
    pdf.set_xy(left_x, y + (i + 2) * line_height)
    if i < len(supplier_lines):
        pdf.cell(90, line_height, supplier_lines[i], ln=0)

    pdf.set_xy(right_x, y + (i + 2) * line_height)
    if i < len(buyer_lines):
        pdf.cell(90, line_height, buyer_lines[i], ln=0)

pdf.output("contract_footer.pdf")