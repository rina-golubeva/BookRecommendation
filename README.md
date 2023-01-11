# BookRecommendation
a project in the 2nd semester about a personal selection of books for reading

BookRecommendation is an app for learning recommendation system.
If You want to see the work of such systems from insude, You may use this app.
You may see some frames in main window: it applies to pairs with common purpose or topic.

First frames give You the opportunity to calculate the similar coefficient from two users or to see the Readme file.
Those functions use different equations for calculating: euclidean distanse estimation and pearson correlation coefficient.

Euclidean distanse estimation. In this case, the items that people evaluated together are presented as coordinate axes. 
Now in this coordinate system, you can place points corresponding to people and see how close they are.
The closer two people are in preference space, the more similar their preferences are. Since this chart is two-dimensional, 
you can only look at two indicators at a time, but the principle is the same for more indicators.
The function always returns a value between 0 and 1, with 1 being the exact match between two people's preferences.
If You see the number greater then 0.0003 it is a very good result, 
the number from 0.0002 to 0.0003 is a good result, 
the number from 0.0001 to 0.0002 is an acceptable result,
the number smaller then 0.0001 is a bad result.

Pearson correlation coefficient. The Pearson correlation coefficient is a measure of how well two sets of data fit a straight line. 
The formula is more complicated than that for calculating the Euclidean distance, but it gives better results when the data is poorly normalized, 
for example, if some critic consistently gives films lower than average ratings.
The Pearson correlation coefficient has one interesting property that can be observed in the figure - it corrects for the discounting of estimates. 
If one critic tends to give higher marks than another, then perfect correlation is still possible, provided that the difference in marks is constant. 
The Euclidean distance method in this case would produce the result that the critics are not alike, since one always turns out to be stricter than the other, 
despite the fact that their tastes are essentially very similar.
This function returns a value between -1 and 1. A value of 1 means that two people gave each item exactly the same rating.
If You see the number greater then 0.005 it is a very good result, 
the number from 0.0025 to 0.005 is a good result, 
the number from 0 to 0.0025 is an acceptable result,
the number smaller then 0 is a bad result.

Second frames give You the opportunity to see list of similar critics or books and the list of recommendation for the critic or the book.

TopMatches. Given functions to compare two people, it is possible to write a function that will calculate the similarity score 
of all available people with a given person and look for the best match.
This function allows you to look at similar books using the same method.
This function return pop-up window with the list of pairs: critic or book and the similarity coefficient with the given critic or book.
If You see the number greater then 0.2 it is a very good result, 
the number from 0.05 to 0.2 is a good result, 
the number from 0.001 to 0.05 is an acceptable result,
the number smaller then 0.001 is a bad result.

GetRecommendation. It would be possible to see which books liked by critics with similar tastes, and choose from them those that the first critic had not yet read.
But with such an approach, one might accidentally stumble upon critics who have not written anything about books that the user might like.
You can also select a critic who for some reason liked a book that received negative reviews from all the other critics included in the topMatches list.
To solve these problems, it is necessary to rank the books themselves by calculating a weighted sum of critics' ratings. 
We take each of the selected critics and multiply their similarity score with the user by the score they gave each book.
If You see the number greater then 3 it is a very good result, 
the number from 2 to 3 is a good result, 
the number from 1 to 2 is an acceptable result,
the number smaller then 1 is a bad result.

GetRecommendedItems. This function really similar to getRecommendation with one updating: we use special file with matches for each book or user.
It is usefull if you are working with big data, where there are a lot of books or something else. So we can create file with the top matches for each position and use it.
If You see the number greater then 4.5 it is a very good result, 
the number from 3 to 4.5 is a good result, 
the number from 2 to 3 is an acceptable result,
the number smaller then 2 is a bad result.

Third frames give You the opportunity to create new rating file with the given number of critics and remove it or to see to the beginning rating file.
