#программа для обработки файлов, получаемых при измерениях АЭ ВАХ
#на характериографе Эрбий

import math
import os
from os import listdir


###############################################################
#функция для очистки файлов от нулевых значений и лишних колонок
#работа с исходным файлом данных - выбор ненулевых значений тока, и соответствующего ему напряжения,
#на вход подаем имя текстового файла без расширения
#на выходе получаем временный файл с ненулевыми значениями тока и напряжения

def clear_data(filename, filename2): 
    #file = open(filename+'.txt', "r")              
    file = open(filename, "r") #открываем исходный файл, считываем из него нужные данные
    temp=open('results/'+filename2+'_clr'+'.txt',"w") #создаем файл, в который записываем напряжение и ток
    U = []
    I = []
      
    try:  #создаем обработку исключений, на случай ошибок, чтобы файл закрылся
        for line in file: #считываем построчно содержимое файла
            str_=line.split() #каждую строку делим на части, отделенные пробелами
            
            if str_[3]!='Uзад' and str_[7]!='Iимп [А]': #отбрасываем заголовки столцов
                
                U.append(str_[3])
                I.append(str_[7])

       
        for i in range(len(U)):
##            while i<len(U):
                if float(I[i-1])> float(I[i]) and float(I[i])==0.0:#убираем нулевые значения токов
                    i=i+1
                    continue
                elif float(I[i])>0.0 and float(I[i-1])<float(I[i]) and i<len(U):#если ток больше нуля, то пишем в файл напряжение и ток                       
                    temp.write(U[i]+" "+I[i]+"\n")
                        
    finally:    
        file.close()#закрываем файл
        temp.close()
###############################################################
#ф-я для удаления пробоев в конце измерений по отношению
#на вход подаем файл, очищенный с помощью clear_data(filename)
#на выходе получаем два массива с очищенными данными
def data_without_breakedown2(filename):     
    temp=open('results/'+filename+'_clr'+'.txt',"r") #открываем ранее полученный файл с током и напряжением на чтение
    #создание двух списков с передачей в них данных из временного файла
    u=[]
    i=[]
    #извлекаем данные из файла и передаем их в списки
    try:
        for line in temp:
            str_=line.split()        
            u.append(float(str_[0]))
            i.append(float(str_[1]))    
    finally:
        temp.close()        
    #создание второго временного файла, куда записываются данные без пробоев
    temp2=open('results/'+filename+'_wbd'+'.txt',"w")#открываем файл для записи данных без пробоев
    try:
    ##    #создаем еще два списка, куда будет записывать данные без пробоев
        u_clr=[]
        i_clr=[]       
        for n in range(len(u)): #опять проходим по всей длине первого списка
            if (float(i[n])/ float(i[n-1])) < 7: #сравниваем чтобы отношение тока текущего и предыдущего было меньше 7 (определено эмпирически), если она меньше, то этот ток и напряжение пишем в файл
                u_clr.append(u[n]) #записываем напряжение, извлеченное из первого списка во второй
                i_clr.append(i[n])
                temp2.write(str(u[n])+" "+str(i[n])+"\n")    #записываем извлеченные данные во второй временный файл        
            else:      #в противном случае прерываем цикл, и останавливаемся на последнем значении перед пробоем 
                break 
    finally:
        temp2.close()
    return u_clr, i_clr   

###############################################################

###############################################################
#программа для определения коэффициентов а и k из уравнения y = ae^(kx)
###############################################################
def factor_a(x,y): #ф-я для опр. коэфф "а"
    sum_x=0
    sum_x2=0    
    sum_lny=0.0
    sum_lnyx=0
    sum2_x=0
    for i in range(len(x)):        
        sum_x=sum_x+x[i]        
        sum_x2=sum_x2+x[i]**2        
        sum_lny=sum_lny+math.log(y[i])
        sum_lnyx=sum_lnyx+math.log(y[i])*x[i]
        sum2_x=sum_x**2
    
    a=(sum_lny*sum_x2-sum_lnyx*sum_x)/(len(x)*sum_x2-sum2_x)
    return math.exp(a)
###############################################################
def factor_b(x,y): #ф-я для опр. коэфф "b" он же коэффициент k для напр в Вольтах и тока в Амперах
    sum_x=0    
    sum_x2=0    
    sum_lny=0
    sum_lnyx=0
    sum2_x=0
    for i in range(len(x)):        
        sum_x=sum_x+x[i]        
        sum_x2=sum_x2+x[i]**2        
        sum_lny=sum_lny+math.log(y[i])
        sum_lnyx=sum_lnyx+math.log(y[i])*x[i]
        sum2_x=sum_x**2
        
    b=(len(x)*sum_lnyx-sum_lny*sum_x)/(len(x)*sum_x2-sum2_x)    
    return b
###############################################################
#ф-я для выбора порогового и максимального напряжений, а также допробойного тока
def parameters(massiveU,massiveI):
    Utrh = massiveU[0]
    Umax = massiveU[-1]
    deltaU = Umax - Utrh
    Imax = massiveI[-1]
    return Utrh, Umax, deltaU, Imax

###############################################################
#результирующий файл с данными
###############################################################
def resfile_title(): #ф-я для создания результирующего файла с расчетными данными
    temp=open('results/resfile.txt',"w") #создаем результирующий файл для записи   
    try:
        temp.write('filename'+" "+'Utrh'+' '+'Umax'+' '+'deltaU'+' '+'Imax'+' '+'a'+" "+'k'+"\n")            
    finally:        
        temp.close()
        
def resfile(filename, Utrh, Umax, deltaU, Imax, a, k):
    temp=open('results/resfile.txt',"a") #открываем результирующий файл на добавление данных    
    try:
        temp.write(filename+':'+' '+Utrh+' '+Umax+' '+deltaU+' '+Imax+" "+a+" "+k+"\n")            
    finally:        
        temp.close()        
    
###############################################################
   
#создаем два списка, куда запишем напряжение и ток без пробоев
U=[]
I=[]


############################################
directory = r'data' #считываем названия сырых файлов из директории data
files = listdir(directory) #записываем имена файлов в список
if not os.path.isdir("results"): #проверяем есть ли директория results, если не - создаем
    os.mkdir("results")
else:
    pass



resfile_title() #запускаем ф-ю для создания результирующего файла
for i in range(len(files)):
    print(files[i])    
    filename = 'data\\'+ files[i]
    filename2 = files[i]
    clear_data(filename, filename2) #выбираем из файла нужные данные без нулей    
    print('filename:',filename2, 'проведена первоначальная обработка')
    U, I = data_without_breakedown2(filename2)    
    print('filename:',filename2, 'проведено удаление пробоев')
    a = factor_a(U,I)
    b = factor_b(U,I)
    Utrh, Umax, deltaU, Imax = parameters(U,I)
    resfile(filename, str(Utrh), str(Umax), str(deltaU), str(Imax), str(a), str(b))

    



