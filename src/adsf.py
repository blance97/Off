from firebase import firebase
import json
if __name__ == '__main__':
    firebase = firebase.FirebaseApplication('https://slackbotadventures.firebaseio.com/', None)
    data = {'Kevin2': {'Armor': {'Arm': 'Lance'}, 'Attributes': {'Charisma': 0, 'Dexterity': 0, 'Health': 10, 'Intelligence': 1, 'Luck': 0, 'Strength': 0}, 'Inventory': {'Item': 'Soylent'}, 'Weapon': {'Wep': 'Lance'}}}
    data2 = {'Kevin': {'Attributes': {'Charisma': 5}}}
    result = firebase.get('/Characters/Kevin/Kevin/Attributes/Intelligence', None)
    print(result)
    data3 = {'Intelligence': 5}
    firebase.put('/Characters','k', data)