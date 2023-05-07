# MongoDB
import pymongo
from pymongo.mongo_client import MongoClient

# Python
from decouple import config


client: MongoClient = MongoClient(config('URI', cast=str))
db = client['testdb']
users = db['users']
tasks = db['tasks']

ALL_LOGINS = [user.get('login') for user in users.find({}, {'_id':0,'login':1})]
USERS_COUNT = users.count_documents({})

CURRENT_USER = {}

TASKS_COUNT = tasks.count_documents({})

if not users.index_information().get('login_-1'):
    users.create_index([('login', pymongo.DESCENDING)], unique=True)
if not tasks.index_information().get('user_id_-1'):
    tasks.create_index([('user_id', pymongo.DESCENDING)])


def login():
    global CURRENT_USER

    while True:
        login = input('  [i] Enter your login : ')
        if not login:
            return
        if login in ALL_LOGINS:
            break
        print('  [x] User not found')

    user = users.find_one({'login': login})
    correct_password = user.get('password')
    while True:
        password = input('  [i] Enter your password : ')
        if not password:
            return
        if password == correct_password:
            break
        print('  [x] Password is invalid')

    print('  [v] You logged in succesfully')
    CURRENT_USER = user


def register():
    global USERS_COUNT

    data = {'_id': USERS_COUNT}
    while True:
        login = input('  [i] Enter your login : ')
        if not login:
            return
        if login not in ALL_LOGINS:
            data['login'] = login
            break
        print('  [x] Login already in use')

    while True:
        password = input('  [i] Enter your password : ')
        if not password:
            return
        if len(password) >= 7:
            data['password'] = password
            break
        print('  [x] Password\'s length must be at least 7 characters')

    while True:
        rep_password = input('  [i] Repeat your password : ')
        if not rep_password:
            return
        if rep_password == password:
            users.insert_one(data)
            USERS_COUNT += 1
            ALL_LOGINS.append(login)
            print('  [v] You registrated succesfully')
            break
        print('  [x] Passwords must be the same')


def logout():
    global CURRENT_USER

    if CURRENT_USER:
        CURRENT_USER = {}
        print('  [i] You logged out succesfully')
    else:
        print('  [i] You must log in before logging out')


def create_task():
    global CURRENT_USER, TASKS_COUNT
    
    if not CURRENT_USER:
        print('  [x] You must login before creating tasks')
        return

    data = {'_id': TASKS_COUNT, 'user_id': CURRENT_USER.get('_id'), 'is_done': False}

    _filter = {'user_id': CURRENT_USER.get('_id'), 'is_done': False}
    TASKS_TITLES = [task.get('title') for task in tasks.find(_filter)]

    while True:
        title = input('  [i] Enter title of task : ')
        if not title:
            return
        if title not in TASKS_TITLES:
            data['title'] = title
            break
        print('  [x] Title already in use')

    print('  [i] Task created succesfully')
    TASKS_COUNT += 1
    tasks.insert_one(data)


def complete_task():
    global CURRENT_USER, TASKS_COUNT
    
    if not CURRENT_USER:
        print('  [x] You must login before completing tasks')
        return

    _filter = {'user_id': CURRENT_USER.get('_id'), 'is_done': False}
    TASKS_TITLES = [task.get('title') for task in tasks.find(_filter)]

    if not TASKS_TITLES:
        print('  [x] You have not tasks')
        return
    
    print('  [i] Avilable tasks : ', end='')
    print(*TASKS_TITLES, sep=', ')
    print('')

    while True:
        title = input('  [i] Enter title of task : ')
        if not title:
            return
        if title in TASKS_TITLES:
            old = {'title': title, 'is_done': False}
            new = {'$set': {'is_done': True}}
            tasks.update_one(old, new)
            print('  [i] Title completed succesfully')
            break

        print('  [x] Title not found')


def show_tasks():
    global CURRENT_USER

    if not CURRENT_USER:
        print('  [x] You must login before completing tasks')
        return

    _filter = {'user_id': CURRENT_USER.get('_id')}
    _show = {'_id': 0}

    while True:
        print('  [i] Enter status of task\n\t0 - all\n\t1 - not done')
        status = input('\t2 - done : ')
        if not status:
            continue
        if status == '0':
            break
        if status == '1':
            _filter.update({'is_done': False})
            break
        if status == '2':
            _filter.update({'is_done': True})
            break
        print('  [x] Status is invalid')

    all_tasks = tuple(tasks.find(_filter, _show))
    if not all_tasks:
        print('\n  [x] You have not tasks\n')
        return
    print('')
    for _id, task in enumerate(all_tasks):
        status = ('Not done', 'Done    ')[task.get('is_done')]
        print(f'\t[{_id}] {status} | {task["title"][:30]}')
    print('')


actions = {
    'login': login,
    'register': register,
    'create-task': create_task,
    'complete-task': complete_task,
    'logout': logout,
    'show-tasks': show_tasks
}

while True:
    enter = input('enter action : ')
    if func := actions.get(enter):
        func()
    else:
        print('Avilable commands : ', end='')
        for command in actions:
            print(command, end=' ')
        print('')
