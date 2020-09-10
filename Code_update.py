import os
from flask import Flask, render_template, request, redirect, url_for,jsonify
from werkzeug.utils import secure_filename
import pandas as pd
import pyreadstat
import numpy as np
import requests
import xlsxwriter



def Check(uploaded_file1,filename,Brand_fromUser,Other,NoneVal,Dont,Prefer,MergeStr,Second_Brand_fromUser):
    fn = os.path.join(uploaded_file1, filename)
    Updated_path = fn.replace('\\', '/')  # replacing \ from file location to / for making it readable for system
    result = list(Updated_path.rpartition('/'))
    VarLAb_InpFile = result[0] + '/' + 'Variable_Label_Input.xlsx'
    ValLAb_InpFile = result[0] + '/' + 'Value_Label_Input.xlsx'
    ValLAb_OutFile = result[0] + '/' + 'Value Labels_Output.xlsx'
    VarLAb_OutFile = result[0] + '/' + 'Var and Rename_Output.xlsx'
    ValLAb_SPSSFile = result[0] + '/' + '3. Recode.sps'
    VarLAb_VarSPSS = result[0] + '/' + '1. VariableLabels.sps'
    VarLAb_RenSPSS = result[0] + '/' + '2. RenameVariable.sps'
    ValueLabels_RenSPSS=result[0]+"/"+"4. ValueLabels.sps"
    Merge_variable=result[0]+"/"+"Merge Variable.sps"

    (df, meta) = pyreadstat.read_sav(Updated_path)
    meta_data = meta.column_names_to_labels
    df1 = pd.DataFrame(list(meta_data.items()), columns=['Variables','Labels'])  # value of variable and available label from SPSS
    col = meta.column_names
    Value_label = meta.variable_value_labels  # Fpr creating value labels getting value as dict

    x = list(Value_label.keys())


    lstcode=[]
    lstval=[]

    length=[]

    for i in range(len(x)):
        lstcode.append(list(Value_label[x[i]].keys()))
        lstval.append(list(Value_label[x[i]].values()))
        length.append(len(list(Value_label[x[i]].values())))
        
        
    #Var_code = [item for sublist in lstcode for item in sublist]
    #flat_list1 = [item for sublist in lstval for item in sublist]    

        
        
    variable=[]
    for k in range(0,len(Value_label)):
        #import pdb;pdb.set_trace()
        variable.append(x[k])
        blankv=length[k]
        for i in range(blankv-1):
                variable.append("")
            
                
    from pandas import DataFrame     #converting created list to dataframes for value label input file
    col = DataFrame (variable,columns=['variable'])
    Var_code= DataFrame ([item for sublist in lstcode for item in sublist],columns=['code'])       
    Option_Label= DataFrame ([item for sublist in lstval for item in sublist],columns=['Option Label'])       
        
    with pd.ExcelWriter(ValLAb_InpFile) as writer:  #writing dataframes to excel value label input file
        col.to_excel(writer, sheet_name="Raw",index=False,startcol=0)          
        Var_code.to_excel(writer, sheet_name="Raw",index=False,startcol=1)            
        Option_Label.to_excel(writer, sheet_name="Raw",index=False,startcol=2)        
        
        
                
        
    from pandas import DataFrame #converting created list to dataframes for variable label input file

    Brand_List = Brand_fromUser
    Brand_List_second = Second_Brand_fromUser
    Brand_List_second_main=Brand_List_second.split(",")
    Brand_List_main=Brand_List.split(",")
    Inp_Brands = DataFrame (Brand_List_main,columns=['brand'])
    Inp_Brands1 = DataFrame (Brand_List_second_main,columns=['brandSecond'])






    with pd.ExcelWriter(VarLAb_InpFile) as writer:   #writing dataframes to excel variable label input file
        df1.to_excel(writer, sheet_name='Raw',index=False)
        Inp_Brands.to_excel(writer, sheet_name='brand',index=False)
        Inp_Brands1.to_excel(writer, sheet_name='brandSecond',index=False)    
        



    otherr = Other
    Nonee = NoneVal
    Dont = Dont
    Prefer = Prefer


    # Creating Value label output excel file and Spss Syntax file #   


    xlsx_file = pd.ExcelFile(ValLAb_InpFile)
    a = pd.read_excel(xlsx_file, "Raw")

    values_list = a.values.tolist()

    values_list_1 = []

    last_value = np.nan
    for i in range(0,len(values_list)):
        if values_list[i][0] is not np.nan:
            last_value= values_list[i][0]

        if "other (please specify)" in values_list[i][2].strip().lower():
            w = values_list[i][2].replace("Other (Please specify)","Other")
        else:
            w = values_list[i][2]
        values_list_1.append([last_value,values_list[i][1],w])


    not_at_all=50001
    not_very=50002
    Somewhat=50003
    Very=50004
    Extremely=50005

    values_list_2 = []
    for i in values_list_1:
        if "other" == i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],otherr])
            #values_list_2.append([i[0],i[1],i[2],"96"])
            continue
        if "none of these" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Nonee])
            #values_list_2.append([i[0],i[1],i[2],"97"])
            continue
        if "don’t know" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Dont])
            continue
        if "prefer not to answer" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Prefer])
            continue
        if "not at all familiar" in i[-1].lower() or "not at all favorable" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],not_at_all])
            continue
        if "not very familiar" in i[-1].lower() or "not very favorable" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],not_very])
            continue
        
        if "somewhat familiar" in i[-1].lower() or "somewhat favorable" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Somewhat])
            continue
        
        if "very familiar" in i[-1].lower() or "very favorable" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Very])
            continue
        
        if "extremely familiar" in i[-1].lower() or "extremely favorable" in i[-1].lower():
            values_list_2.append([i[0],i[1],i[2],Extremely])
            continue
        
        values_list_2.append([i[0],i[1],i[2],i[1]])




    values_list_3 = []
    for i in values_list_2:
        if i[-1] != "" and i[-1] in [otherr,Nonee,Dont,Prefer]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),i[3])
            
        elif i[-1] != "" and i[-1] in [not_at_all]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),1)
            
        elif i[-1] != "" and i[-1] in [not_very]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),2)
            
        elif i[-1] != "" and i[-1] in [Somewhat]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),3)
            
        elif i[-1] != "" and i[-1] in [Very]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),4)
            
        elif i[-1] != "" and i[-1] in [Extremely]:
            syntex = "recode %s(%s=%s). "%(i[0],int(i[1]),5)
            
        else:
            syntex = ""
        values_list_3.append([i[0],i[1],i[2],i[3],syntex])




    d ={}
    for i in values_list_3:
        if i[0] in d:
            if i[-1]!="" or i[1]<0:
                d[i[0]]=True

        else:
            d[i[0]]=False


    temp_dict = {}

    values_list_4 = []
    for i in values_list_3:
        if i[1] <0:
            # values_list_4.append([i[0],i[1],i[2],i[3],i[4],""])
            continue
        if i[0] in temp_dict:
            syntex = """%s "%s" """ %(int(i[3]),i[2])
        else:
            temp_dict[i[0]]=True
            syntex = """value labels %s %s "%s" """ %(i[0],int(i[3]),i[2])
        if d[i[0]] is True:
            values_list_4.append([i[0],i[1],i[2],i[3],i[4],syntex])
        else:
            values_list_4.append([i[0],i[1],i[2],i[3],i[4],""])

    ForBrand_loop=[]
    for i in range(len(values_list_4)):
        if values_list_4[i][5].startswith("5000"):
            ForBrand_loop.append(values_list_4[i][0].split("_")[0])
        values_list_4[i][5]=values_list_4[i][5].replace("5000",'')
        

    not_formatted = []
    ids_list = []
    for i in values_list_4:
        if "[%" in i[2]:
            ids_list.append(i[0])
    ids_list_df = pd.DataFrame(ids_list)


    next_sheet_data = []
    for i in values_list_4:
        next_sheet_data.append(i[4])
    next_sheet_data = list(filter(None,next_sheet_data))

    cleared_final_excel = pd.DataFrame(values_list_4)
    next_sheet_data_excel = pd.DataFrame(next_sheet_data)
    # cleared_final_excel.to_excel("values_output.xls")



    def dfs_tabs(df_list, sheet_list, file_name):
        writer = pd.ExcelWriter(file_name,engine='xlsxwriter')   
        for dataframe, sheet in zip(df_list, sheet_list):
            dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0)   
        writer.save()


    dfs = [cleared_final_excel, next_sheet_data_excel,ids_list_df]
    sheets  =["Value Labels(G)", "Recoding Syntax","Need Manual Updation"]
    dfs_tabs(dfs, sheets, ValLAb_OutFile)


    xlsx_file1=pd.ExcelFile(ValLAb_OutFile)
    a = pd.read_excel(xlsx_file1,"Recoding Syntax")
    b = pd.read_excel(xlsx_file1,"Value Labels(G)")

    cleanedList = [x for x in b[5].tolist() if x == x]


        

    vala = b[5].values.tolist()
    new_list1 = [vala[x] for x in range(len(vala)) if vala[x] is not np.nan]
    for j in range(len(new_list1)):
        current_ele=new_list1[j]
        if len(new_list1)-j > 2:
            if "value labels" in new_list1[j+1]:
                new_list1[j]=current_ele + ". \n EXECUTE."
    with open(ValLAb_SPSSFile,'w') as f:
        for text in a[0].tolist():
            f.write(text + '\n')
    with open(ValueLabels_RenSPSS,'w') as f:
        for text in new_list1:
            if text is not np.nan:
                f.write(text + '\n')
        else:
            f.write('.\n EXECUTE.')
        
            
        
            
            
            
    

    # Creating variable label and rename variable output excel file and Spss Syntax file    
        
    xlsx_file = pd.ExcelFile(VarLAb_InpFile)
    a = pd.read_excel(xlsx_file, "Raw") # Read 'raw' sheet from input file
    brand = pd.read_excel(xlsx_file, "brand")['brand'].to_list()
    brand1 = pd.read_excel(xlsx_file, "brandSecond")['brandSecond'].to_list()

    data_list = a.values.tolist()

    underscore_with_dot = []
    underscore_without_dot = []
    without_underscore_with_dot_data = []
    without_underscore_without_dot_data = []

    for l in data_list:
        if "_"  in l[0] and "." in l[0]:
            underscore_with_dot.append(l)
        elif "_" in l[0] and not "." in l[0]:
            underscore_without_dot.append(l)
        elif not "_" in l[0] and "." in l[0]:
            without_underscore_with_dot_data.append(l)
        else:
            without_underscore_without_dot_data.append(l)

    # underscore_with_dot
    final_underscore_with_dot = []
    for i in underscore_with_dot:
        #if len(i[1]) > 30:
            # final_underscore_with_dot.append([i[0],i[0].split("_")[0] + " -" + i[1].split("]")[-1] + " ::" + i[1].split("-")[1].split("[")[0]])
            #print(i)
            mystring = i[0].split("_")[0] + " -" + i[1].split("]")[-1] + " ::" + i[1].split("-")[1].split("[")[0]
            if "other" in i[0].lower():
                mystring = mystring.split("::")
                mystring = mystring[0].strip() + " :: TEXT :: " + mystring[1]

            final_underscore_with_dot.append([i[0],mystring])



    # underscore_without_dot
    final_underscore_without_dot = []
    for i in underscore_without_dot:
        if len(i[1]) > 30:
            #print(i)
            # final_underscore_without_dot.append([i[0],i[0].split("_")[0] + " -" + i[1].split("]")[-1] + " ::" + i[1].split("-")[1].split("[")[0]])
            mystring = i[0].split("_")[0] + " -" + i[1].split("]")[-1] + " ::" + i[1].split("-")[1].split("[")[0]

            if "other" in i[0].lower():
                mystring = mystring.split("::")
                mystring = mystring[0].strip() + " :: TEXT :: " + mystring[1]

            final_underscore_without_dot.append([i[0],mystring])




    # without_underscore_with_dot_data
    final_without_underscore_with_dot_data = []
    for i in without_underscore_with_dot_data:
        final_without_underscore_with_dot_data.append([i[0],str(i[1]).split("[")[0]])

    # without_underscore_without_dot_data

    final_without_underscore_without_dot_data = []
    for i in without_underscore_without_dot_data:
        final_without_underscore_without_dot_data.append([i[0],str(i[1]).split("[")[0]])


    final_excel =  final_underscore_with_dot + final_underscore_without_dot + final_without_underscore_with_dot_data + final_without_underscore_without_dot_data

    cleared_final_excel = []



    #removing ? and . and adding rename variables on col D
    for i in final_excel: #Iterating over final_excel created
        d = i[1].strip()
        if "?" == d[-1] or "." == d[-1]:
            d = d[:-1]
        if "(Please specify)" in d:
            d = d.replace("(Please specify)","")

        # removing double spaces
        d = filter(None, d.split(" "))
        d = " ".join(d)



        #adding none of these and none
        if "other" in i[0]:
            cleared_final_excel.append([i[0], d, i[0].split("_")[0] + "_" + otherr + "_OTHER" ])
        elif "None of these ::" in d or "None ::" in d:
            s = i[0].split("_")[0]+"_"+ Nonee
            if "." in i[0]:
                s1 = i[0].split(".")[-1]
                cleared_final_excel.append([i[0], d, s + "." + s1 ])
            else:
                cleared_final_excel.append([i[0], d, s ])

        elif "Don’t know / don’t remember ::" in d or "Don’t know ::" in d:
            s = i[0].split("_")[0]+"_"+ Dont
            if "." in i[0]:
                s1 = i[0].split(".")[-1]
                cleared_final_excel.append([i[0], d, s + "." + s1 ])
            else:
                cleared_final_excel.append([i[0], d, s ])

        elif "Prefer not to answer ::" in d:
            s = i[0].split("_")[0]+"_"+"99"
            if "." in i[0]:
                s1 = i[0].split(".")[-1]
                cleared_final_excel.append([i[0], d, s + "." + s1 ])
            else:
                cleared_final_excel.append([i[0], d, s ])

        elif "Other ::" in d:
            s = i[0].split("_")[0]+"_"+ otherr
            if "." in i[0]:
                s1 = i[0].split(".")[-1]
                cleared_final_excel.append([i[0], d, s + "." + s1 ])
            else:
                cleared_final_excel.append([i[0], d, s ])
        else:
            cleared_final_excel.append([i[0], d, i[0]])



    brand_dict = {}
    for index, i in enumerate(brand,1): #iterating over list brand
        brand_dict[index] = i  #passing value to key

    brand_dict1 = {}
    for index, i in enumerate(brand1,1): #iterating over list brand
        brand_dict1[index] = i        

    #Brand_set=set(ForBrand_loop)
    '''cleared_final_excel_inter = []  #nt us
    for i in cleared_final_excel:
        Question_name = BrandQ
        if Question_name  == i[0][:2] and "_r" in i[0]:
            index_value = int(i[0].split("_r")[-1])
            if index_value > len(brand_dict):
                cleared_final_excel_inter.append([i[0],i[1],i[2]])
            else:
                new_string = i[1].split("[%")[0] + " " + brand_dict[index_value] + " :: " + i[1].split("::")[1]
                cleared_final_excel_inter.append([i[0],new_string,i[2]])
                continue
        else:
            cleared_final_excel_inter.append([i[0],i[1],i[2]])'''

    cleared_final_excel_inter = []
    for i in cleared_final_excel:
        cleared_final_excel_inter.append([i[0],i[1],i[2]])




    cleared_final_excel_0 = []
    for i in cleared_final_excel_inter:
        if "_r" in i[0] or "_c" in i[0]:
            cleared_final_excel_0.append([i[0],i[1],i[0].replace("r","").replace("c","")])    
        else:
            cleared_final_excel_0.append(i)

    
    #adding brand ### yhn update forsecond brand 
    cleared_final_excel_inter_1 = []
    first_loop=[] #updated 7/9
    Second_loop=[] #updated 7/9
    for i in cleared_final_excel_0:
        if "." in i[0]: 
            inx = int(i[0].split(".")[-1])
            #first_loop.append(i[0]) or inx - int(var.split(".")[-1]) < 2
            
            if len(first_loop) > 0:
                var = str(first_loop[-1])
                abc= int(var.split(".")[-1])
                #print(type(abc))
            if len(first_loop) < 1 or inx - abc == 1 or inx - abc == 0 : #updated 7/9
                first_loop.append(i[0])
                if inx <= len(brand_dict):
                    cleared_final_excel_inter_1.append([i[0],i[1] + " " + brand_dict[inx],i[2]])
                continue
                 #updated 7/9
            else: #updated 7/9
                Second_loop.append(i)  #updated 7/9    
                if inx <= len(brand_dict):
                    cleared_final_excel_inter_1.append([i[0],i[1] + " " + brand_dict1[inx],i[2]])
                continue
        #print("first loop",first_loop)
        #print("second loop",Second_loop)
        cleared_final_excel_inter_1.append([i[0],i[1],i[2]])



    # J1 - Screen 1 :: When thinking about choosing a provider for video security solutions :: Which is MOST IMPORTANT
    # J1 -) MOST IMPORTANT :: When thinking about choosing a provider for video security solutions… Which is MOST IMPORTANT? Which is LEAST IMPORTANT? (Please select one for each column) (

    # J1 - Screen 1 :: When thinking about choosing a provider for video security solutions :: Which is LEAST IMPORTANT
    # J1 -) LEAST IMPORTANT :: When thinking about choosing a provider for video security solutions… Which is MOST IMPORTANT? Which is LEAST IMPORTANT? (Please select one for each column) (
    cleared_final_excel_inter_2 = []
    for i in cleared_final_excel_inter_1:
        if "_b" in i[0]:
            screen_string = " - Screen " + str(i[0].split("_")[1]) + " "
            new_string = i[1].replace("-) MOST IMPORTANT ",screen_string).split("…")[0] + ":: Which is MOST IMPORTANT"
        elif "_w" in i[0]:
            screen_string = " - Screen " + str(i[0].split("_")[1]) + " "
            new_string = i[1].replace("-) LEAST IMPORTANT ",screen_string).split("…")[0] + " :: Which is LEAST IMPORTANT"
        else:
            new_string=i[1]
        cleared_final_excel_inter_2.append([i[0],new_string,i[2]])



    # converting
    cleared_final_excel_1 = []
    for i in cleared_final_excel_inter_2:   
        cleared_final_excel_1.append([i[0],i[1],i[2],"""Variable Labels %s"%s"."""%(i[0],i[1])])


    cleared_final_excel_2 = []
    for i in cleared_final_excel_1:
        cleared_final_excel_2.append([i[0],i[1],i[2],i[3],"""Rename Variables (%s=%s)."""%(i[0],i[2])])


    # fetching the ids with %[
    cleared_final_excel_3 = []
    ids_list = []
    checking_list = []
    for i in cleared_final_excel_2:
        if i[0] in checking_list:
            continue
        if "[%" in i[1]:
            ids_list.append([i[0],i[3],"Perl char available after filtering "])
        if len(i[3]) > 250:
            ids_list.append([i[0],i[3],"Length Greater then 250 char (truncated text)"])
        checking_list.append(i[0])




    def dfs_tabs(df_list, sheet_list, file_name):
        writer = pd.ExcelWriter(file_name,engine='xlsxwriter')   
        for dataframe, sheet in zip(df_list, sheet_list):
            dataframe.to_excel(writer, sheet_name=sheet, startrow=0 , startcol=0 , index=False)   
        writer.save()


    cleared_final_excel = pd.DataFrame(cleared_final_excel_2)
    ids_list_df = pd.DataFrame(ids_list)
    # cleared_final_excel.to_excel("file.xls")


    dfs = [cleared_final_excel, ids_list_df]
    sheets  =["Updated by code", "Need Manual Updation"]
    dfs_tabs(dfs, sheets, VarLAb_OutFile)    
        


    xlsx_file1=pd.ExcelFile(VarLAb_OutFile)
    a = pd.read_excel(xlsx_file1,"Updated by code")

    with open(VarLAb_VarSPSS,'w') as f:
        for text in a[3].tolist():
            f.write(text + '\n')

    with open(VarLAb_RenSPSS,'w') as f:
        for text in a[4].tolist():
            f.write(text + '\n')   

    if MergeStr != "":
        if ',' in MergeStr:
            MergeStr1=MergeStr.split(",")
            syn=[]
            for i in range(len(MergeStr1)):
                (a, b) = MergeStr1[i].split('-')
                syntax = "If(missing(" + a + "))" + a + "=" + b + ".\nExecute. \n"
                syn.append(syntax)  

        else:
            syn=[]
            (a, b) = MergeStr.split('-')
            syntax = "If(missing(" + a + "))" + a + "=" + b + ".\nExecute. \n"
            syn.append(syntax)

        with open(Merge_variable, 'w') as f:
            for item in syn:
                f.write("%s\n" % item)  

    xlsx_file1=pd.ExcelFile(VarLAb_OutFile)
    Eror = pd.read_excel(xlsx_file1,"Need Manual Updation")
    label = pd.read_excel(xlsx_file1,"Updated by code")


    
    

        
    return Eror,label