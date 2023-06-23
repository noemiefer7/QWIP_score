################################ PROCESSING_MODULE #######################################

#This module has been created to calculate the QWIP-score of datas collected by Pamela USV
#in the Mjosa Lake. 
#Before to use the module, all the files have to be in a same folder. 

##########################################################################################

import pandas as pd
import os 
import shutil


#create a new text file without the 7 first lines and without the unity of each component
#the parameters must be str
def rewrite_file (namefile, outputfile):
    with open(namefile,'r') as input_file:
        with open(outputfile,'w') as output:
            raw_data=input_file.readlines()
            output.write(raw_data[8])
            for i in range(10,len(raw_data)-1):
                output.write(raw_data[i])


#Use to create list for each component
#the parameters must be str
def extract_data(newfile, column):
# smaller sample data without tabs and original post data
    with open(newfile,'r') as data:
        # analyze header
        header = next(data)
        # first post had tab separation, second not. Adapth to situation
        header = [h.strip() for h in header.split('\t' if '\t' in header else None)]
        ind = header.index(column)
        # tab separation if exist, otherwise all white space splits
        column_extracted = [float(line.split('\t' if '\t' in line else None)[ind]) for line in data]
        return column_extracted            


#AVW calcul
#the parameter must be a str
def AVW (newfile):
    
    lambda_=extract_data(newfile,'Wavelength')
    Rrs=extract_data(newfile, 'Reflectance')
    c1=0
    c2=0
    n=len(Rrs)
    for i in range(n-1):
        c1+=Rrs[i]
        c2+=Rrs[i]/lambda_[i]
    return c1/c2


#QWIP_score calcul
#the parameter must be a str
def QWIP_score (newfile):
    '''
        https://www.frontiersin.org/articles/10.3389/frsen.2022.869611/full#:~:text=The%20QWIP%20score%20represents%20the,trends%20observed%20in%20aquatic%20optics.
    '''
   
    avw=AVW(newfile)
    p=[-8.399885*10**(-9),1.715532*10**(-5),-1.301670*10**(-2),4.357838,-5.449532*10**2]
    qwip=p[0]*avw**4+p[1]*avw**3+p[2]*avw**2+p[3]*avw+p[4]
    
    #Nomarlized Difference Index
    Rrs=extract_data(newfile, 'Reflectance')
    ndi=Rrs[44]/Rrs[97]  #Wavelengths in blue and red
    
    qwip_score=ndi-qwip
    return qwip_score


#use to creat a dataframe in which there is in each line the name of the file and the associated qwip score 
#the parameter must be a str    
def result(folder):
    
    path=os.listdir(folder)
    new_folder='modified_datas'
    if not os.path.exists(new_folder):
        os.mkdir(new_folder)
     
    #Calcul of the qwip score and creation of a list with the file's names
    qwip_score=[]
    filename=[]
    for file in path:
        rewrite_file(folder+'/'+file,new_folder+'/'+file)
        qwip_score.append(QWIP_score(new_folder+'/'+file))
        filename.append(file.replace('.txt',''))
    
    #prettify the time format
    time=[]    
    for date in filename:
        new_date=date.replace('_','')
        new_date=new_date[6:8]+'/'+new_date[8:10]+'/'+new_date[10:14]+'_'+new_date[0:2]+'h'+new_date[2:4]+'m'+new_date[4:6]+'s'
        time.append(new_date)
        
    #creation of the dataframe    
    df=pd.DataFrame({"Time": time, "QWIP-score": qwip_score})
    
    #remove the folder created
    shutil.rmtree('modified_datas') 
    
    return df








           
    

