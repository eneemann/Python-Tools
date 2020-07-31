
def csv_file_mover (cur_dir, dest_dir, csv_loc):
    import csv, shutil, os
    reader = csv.reader(open(csv_loc, "rb"))
    cur_checklist = os.listdir(cur_dir)
    notFound = 0
    #dest_dir = os.mkdir(cur_dir + '\name_check')
    for row in reader:
        if os.path.isfile(cur_dir + "\\" + str(row)[2:-2]):
            in_pdfpath = cur_dir
            in_pdf = in_pdfpath + '\\' + str(row)[2:-2]
            out_pdfpath = dest_dir
            out_pdf = out_pdfpath + '\\' + str(row)[2:-2]
            shutil.move (in_pdf, out_pdf)
        else:
            notFound += 1
            print('not found: '+ str(row)[2:-2])

    print(notFound)

csv_file_mover(input('current dir: '), input('destination dir: '), input('CSV location: '))
#csv_file_mover ('I:\AGR11\County PLSS Data\Tooele\Tooele_Ties\PLSS_Ready','I:\AGR11\County PLSS Data\Tooele\Tooele_Ties\PLSS_Ready\asdf',"C:\KW_Working\PLSS_App\Temp\WendoverCheck.csv")