from django.test import TestCase

# Create your tests here.

# def unit_import(request):

# if request.method == 'GET':
#     excel_path = "D:\\PyProgram\\SpecAlly\\unit_info-20210524.xls"
#
#     # 打开文件，获取excel文件的workbook（工作簿）对象
#     excel = xlrd.open_workbook(excel_path, encoding_override="utf-8")
#
#     # 获取第一个sheet对象
#     sheet = excel.sheets()[0]
#     sheet_row_mount = sheet.nrows  # 总行数
#     sheet_col_mount = sheet.ncols  # 总列数
#
#     print(sheet_row_mount, sheet_col_mount)
#     for each_row in range(1, sheet_row_mount):
#         row_data = sheet.row_values(each_row)
#
#         unit_name = row_data[1]
#         duty_paragraph = row_data[2]
#         bank = row_data[3]
#         account = row_data[4]
#         address = row_data[5]
#         phone = row_data[6]
#         person_add = "管理员"
#         unit_new = UnitInvoice(unit_name=unit_name, duty_paragraph=duty_paragraph, bank=bank, account=account,
#                                address=address, phone=phone, person_add=person_add)
#         unit_new.save()
#     msg = "import_success"
#     return HttpResponse(msg)