import xlrd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import xlsxwriter

# input the file path to the excel spreadsheet here:
data_folder = Path(input("What is the file path?"))
loc = data_folder / input("What is the file name?")

wb = xlrd.open_workbook(loc)
sheet = wb.sheet_by_index(0)
sheet.cell_value(0, 0)

def largest(arr,n):
    # return max using max
    # inbuilt max() function
    return (max(arr))
    # This code is contributed by Jai Parkash Bhardwaj

def calc_cumrelintensity(num):

    name_of_cell = sheet.cell_value(0, ((num - 1) * 3) + 1)
    quiescent_or_dividing = sheet.cell_value(1, ((num - 1) * 3) + 1)
    day = sheet.cell_value(2, ((num - 1) * 3) + 1)

    actual_distance = []
    # creating an array for all of the distance values, and adding the values from the spreadsheet 
    # into the array
    for i in range(7, sheet.nrows):
        if sheet.cell_value(i, (num*3) - 2) != "":
            actual_distance.append(sheet.cell_value(i, (num * 3) - 2))



    raw_signal = []
    # doing the same as above, but for the raw signal values
    for i in range(7, sheet.nrows):
        if sheet.cell_value(i, (num*3) - 1) != "":
            raw_signal.append(sheet.cell_value(i, (num * 3) - 1))


    # normalizing distance
    distance_max = largest(actual_distance, len(actual_distance))
    normalized_distance = []
    for i in range (len(actual_distance)):
        normalized_distance.append((100 * actual_distance[i]) / distance_max)


    # calculating the average max
    sum = 0.0
    i=7
    count = 0
    while sheet.cell_value(i, (num*3)) != "":
        #print(i)
        sum = sum + float(sheet.cell_value(i, (num * 3)))
        count +=1
        i+=1

    ave_max = sum / count
    # background subtraction
    bg_subtraction = []
    for i in range (len(raw_signal)):
        bg_subtraction.append(raw_signal[i] - ave_max)

    # background subtraction, only positive values
    bg_subtraction_positive = []
    for i in range(len(bg_subtraction)):
        if bg_subtraction[i] > 0:
            bg_subtraction_positive.append(bg_subtraction[i])
        else:
            bg_subtraction_positive.append("0.0")



    # normalized bg subtraction, only positive values
    normalized_bg_positive = []
    max = largest(bg_subtraction, len(bg_subtraction))
    for i in range(len(bg_subtraction)):
        if ((bg_subtraction[i] / max) * 100) > 0:
            normalized_bg_positive.append(((bg_subtraction[i] / max) * 100))
        else:
            normalized_bg_positive.append(0.0)


    # within mito order
    within_mito_order = []
    if normalized_bg_positive[0] != 0:
        within_mito_order.append(1)
    else:
        within_mito_order.append(0)

    for i in range (1, len(normalized_bg_positive)):
        if normalized_bg_positive[i-1] == 0:
            if normalized_bg_positive[i] == 0:
                 within_mito_order.append(0)
            else:
                within_mito_order.append(1)

        elif normalized_bg_positive[i] != 0:
            within_mito_order.append(within_mito_order[i-1] + 1)
        else:
            within_mito_order.append(0)


    # adding rel intensity
    add_rel_intensity = []
    add_rel_intensity.append(normalized_bg_positive[0])
    for i in range(1, len(normalized_bg_positive)):
        if i == len(normalized_bg_positive):
            if(normalized_bg_positive[i] != 0 and within_mito_order[i] != 0):
                add_rel_intensity.append(normalized_bg_positive[i] + add_rel_intensity[i-1])
            else:
                add_rel_intensity_append(0.0)
        elif (normalized_bg_positive[i] != 0 and within_mito_order[i] != 0) or (within_mito_order[i] != 0 and within_mito_order[i+1] == 0):
            add_rel_intensity.append(normalized_bg_positive[i] + add_rel_intensity[i-1])
        else:
            add_rel_intensity.append(0.0)

    add_rel_intensity.append(0.0)
    # sum intensity in mito
    sum_mito_intensity = []
    sum_mito_intensity.append(0)

    for i in range(1, len(add_rel_intensity)):
        if add_rel_intensity[i-1] != 0 and add_rel_intensity[i]==0:
            sum_mito_intensity.append(add_rel_intensity[i-1])
        else:
            sum_mito_intensity.append(0)



    # relative intensity contribution
    rel_intensity_cont = []
    mitosum = 0
    for i in range(len(sum_mito_intensity)):
        mitosum = mitosum + sum_mito_intensity[i]

    for i in range(0, len(sum_mito_intensity) - 1):
            rel_intensity_cont.append(normalized_bg_positive[i] / mitosum)



    # cumulative relative intensity 

    cumulative_rel_intensity = []
    cumulative_rel_intensity.append(0.0)

    for i in range(1, len(rel_intensity_cont)):
        cumulative_rel_intensity.append(cumulative_rel_intensity[i-1] + rel_intensity_cont[i])

    return normalized_distance, cumulative_rel_intensity, name_of_cell, quiescent_or_dividing, day


def ten_percent_singlecell(norm_distance, cumul_intensity):
    ten_percents = []

    for i in range(1, 11):
        sum = 0
        count = 0
        for j in range (0, len(norm_distance)):
            if (10 * (i-1)) <= norm_distance[j] < (10 * i):
                sum = sum + cumul_intensity[j]
                count = count + 1
        ten_percents.append(sum / count)

    return ten_percents

def ten_percent_array(norm_distance, cumul_intensity):
    ten_percents = []

    for i in range(0, len(norm_distance)):
        x = ten_percent_singlecell(norm_distance[i], cumul_intensity[i])
        #print(x)
        ten_percents.append(x)

    return ten_percents




distances = []
intensities = []
cell_names = []
q_or_d = []
days = []
markercolor = ''
legendtitle = ''
title = ''
num_cells = int(input(("How many cells' data are in the spreadsheet?")))
graph_choice = int(input(("Print the number of the option you would like: \n 1: Plot each cell separately in a different color \n 2: Plot all quiescent cells in one color, dividing cells in another color \n 3: Plot all cells from the same cell date in one color \n 4: Plot average intensities per 10% distance for all cells of the same date \n 5: Plot average intensities per 10% distance for one cell over many dates \n 6: Quit" )))

while graph_choice != 6:

    for i in range(1, num_cells + 1):
        x, y, z, a, b = calc_cumrelintensity(i)
        distances.append(x)
        intensities.append(y)
        cell_names.append(z)
        q_or_d.append(a)
        days.append(b)

    ten_percents = ten_percent_array(distances, intensities)


    fig = go.Figure()
    if graph_choice == 1:
        title = 'Cumulative Relative Mitochondrial Intensities by Distance'
        for i in range (0, len(distances)):
            fig.add_trace(go.Scatter(
            x=distances[i], y=intensities[i],
            name=cell_names[i], mode='markers'
        ))

    if graph_choice == 2:
        for i in range (0, len(distances)):
            if q_or_d[i] == 'Quiescent':
                markercolor = 'rgba(0, 0, 255, .6)'

            else:
                markercolor = 'rgba(255, 0, 0, .6)'

            legendtitle = 'Blue: Quiescent \n Red: Dividing'
            #legendgroup = d_or_d[i]
            title = 'Cumulative Relative Mitochondrial Intensities for Quiescent vs Dividing Cells'
            fig.add_trace(go.Scatter(
            x=distances[i], y=intensities[i],
            name=cell_names[i], mode='markers', marker_color = markercolor, legendgroup = q_or_d[i]
        ))


    if graph_choice == 3:
        for i in range (0, len(distances)):
            if days[i] == 'Q 1':
                markercolor = 'rgba(255, 0, 0, .6)'
            elif days[i] == "Q 2":
                markercolor = 'rgba(255, 165, 0, .6)'
            elif days[i] == 'Q 3':
                markercolor = 'rgba(255, 255, 0, .6)'
            elif days[i] == 'Q 4':
                markercolor = 'rgba(0, 128, 0, .6)'
            elif days[i] == "D -2":
                markercolor = 'rgba(0, 0, 255, .6)'
            elif days[i] == 'D -1':
                markercolor = 'rgba(75, 0, 130, .6)'
            elif days[i] == 'D 0':
                markercolor = 'rgba(238, 130, 238, .6)'
            elif days[i] == "D 1":
                markercolor = 'rgba(101, 67, 33, .6)'
            elif days[i] == 'D 2':
                markercolor = 'rgba(0, 0, 0, .87)'
            elif days[i] == 'D 3':
                markercolor = 'rgba(128, 128, 128, .1)'

            legendtitle = 'Red: Q 1 \n Orange: Q 2 \n Yellow: Q 3 \n Green: Q 4 \n Blue: D -2 \n Purple: D -1 \n Pink: D 0 \n Brown: D 1 \n Black: D 2 \n Gray: D 3'
            title = 'Cumulative Relative Mitochondrial Intensities by Cell Date'
            fig.add_trace(go.Scatter(
            x=distances[i], y=intensities[i],
            name=cell_names[i], mode='markers', marker_color = markercolor, legendgroup = days[i]
        ))

    if graph_choice == 4:
        final_percents = []
        x_axis = []
        for i in range(5, 115, 10):
            x_axis.append(i)

        Q1 = []
        Q2 = []
        Q3 = []
        Q4 = []
        Dneg2 = []
        Dneg1 = []
        D0 = []
        D1 = []
        D2 = []
        D3 = []

        for i in range (0, len(distances)):
            if days[i] == "Q 1":
                Q1.append(ten_percents[i])
            elif days[i] == "Q 2":
                Q2.append(ten_percents[i])
            elif days[i] == "Q 3":
                Q3.append(ten_percents[i])
            elif days[i] == "Q 4":
                Q4.append(ten_percents[i])

            elif days[i] == "D -2":
                Dneg2.append(ten_percents[i])
            elif days[i] == "D -1":
                Dneg1.append(ten_percents[i])

            elif days[i] == "D 0":
                D0.append(ten_percents[i])
            elif days[i] == "D 1":
                D1.append(ten_percents[i])
            elif days[i] == "D 2":
                D2.append(ten_percents[i])
            elif days[i] == "D 3":
                D3.append(ten_percents[i])



        if len(Q1) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Q1)):
                sum = np.add(sum, Q1[i])
            for i in range(0, len(sum)):
                sum[i] = sum[i] / len(Q1)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(255, 0, 0, .6)', name = "Q 1"))

        if len(Q2) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Q2)):
                sum = np.add(sum, Q2[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(Q2)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(255, 165, 0, .6)', name = "Q 2"))

        if len(Q3) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Q3)):
                sum = np.add(sum, Q3[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(Q3)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(255, 255, 0, .6)', name = "Q 3"))

        if len(Q4) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Q4)):
                sum = np.add(sum, Q4[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(Q4)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(0, 128, 0, .6)', name = "Q 4"))

        if len(Dneg2) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Dneg2)):
                sum = np.add(sum, Dneg2[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(Dneg2)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(0, 0, 255, .6)', name = "D - 2"))

        if len(Dneg1) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(Dneg1)):
                sum = np.add(sum, Dneg1[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(Dneg1)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(75, 0, 130, .6)', name = "D -1"))

        if len(D0) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(D0)):
                sum = np.add(sum, D0[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(D0)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(238, 130, 238, .6)', name = "D 0"))

        if len(D1) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(D1)):
                sum = np.add(sum, D1[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(D1)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(101, 67, 33, .6)', name = "D 1"))

        if len(D2) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(D2)):
                sum = np.add(sum, D2[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(D2)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(0, 0, 0, .87)', name = "D 2"))

        if len(D3) != 0:
            sum = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for i in range (0, len(D3)):
                sum = np.add(sum, D3[i])
            for i in range(0, len(sum)):
                    sum[i] = sum[i] / len(D3)
            final_percents.append(sum)
            fig.add_trace(go.Scatter(
            x=x_axis, y=sum, mode='markers', marker_color = 'rgba(128, 128, 128, 1)', name = "D 3"))

        title = 'Cumulative Relative Mitochondrial Intensities Averaged Per 10% Distance'

        legendtitle = 'Red: Q 1 \n Orange: Q 2 \n Yellow: Q 3 \n Green: Q 4 \n Blue: D -2 \n Purple: D -1 \n Pink: D 0 \n Brown: D 1 \n Black: D 2 \n Gray: D 3'

    if graph_choice == 5:
        x_axis = []
        for i in range(5, 115, 10):
            x_axis.append(i)
        fig = go.Figure()
        cell_choice = int(input("Type the dataset cell ID number of the cell you would like to see."))
        sheet2 = wb.sheet_by_index(1)
        sheet2.cell_value(0, 0)
        for i in range(0, num_cells):
            if sheet2.cell_value(i, 0) == cell_choice:
                index = -1
                for j in range(0, len(cell_names)):
                    if cell_names[j] == sheet2.cell_value(i, 5):
                        index = j

                tenpercents = ten_percent_singlecell(distances[index], intensities[index])
                fig.add_trace(go.Scatter(
                x=x_axis, y=tenpercents,
                name=days[index], mode='markers', showlegend = True
                ))
        title = "Average Cumulative Intensities over Division for " + cell_names[index]


# for one cell - show the averages for Q1, Q2, Q3, etc
# showing all quiescent cells, and on top of it, the ten percent average line for all of them
# make a table showing all the ten percent values for all the cells with ID
# plot relative intensity q vs d, cell date

    fig.update_layout(xaxis_title = 'Normalized Distance', yaxis_title = 'Cumulative Relative Intensity', title=title, legend_title=legendtitle)


    fig.show()
    if str(input("Write graph to html file? type Y or N: ")).upper() == 'Y':
        fig.write_html(input('File path for export graph?'))

    if str(input("Create Excel file with all Normalized Distance and Cumulative Rel Intensity data? Type Y or N: ")).upper() == 'Y':
        workbook = xlsxwriter.Workbook(input("Type the filename for the new spreadsheet: "))
        worksheet = workbook.add_worksheet()
        worksheet.write(0, 0, 'File Name')
        worksheet.write(1, 0, 'Cell ID')
        worksheet.write(2, 0, 'Division Behavior')


        j = 1
        for i in range(0, len(cell_names)):
            worksheet.write(0, (j * 2) - 1, cell_names[i])
            worksheet.write(1, (j * 2) - 1, q_or_d[i])
            worksheet.write(2, (j * 2) - 1, days[i])
            worksheet.write(6, (j * 2) - 1, 'Normalized Distance')
            worksheet.write(6, (j * 2), 'Cumulative Relative Intensity')

            for k in range(0, len(distances[i])):
                worksheet.write(k+7, (j * 2) - 1, distances[i][k])
                worksheet.write(k+7, (j * 2), intensities[i][k])

            j += 1


        workbook.close()
    graph_choice = int(input(("Print the number of the option you would like: \n 1: Plot each cell separately in a different color \n 2: Plot all quiescent cells in one color, dividing cells in another color \n 3: Plot all cells from the same cell date in one color \n 4: Plot average intensities per 10% distance for all cells of the same date \n 5: Plot average intensities per 10% distance for one cell over many dates \n 6: Quit" )))
