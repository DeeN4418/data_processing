##Программа для обработки нескольких файлов долговременных измерений эмиссионого тока, расположенных
##в одной папке.
##Производится очистка файлов от вспомогательных колонок после чего производится 
##определение среднего тока и его стандартного отклонения.


import math
import os
from os import listdir

#ф-я для расчета стандартного отклонения тока 
def stand_div(filename, Imid, N):
    Ii = 0.0
    SD = 0.0
    file = open(filename, "r")
    try:  #создаем обработку исключений, на случай ошибок, чтобы файл закрылся
        for line in file: #считываем построчно содержимое файла
            str_=line.split() #каждую строку делим на части, отделенные пробелами            
            if str_[3]!='Uзад' and str_[7]!='Iимп [А]':                
                Ii = Ii + pow((float(str_[7]) - Imid),2)
        SD = math.sqrt(Ii/(N-1))
    finally:    
        file.close()
    return SD
###################################################
#ф-я по очищению файлов от лишних данных, сборка их в отдельные файлы, а также
##расчет средних величин
##на выходе имеем два файла в одном данные по всем измерениям,
##во втором усреднные значения и стандоткл
def clear_data(filename): 
    print('filename= ', filename)              
    file = open(filename, "r") #открываем исходный файл, считываем из него нужные данные
    temp=open('results/results_clr'+'.txt',"a") #создаем файл, в который записываем напряжение и ток
    temp_mid=open('results/results_mid'+'.txt',"a") #создаем файл, в который записываем напряжение и ток
    count = 0
    U_mid = 0.0
    I_mid = 0.0
    SD = 0.0
    try:  #создаем обработку исключений, на случай ошибок, чтобы файл закрылся
        for line in file: #считываем построчно содержимое файла
            
            str_=line.split() #каждую строку делим на части, отделенные пробелами
            if str_[3]!='Uзад' and str_[7]!='Iимп [А]': #отбрасываем заголовки столцов                   
                temp.write(str_[3]+" "+str_[7]+"\n")
                count = count + 1
                U_mid = U_mid + float(str_[3])
                I_mid = I_mid + float(str_[7])
        U_mid = U_mid / count
        I_mid = I_mid / count

        SD = stand_div(filename, I_mid, count)    
        print('count= ', count)
        print('U_mid= ', U_mid)
        print('I_mid= ', I_mid)
        print('SD= ', SD)
         
        temp_mid.write(filename +" "+str(U_mid) +" "+str(I_mid)+" "+str(SD)+"\n")
    finally:    
        file.close()#закрываем файл
        temp.write("\n")
        temp.close()        
        temp_mid.close()
############################################
def resfile_title(): #ф-я для создания результирующего файла с расчетными данными
    temp=open('results/results_mid.txt',"w") #создаем результирующий файл для записи   
    try:
        temp.write('filename'+" "+'U_mid'+' '+'I_mid'+' '+'SD'+"\n")            
    finally:        
        temp.close()        
############################################
directory = r'data_series'
files = listdir(directory)
if not os.path.isdir("results_series"): #проверяем есть ли директория results, если не - создаем
    os.mkdir("results_series")
else:
    pass
resfile_title()
#print(len(files))
for i in range(len(files)):    
    clear_data('data_series\\'+ files[i])
    