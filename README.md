## Sentiment Experiments

## TA Experiments
* The first part of the project is analyzing feedback on a course and assigning scores to TAs based on the sentiment of the reviews. This can be found under survey sentiment
* Three dictionaries are generated containing normalized scores of positive, negative and combined score reviews. The names have been changed.
* This can be used to better analyse performances of people in various areas. 
* You need two JSON files, one for your spreadsheet credentials, and one for the google API credentials. Instructions can be found on the Google Cloud API site.
  ```
  Pos dict {'Aditya': 0.42499999999999993, 'Aman': 0.2833333333333333, 'Rachel': 0.42045454545454547, 'Mudit': 0.44032258064516144, 'Sam': 0.3499999999999999, 'Achal': 0.375, 'Brenda': 0.35428571428571437, 'John': 0.23333333333333334, 'Pam': 0.38571428571428573, 'Denero': 0.27631578947368424, 'Twinkle': 0.5166666666666667}

  Neg dict {'Aditya': -0.005000000000000008, 'Aman': -0.19666666666666668, 'Rachel': -0.04999999999999998, 'Mudit': -0.07096774193548386, 'Sam': -0.12142857142857141, 'Achal': -0.12499999999999997, 'Brenda': -0.0257142857142857, 'John': -0.12142857142857148, 'Pam': -0.16857142857142857, 'Denero': -0.07105263157894737, 'Twinkle': -0.02916666666666667}

  Net dict {'Aditya': 0.41999999999999993, 'Aman': 0.08666666666666667, 'Rachel': 0.3704545454545455, 'Mudit': 0.3693548387096773, 'Sam': 0.22857142857142865, 'Achal': 0.24999999999999994, 'Brenda': 0.32857142857142857, 'John': 0.11190476190476192, 'Pam':0.21714285714285722, 'Denero': 0.20526315789473681, 'Twinkle': 0.48750000000000004}
  ```

## Spotify Sentiment Analysis

* First you need to ensure Google Auth Works. Register for a Google Cloud Account and follow the instructions there, you should have a json config file by the end of it and should be issue a command:

  ```
  export GOOGLE_APPLICATION_CREDENTIALS = path/to/config/file
  ```

* navigate to the this_time_flask folder and run hello.py
 
OR

* View the project on https://devpost.com/software/the-one-qmotin.
