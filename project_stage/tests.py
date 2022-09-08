# from django.test import TestCase
import xlrd
from .models import SpeciesInfo
from django.http import HttpResponse
# Create your tests here.


def species_import(request):

    if request.method == 'GET':
        excel_path = "D:\\PyProgram\\Spec-ally\\database_20220810.xls"

        # 打开文件，获取excel文件的workbook（工作簿）对象
        excel = xlrd.open_workbook(excel_path, encoding_override="utf-8")

        # 获取第一个sheet对象
        sheet = excel.sheets()[0]
        sheet_row_mount = sheet.nrows  # 总行数
        sheet_col_mount = sheet.ncols  # 总列数

        print(sheet_row_mount, sheet_col_mount)
        for each_row in range(1, sheet_row_mount):
            row_data = sheet.row_values(each_row)

            database = row_data[0]
            entry_count = row_data[2]
            species = row_data[3]
            creator = "孙冬冬"
            info = SpeciesInfo.objects.create(database=database, entry_count=entry_count, species=species,
                                              creator=creator)

        msg = "import_success"
        return HttpResponse(msg)
