import copy,tempfile,unittest,zipfile
from pathlib import Path
from xml.sax.saxutils import escape
from scripts.import_csu import HEADERS,load_first_sheet,transcribe

def fixture():
    rows=[HEADERS[:]]
    for n in range(1,27):
        start=(n-1)*6;end=start+(8 if n==26 else 6)
        tc=lambda x:f'{x//60:02d}:{x%60:02d}'
        rows.append([str(n),'section',tc(start),tc(end),str(end-start),'旁白' if n<26 else '', 'camera','visual','overlay','sound','method','review','待制作'])
    return rows

def write_xlsx(path,rows,shared=False):
    all_values=list(dict.fromkeys(v for row in rows for v in row));cells=[]
    for n,row in enumerate(rows,1):
        content=[]
        for col,value in enumerate(row):
            ref=chr(65+col)+str(n)
            body=f'<v>{all_values.index(value)}</v>' if shared else f'<is><t>{escape(value)}</t></is>'
            content.append(f'<c r="{ref}" t="'+('s' if shared else 'inlineStr')+f'">{body}</c>')
        cells.append(f'<row r="{n}">'+''.join(content)+'</row>')
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('xl/workbook.xml','<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Pilot" sheetId="7" r:id="rId7"/></sheets></workbook>')
        z.writestr('xl/_rels/workbook.xml.rels','<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId7" Target="worksheets/sheet7.xml"/></Relationships>')
        z.writestr('xl/worksheets/sheet7.xml','<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+''.join(cells)+'</sheetData></worksheet>')
        if shared:z.writestr('xl/sharedStrings.xml','<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'+''.join('<si><t>'+escape(v)+'</t></si>' for v in all_values)+'</sst>')
class ImportTests(unittest.TestCase):
    def test_missing_input(self):
        with self.assertRaises(FileNotFoundError):load_first_sheet('does-not-exist.xlsx')
    def test_real_layout_inline_and_shared(self):
        for shared in [False,True]:
            with self.subTest(shared=shared),tempfile.TemporaryDirectory() as d:
                p=Path(d)/'pilot.xlsx';write_xlsx(p,fixture(),shared)
                data=transcribe(load_first_sheet(p),'pilot.xlsx','hash')
                self.assertEqual(data['total_seconds'],158);self.assertEqual(data['shots'][-1]['narration'],'')
    def test_headers(self):
        rows=fixture();rows[0][5]='unexpected'
        with self.assertRaises(ValueError):transcribe(rows,'x','h')
    def test_same_total_wrong_individual_durations(self):
        rows=fixture();rows[1][4]='7';rows[2][4]='5'
        with self.assertRaises(ValueError):transcribe(rows,'x','h')
    def test_gap_overlap_and_duplicate(self):
        for col,value in [(2,'00:01'),(3,'00:05'),(0,'2')]:
            rows=fixture();rows[1][col]=value
            with self.subTest(col=col),self.assertRaises(ValueError):transcribe(rows,'x','h')
    def test_blank_narration_and_extra_row(self):
        rows=fixture();rows[1][5]=''
        with self.assertRaises(ValueError):transcribe(rows,'x','h')
        rows=fixture();rows.append(['footer'])
        with self.assertRaises(ValueError):transcribe(rows,'x','h')
