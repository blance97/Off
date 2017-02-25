from firebase import firebase

if __name__ == '__main__': 
    print("Hello World")

    firebase = firebase.FirebaseApplication('https://slackbotadventures.firebaseio.com', None)

    result = firebase.get('/Character', None)
    print result