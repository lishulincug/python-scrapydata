# coding=GBK
import xlrd
import sys
#reload(sys)
#sys.setdefaultencoding('utf8')
#��ȡ��б���ʻ��еĴ���
data = xlrd.open_workbook(u"./ontologydata/word_emotion_ontology.xlsx")
table = data.sheets()[0]
nrows = table.nrows
ncols = table.ncols
print("һ����:",nrows,"��---",ncols,"��")


mydata = []

#ѭ�����б�����
for i in range(nrows):
    tempdata = [(table.row_values(i)[0]).encode("utf8"),(table.row_values(i)[4]).encode("utf-8")]
    #tempdata.append(table.row_values(i)[0])
    #tempdata.append(table.row_values(i)[4])
    mydata.append(tempdata)
    print("���Ϊ��",(tempdata[0]).decode("utf8"),"----�������Ϊ��",(tempdata[1]).decode("utf8"))