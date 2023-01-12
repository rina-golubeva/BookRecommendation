import pandas as pd
from tkinter import *
from tkinter import messagebox
from tkinter import scrolledtext
import json
from math import sqrt
import random
import os
import os.path


'''work with start data'''


dfy = pd.read_excel('Amazon_top100_bestselling_books_2009to2021.xlsx',
                    dtype={"no_of_reviews": str})
dfy.drop(columns=['Unnamed: 0'], inplace=True)
dfy['no_of_reviews'] = dfy['no_of_reviews'].str.replace(',', '').astype(float)
dfy['no_of_reviews'] = pd.to_numeric(dfy['no_of_reviews'])
dfy['no_of_reviews'] = dfy['no_of_reviews'].fillna(dfy['no_of_reviews'].median())
dfy['price'] = dfy['price'].fillna(dfy['price'].mean())
dfy['ratings'] = dfy['ratings'].fillna(dfy['ratings'].mode())
dfy.dropna(inplace=True)
dfy.no_of_reviews = dfy.no_of_reviews.astype(int)
dfy.price = dfy.price.astype(float)
dfy.ranks = dfy.ranks.astype(int)
dfy.drop(dfy.loc[dfy['genre'] == 'unknown'].index, inplace=True)
names = dfy['title']
names.drop_duplicates()
names = names.to_list()
names = list(map(str, names))
names = sorted(list(set(names)))


'''work with rating data'''


'''If user created new rating file, we need to use it'''


if os.path.isfile('ratings1.json'):
    with open('ratings1.json', 'r', encoding='utf-8') as f:
        d = json.load(f)
else:
    with open('ratings.json', 'r', encoding='utf-8') as f:
        d = json.load(f)

d = pd.DataFrame(d)
books = d.to_dict()
d_trans = d.T
critics = d_trans.to_dict()


'''all functions for recommendation system'''


def sim_distance(prefs, person1, person2):
    """Return a distance-based similarity score for person1 and person2."""
    # get the list of shared items
    si = {}
    for item in prefs[person1]:
        if item in prefs[person2]:
            si[item] = 1

    # if no ratings in common, return 0
    if len(si) == 0:
        return 0

    # add up the squares of all the differences
    sum_of_squares = sum([pow(prefs[person1][item] - prefs[person2][item], 2)
                          for item in prefs[person1] if item in prefs[person2]])
    return 1 / (1 + sum_of_squares)
    # between (0, 1)


def sim_pearson(prefs, p1, p2):
    """Return the Pearson correlation coefficient for person1 and person2."""
    # get the list of shared items
    si = {}
    for item in prefs[p1]:
        if item in prefs[p2]:
            si[item] = 1

    # find the number of elements
    n = len(si)

    # if no ratings in common, return 0
    if len(si) == 0:
        return 0

    # add up all the preferences
    sum1 = sum([prefs[p1][item] for item in si])
    sum2 = sum([prefs[p2][item] for item in si])

    # sum up the squares
    sum1Sq = sum([pow(prefs[p1][item], 2) for item in si])
    sum2Sq = sum([pow(prefs[p2][item], 2) for item in si])

    # sum up the products
    pSum = sum([prefs[p1][item] * prefs[p2][item] for item in si])

    # calculate Pearson score
    num = pSum - (sum1 * sum2) / n
    den = sqrt((sum1Sq - pow(sum1, 2) / n) * (sum2Sq - pow(sum2, 2) / n))
    if den == 0:
        return 0
    else:
        return num / den
        # between(-1, 1)


def topMatches(prefs, person, n=5, similarity=sim_pearson):
    """Return the best matches for person from the prefs dictionary."""
    scores = [(round(similarity(prefs, person, other), 5), other)
              for other in prefs if other != person]
    # sort the list so the highest scores appear at the top
    scores.sort(reverse=True)
    return scores[0:n]


def getRecommendations(prefs, person, n=5, similarity=sim_pearson):
    """Get recommendations for a person by using a weighed averaged ranking."""
    totals = {}
    simSums = {}
    for other in prefs:
        # don't compare me to myself (skip to the next iteration)
        if other == person:
            continue

        sim = similarity(prefs, person, other)

        # ignore scores of zero or lower
        if sim <= 0:
            continue

        for item in prefs[other]:
            # only score movies I haven't seen yet
            if item not in prefs[person] or prefs[person][item] == 0:
                # similarity * score
                totals.setdefault(item, 0)
                totals[item] += prefs[other][item] * sim
                # sum of similarities
                simSums.setdefault(item, 0)
                simSums[item] += sim

    # create the normalized list
    rankings = [(round(total / simSums[item], 5), item) for item, total in totals.items()]

    # return the sorted list
    rankings.sort(reverse=True)
    return rankings[:n]


def transformPrefs(prefs: dict):
    """Swipe the people and the item."""
    results = {}
    for person in prefs:
        for item in prefs[person]:
            results.setdefault(item, {})
            # flip item and person
            results[item][person] = prefs[person][item]
    return results


def calculateSimilarItems(prefs, k=5):
    """Return a dictionary of items showing which other items they are most similar to."""
    result = {}
    # invert the preference matrix to be item-centric
    itemPrefs = transformPrefs(prefs)
    c = 0
    for item in itemPrefs:
        # status updates for large datasets
        c += 1
        if c % 100 == 0:
            print("%d/%d" % (c, len(itemPrefs)))
        # find the most similar items to this one
        scores = topMatches(itemPrefs, item, n=k, similarity=sim_distance)
        result[item] = scores
    return result


with open('itemsim.json', 'r', encoding='utf-8') as f:
    '''work with previous function and generated data with books matches'''
    itemsim = json.load(f)

with open('itemsim2.json', 'r', encoding='utf-8') as f2:
    '''work with previous function and generated data with critics matches'''
    itemsim2 = json.load(f2)


def getRecommendedItems(prefs, itemMatch, user, n):
    """Get recommendations using the item-based filtering."""
    userRatings = prefs[user]
    scores = {}
    totalSim = {}

    # loop over items rated by this user
    for (item, rating) in userRatings.items():
        # loop over items similar to this one
        for (similarity, item2) in itemMatch[str(item)]:
            # ignore if user has already reated this item
            if item2 in userRatings and rating == 0:
                continue

            # weighted sum of rating times similarity
            scores.setdefault(item2, 0)
            scores[item2] += similarity * rating

            # sum of all the similarities
            totalSim.setdefault(item2, 0)
            totalSim[item2] += similarity

    # divide each total score by total weighting to get an average
    rankings = [(round(score / totalSim[item], 5), item)
                for item, score in scores.items()]

    # return the rankings from highest to lowest
    rankings.sort(reverse=True)
    return rankings[:n]


'''generating new matches file if the user create his own rating file'''


if os.path.exists('ratings1.json'):
    itemsim = calculateSimilarItems(critics, 10)
    itemsim2 = calculateSimilarItems(books, 10)


'''functions for interface'''


'''function to display the result of the work sim_distance'''


def click_1():
    var1, var2 = entry_1.get().split(',')
    if var1.isdigit() and var2.isdigit():
        answer_1.config(text=f"for user{var1} and user{var2}: " +
                             str(round(sim_distance(critics, int(var1), int(var2)), 5)))
    else:
        messagebox.showerror("Error!", "Please check entered data.")


'''function to display the result of the work sim_pearson'''


def click_2():
    var1, var2 = entry_2.get().split(',')
    if var1.isdigit() and var2.isdigit():
        answer_2.config(text=f"for user{var1} and user{var2}: " +
                             str(round(sim_pearson(critics, int(var1), int(var2)), 5)))
    else:
        messagebox.showerror("Error!", "Please check entered data.")


'''function to display the result of the work topMatches'''


def click_3():
    """if you want to see results with using command config you may use comment lines in a function"""
    var1, var2, var3 = entry_3.get().split(',')
    if var1 == 'critics':
        if var2.isdigit() and var3.isdigit():
            c = map(str, topMatches(critics, int(var2), int(var3)))
            messagebox.showinfo('topMatches', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_3.config(text=f"critics for user{var2}: " + json.dumps(c))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    elif var1 == 'books':
        var2 = str(var2)
        if var2 in names and var3.isdigit():
            c = map(str, topMatches(books, var2, int(var3)))
            messagebox.showinfo('topMatches', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_3.config(text=f"books for {var2}: " + json.dumps(c))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    else:
        messagebox.showerror("Error!", "Please check entered data.")


'''function to display the result of the work getRecommendations'''


def click_4():
    """if you want to see results with using command config you may use comment lines in a function"""
    var1, var2, var3 = entry_4.get().split(',')
    if var1 == 'critics':
        if var2.isdigit() and var3.isdigit():
            c = map(str, getRecommendations(critics, int(var2), int(var3)))
            messagebox.showinfo('recommendation', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_4.config(text=f"critics for user{var2}: " + json.dumps(c[1]))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    elif var1 == 'books':
        var2 = str(var2)
        if var2 in names and var3.isdigit():
            c = map(str, getRecommendations(books, var2, int(var3)))
            messagebox.showinfo('recommendation', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_4.config(text=f"books for {var2}: " + json.dumps(c))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    else:
        messagebox.showerror("Error!", "Please check entered data.")


'''function for creating new rating file'''


def click_5():
    var1 = entry_5.get()
    if var1.isdigit():
        d1 = {}
        List = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        for i in names:
            d1[i] = random.choices(List, weights=(random.shuffle([10, 20, 25, 30, 40, 45, 50, 60, 70, 80, 90])),
                                   k=int(var1))
        d1 = pd.DataFrame(d1)
        json_file = d1.to_json(orient='records')
        with open('ratings1.json', 'w') as f1:
            f1.write(json_file)
        os.system('start " " ratings1.json')


'''function for opening the beginning rating file'''


def click_6():
    os.system('start " " ratings.json')


'''function for removing new rating file if it exists'''


def click_7():
    if messagebox.askokcancel("Removing new rating file", "Do you want to remove ratings1.gson?"):
        if os.path.isfile('ratings1.json'):
            os.remove('ratings1.json')


'''function for opening readme file'''


def click_8():
    os.system('start " " readme.txt')


'''function to display the result of getRecommendedItems function'''


def click_9():
    """if you want to see results with using command config you may use comment lines in a function"""
    var1, var2, var3 = entry_9.get().split(',')
    if var1 == 'critics':
        if var2.isdigit() and var3.isdigit():
            c = map(str, getRecommendedItems(critics, itemsim, int(var2), int(var3)))
            messagebox.showinfo('recommendation', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_4.config(text=f"critics for user{var2}: " + json.dumps(c[1]))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    elif var1 == 'books':
        var2 = str(var2)
        if var2 in names and var3.isdigit():
            c = map(str, getRecommendedItems(books, itemsim2, var2, int(var3)))
            messagebox.showinfo('recommendation', '\n'.join([s.strip('(').strip(')') for s in c]))
            '''answer_4.config(text=f"books for {var2}: " + json.dumps(c))'''
        else:
            messagebox.showerror("Error!", "Please check entered data.")
    else:
        messagebox.showerror("Error!", "Please check entered data.")


'''
Function for exiting the application.
A pop-up window with buttons
to exit or cancel the action is used.
'''


def on_closing():
    if messagebox.askokcancel("Exiting the application",
                              "Do you want to exit the app?"):
        if os.path.isfile('ratings1.json'):
            os.remove('ratings1.json')
        root.destroy()


'''realization of interface'''
'''You need to uncomment some lines if You want to see all results in main window'''


root = Tk()
root.title("BookRecommendation")
root.geometry('1100x750')
root["bg"] = "#C8C3C9"
root.iconbitmap("book.ico")

txt = scrolledtext.ScrolledText(root, width=60, height=3,
                                bg='#B47EB2', font=("Courier", 12, "italic"))
txt.grid(row=0, column=0, columnspan=3)
txt.insert(INSERT, 'Welcome to the Books Recommendation app,''\n'
                   'the app for working with recommendation systems!')

txt1 = scrolledtext.ScrolledText(root, width=60, height=2,
                                 bg='#FCE0D5', font=("Courier", 12, "italic"))
txt1.grid(row=1, column=0, columnspan=3)
txt1.insert(INSERT, 'Functions for calculating similarity coefficient.' '\n'
                    'You need to enter 2 users.')
root.protocol("WM_DELETE_WINDOW", on_closing)

frame_1 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_1.grid(row=2, column=0)

label_1 = Label(frame_1, text="Calculating the similarity score"
                              "\nusing function sim_distance", bg='#99D0D3',
                font=("Courier", 12, "italic"))
label_1.grid(row=3, column=0)

entry_1 = Entry(frame_1)
entry_1.grid(row=4, column=0)

button_1 = Button(frame_1, text='calculate', command=click_1, bg='#2E958C',
                  font=("Courier", 12, "italic"))
button_1.grid(row=5, column=0)

'''answer_1 = Label(frame_1, text="sim_distance", bg='#99D0D3', 
                 font=("Courier", 12, "italic"))
answer_1.grid(row=6, column=0)'''

answer_1 = Label(frame_1, bg='#99D0D3', font=("Courier", 12, "italic"))
answer_1.grid(row=7, column=0)

frame_2 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_2.grid(row=2, column=1)

label_2 = Label(frame_2, text="Calculating the similarity score"
                              "\nusing function sim_pearson", bg='#99D0D3',
                font=("Courier", 12, "italic"))
label_2.grid(row=3, column=1)

entry_2 = Entry(frame_2)
entry_2.grid(row=4, column=1)

button2 = Button(frame_2, text='calculate', command=click_2,
                 bg='#2E958C', font=("Courier", 12, "italic"))
button2.grid(row=5, column=1)

'''answer_2 = Label(frame_2, text="sim_pearson", bg='#99D0D3', 
                 font=("Courier", 12, "italic"))
answer_2.grid(row=6, column=1)'''

answer_2 = Label(frame_2, bg='#99D0D3', font=("Courier", 12, "italic"))
answer_2.grid(row=7, column=1)

txt2 = scrolledtext.ScrolledText(root, width=60, height=2,
                                 bg='#FCE0D5', font=("Courier", 12, "italic"))
txt2.grid(row=8, column=0, columnspan=3)
txt2.insert(INSERT, 'All functions use the Pearson method to calculate the' '\n'
                    'similarity coefficient, as it gives better results.')

txt3 = scrolledtext.ScrolledText(root, width=30, height=3,
                                 bg='#FCE0D5', font=("Courier", 12, "italic"))
txt3.grid(row=9, column=0)
txt3.insert(INSERT, 'If you want to get matches for'
                    '\nuser or book, you may use next'
                    '\nfunction.')

txt4 = scrolledtext.ScrolledText(root, width=60, height=3,
                                 bg='#FCE0D5', font=("Courier", 12, "italic"))
txt4.grid(row=9, column=1, columnspan=3)
txt4.insert(INSERT, 'If you want to get recommendations for user, you may'
                    '\nuse next functions. First function generated new data'
                    '\nwith all restarts, second - use special file.')

frame_3 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_3.grid(row=10, column=0)

label_3 = Label(frame_3, text="You need to enter the names "
                              "\nof dictionary, user or book and \ncount of matches",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_3.grid(row=11, column=0)

entry_3 = Entry(frame_3, width=50)
entry_3.grid(row=12, column=0)

button3 = Button(frame_3, text='calculate', command=click_3,
                 bg='#2E958C', font=("Courier", 12, "italic"))
button3.grid(row=13, column=0)

'''answer_3 = Label(frame_3, text="topMatches", bg='#99D0D3', 
                 font=("Courier", 12, "italic"))
answer_3.grid(row=14, column=0)'''

'''answer_3 = Label(frame_3, bg='#99D0D3', font=("Courier", 12, "italic"))
answer_3.grid(row=15, column=0)'''

frame_4 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_4.grid(row=10, column=1)

label_4 = Label(frame_4, text="You need to enter the names"
                              "\nof dictionary, user or book and \ncount of recommendations",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_4.grid(row=11, column=1)

entry_4 = Entry(frame_4, width=50)
entry_4.grid(row=12, column=1)

button4 = Button(frame_4, text='calculate', command=click_4,
                 bg='#2E958C', font=("Courier", 12, "italic"))
button4.grid(row=13, column=1)

'''answer_4 = Label(frame_4, text="getRecommendations", bg='#99D0D3', 
                 font=("Courier", 12, "italic"))
answer_4.grid(row=14, column=1)'''

'''answer_4 = Label(frame_4, bg='#99D0D3', font=("Courier", 12, "italic"))
answer_4.grid(row=15, column=1)'''

txt5 = scrolledtext.ScrolledText(root, width=60, height=3,
                                 bg='#FCE0D5', font=("Courier", 12, "italic"))
txt5.grid(row=16, column=0, columnspan=3)
txt5.insert(INSERT, 'If you want to get new rating file, you may use left''\n'
                    'function and you need to restart the program.''\n'
                    'If you want to see beginning file use right function.')

frame_5 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_5.grid(row=17, column=0)

label_5 = Label(frame_5, text="You need to enter count of users",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_5.grid(row=18, column=0)

entry_5 = Entry(frame_5)
entry_5.grid(row=19, column=0)

button5 = Button(frame_5, text='create', command=click_5, bg='#2E958C',
                 font=("Courier", 12, "italic"))
button5.grid(row=20, column=0)

frame_6 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_6.grid(row=17, column=2)

label_6 = Label(frame_6, text="Click if you want to see\nrating file",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_6.grid(row=18, column=2)

button6 = Button(frame_6, text='see', command=click_6, bg='#2E958C',
                 font=("Courier", 12, "italic"))
button6.grid(row=19, column=2)

frame_7 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_7.grid(row=17, column=1)

label_7 = Label(frame_7, text="Click if you want to remove\nnew rating file",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_7.grid(row=18, column=1)

button7 = Button(frame_7, text='remove', command=click_7, bg='#2E958C',
                 font=("Courier", 12, "italic"))
button7.grid(row=19, column=1)

frame_8 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3", pady=4)
frame_8.grid(row=2, column=2)

label_8 = Label(frame_8,
                text="Click if you want to see\nreadme file with notes"
                     "\nabout the results of\nprevious functions",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_8.grid(row=3, column=2)

button6 = Button(frame_8, text='see', command=click_8, bg='#2E958C',
                 font=("Courier", 12, "italic"))
button6.grid(row=4, column=2)

frame_9 = Frame(root, borderwidth=10, relief=GROOVE, bg="#99D0D3")
frame_9.grid(row=10, column=2)

label_9 = Label(frame_9, text="You need to enter the names"
                              "\nof dictionary, user or book and "
                              "\ncount of recommendations",
                bg='#99D0D3', font=("Courier", 12, "italic"))
label_9.grid(row=11, column=2)

entry_9 = Entry(frame_9, width=50)
entry_9.grid(row=12, column=2)

button9 = Button(frame_9, text='calculate', command=click_9,
                 bg='#2E958C', font=("Courier", 12, "italic"))
button9.grid(row=13, column=2)

'''answer_9 = Label(frame_9, text="getRecommendedItems", bg='#99D0D3', 
                 font=("Courier", 12, "italic"))
answer_9.grid(row=14, column=2)'''

'''answer_9 = Label(frame_9, bg='#99D0D3', font=("Courier", 12, "italic"))
answer_9.grid(row=15, column=2)'''

button = Button(text="Click and quit", command=on_closing,
                bg='#B47EB2', font=("Courier", 12, "italic"))
button.grid(row=21, column=0, columnspan=3)

root.mainloop()
