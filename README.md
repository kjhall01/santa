# santa
Santa's Village Optimization Kaggle Competition 12/23/2019

sgd_elf2.py is the final code
I implemented three separate optimization algorithms:
-same as starter notebook for this challenge, loop over the families' choices and try to give them the best possible one, keep if its better
- try to reschedule all the families in a given day until the day is at minimum capacity- select families to be rescheduled in random order 
-loop over top n days by cost and try to reschedule them all, increasing n as local minima are found

going forward , I would try to reschedule families randomly selected from the top n days rather than reschedule one day at a time- it would provide for more flexibility and maybe improve the result. who knows

final score of ~188000 - under 1000th place!
