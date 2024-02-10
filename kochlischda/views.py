from django.shortcuts import render, HttpResponse
from . import settings
from .services import calculate_month, additional_holidays, additional_waiverdays, get_list_of_kids, check_correctness, optimise
import os
from .forms import WaiverdaysForm, DataframeChoice
import pandas as pd
from kochlischda.globals import Setup
from .models import Dish
import os
from django.conf import settings
from django.http import FileResponse
import tempfile


def home(request):
    return render(request, 'home.html')

def base(request):
    return render(request, 'base.html')

def home(request):
    return render(request, 'StaticPages/main.html')


def add_holidays(request):
    """
    #TODO: take admin input
    """
    state = additional_holidays('1-6')
    return HttpResponse(state)

def setup_month(request):
    """
    #TODO: take user input
    """
    if request.method == 'POST':
        form = WaiverdaysForm(request.POST)
        if form.is_valid():
            dates = form.cleaned_data['dates']
            kid = form.cleaned_data['kid']
            dishes_this_month = form.cleaned_data['dishes_this_month']
            dish = form.cleaned_data['dish']
            wishdays = form.cleaned_data['wishdays']
            month = form.cleaned_data['month']
            year = form.cleaned_data['year']
            state = additional_waiverdays(days=dates, wishdays=wishdays, kid=list(kid)[0], dishes_this_month=dishes_this_month, month=month, year=year, dish=dish)
            return HttpResponse(state)
        else:
            print(form.errors.as_data()) # here you print errors to terminal
    

    form = WaiverdaysForm()
    return render(request, 'waiverday_form.html', {'form': form})
    #wishdays = 0
    #kids_list = get_list_of_kids()
    #this_kid = kids_list[3]
    #state = additional_notdays('15-31', wishdays=wishdays, kid=this_kid)
    #return HttpResponse(state)

def brewing_the_kochliste(request):
    if request.method == "POST":
        form = DataframeChoice(request.POST)
        if form.is_valid(): 
            onetwothree = form.cleaned_data['df_number']
        if onetwothree == '1':
            df = Setup.df1
        elif onetwothree == '2':
            df = Setup.df2
        else:
            df = Setup.df3
        
        df['dish'] = ''
        df.rename(columns={df.keys()[0]: "kid"}, inplace=True)
        for i, row in df.iterrows():
            if row.kid != '':
                if row.name.day_of_week == 1:
                    df.at[i, 'dish'] = 'Essen to go (Ausflugsessen)'
                else:
                    res = [x for x in Dish.objects.all() if x.cook.name == row.kid]
                    if not len(res):
                        df.at[i, 'dish'] = ''
                    else:   
                        df.at[i, 'dish'] = str(res[0])

                    
        
        ####### fill nan values of weekend days and holidays
        df['dish'].fillna('')
        
        df.reset_index(inplace=True)
        
        path_to_csv = f'/home/daberer/Documents/Kochliste/{Setup.year}_{Setup.month}_kochliste.csv'
        df.to_csv(path_to_csv, sep=",", index=False, header=None)
        # temp_path = tempfile.mkdtemp()

        # path_to_excel = os.path.join(temp_path, f'{Setup.year}_{Setup.month}_kochliste.xlsx')
        # # Create a Pandas Excel writer using XlsxWriter as the engine.
        # writer = pd.ExcelWriter(path_to_excel, engine='xlsxwriter')

        # # Write the dataframe data to XlsxWriter. Turn off the default header and
        # # index and skip one row to allow us to insert a user defined header.
        # df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False, index=False)

        

        # # Get the xlsxwriter workbook and worksheet objects.
        # workbook = writer.book
        # worksheet = writer.sheets['Sheet1']


        # # Get the dimensions of the dataframe.
        # (max_row, max_col) = df.shape
        
        # # Create a list of column headers, to use in add_table().
        # column_settings = [{'header': column} for column in df.columns]

        # # Add the Excel table structure. Pandas will add the data.
        # worksheet.add_table(0, 0, max_row, max_col - 1, {'columns': column_settings})

        # text_format = workbook.add_format({'text_wrap' : True})

        # # Make the columns wider for clarity.
        # worksheet.set_column(0, 0, 20)
        # worksheet.set_column(1, 1, 20)
        # worksheet.set_column(1, 2, 60, text_format)


        # # Close the Pandas Excel writer and output the Excel file.
        # writer.close()

        return FileResponse(open(path_to_csv, 'rb'))
    


    scoreboard = {}
    for i in range(Setup.trial_number):
        res = calculate_month(i)
        #ro = check_correctness(res)
        if res:
            scoreboard[i] = [res[0], res[1], res[2]]
            
    sorted_scoreboard = sorted(scoreboard.items(), key=lambda x: x[0])

    df1 = pd.DataFrame(sorted_scoreboard[0][1][2], index=['Kids (variant 1)']).transpose()
    
    df1.index = pd.to_datetime(df1.index)
    if Setup.optimise:
        df1 = optimise(df1)
    df1.fillna('', inplace=True)
    #df1 = ({df1.index: 32, df1.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[0][1][1].items()])})
    df2 = pd.DataFrame(sorted_scoreboard[1][1][2], index=['Kids (variant 2)']).transpose()
    df2.index = pd.to_datetime(df2.index)
    if Setup.optimise:
        df2 = optimise(df2)
    df2.fillna('', inplace=True)
    #df2 = df2.append({df2.index: 32, df2.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[1][1][1].items()])})
    df3 = pd.DataFrame(sorted_scoreboard[2][1][2], index=['Kids (variant 3)']).transpose()
    df3.index = pd.to_datetime(df3.index)
    if Setup.optimise:
        df3 = optimise(df3)
    df3.fillna('', inplace=True)
    #df3 = df3.append({df3.index: 32, df3.keys()[0]: str([str(a[0])+ ' ' + str(a[1]) for a in sorted_scoreboard[2][1][1].items()])})
    print(f'Lucky kids: \n {sorted_scoreboard[0][1][1]} \n {sorted_scoreboard[1][1][1]} \n {sorted_scoreboard[2][1][1]}')
    Setup.df1 = df1
    Setup.df2 = df2
    Setup.df3 = df3

    form = DataframeChoice()
    #return HttpResponse(df.to_html())
    return render(request, 'result_form.html', {'resulttable1': df1.to_html(classes="dataframe dfirst"), 'resulttable2': df2.to_html(classes="dataframe dsecond"), 'resulttable3': df3.to_html(classes="dataframe dthird"), 'form': form})