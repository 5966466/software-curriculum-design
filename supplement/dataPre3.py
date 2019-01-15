import torch
import torchvision
from torch import nn
import torch.nn.functional as F
import torchvision.transforms as transforms
import sqlite3
import os
import numpy as np
import threading, time

import zipfile, shutil

from xdb_test import XDB_test
import sys

class DataPre():
    def __init__(self, filepath, setpath):
        self.filepath = filepath.split('.')[0]
        self.setpath = setpath

        self.st_msg = (True, None)

        setName = os.path.basename(filepath)
        self.setName = setName.split('.')[0]

        self.tableName = 'DataPre'
        self.connection = sqlite3.connect(\
            os.path.join(self.setpath, self.setName+'.db'))
        self.cursor = self.connection.cursor()
        path = os.path.join(self.setpath, self.setName)
        if not os.path.exists(path):
            os.mkdir(path)

        self.states = np.array(['Wrong', 'Right'])
        self.labels = ['airplane', 'automobile', 'bird', 'cat', 'deer', \
                'dog', 'frog', 'horse', 'ship', 'truck']

        self.lock = threading.Lock()
        #self.net = 0
        #self.device = 0
        #self.tups = []
        
    def add_msg(self, msg):
        if self.st_msg[0]:
            self.st_msg = (False, msg)

    def execute_set(self, demand):
        self.cursor.execute(demand)
        self.connection.commit()
        data = self.cursor.fetchall()
        return data

    def create_table(self):
        dm = '''CREATE TABLE %s
            (
            id integer NOT NULL PRIMARY KEY AUTOINCREMENT, 
            labelled_img varchar(50) NULL, 
            interfered_img varchar(50) NULL, 
            state varchar(10) NULL
            );''' % self.tableName

        try:
            self.execute_set(dm)
        except Exception as e:
            self.add_msg(str(e))

    def insert_table(self, labelled_img, interfered_img, state):
        dm = '''INSERT INTO %s(labelled_img, interfered_img, state)
            VALUES('%s', '%s', '%s');'''\
            % (self.tableName, labelled_img, interfered_img, state)

        try:
            self.execute_set(dm)
        except Exception as e:
            self.add_msg(str(e))

    def insert_table_all(self, tups):
        for tup in tups:
            dm = '''INSERT INTO %s(labelled_img, interfered_img, state)
                VALUES('%s', '%s', '%s');'''\
                % (self.tableName, tup[0], tup[1], tup[2])
            try:
                self.cursor.execute(dm)
            except Exception as e:
                self.add_msg(str(e))

        try:
            self.connection.commit()
        except Exception as e:
            self.add_msg(str(e))

    def get_pics(self, test_data):
        #net = torch.load(os.path.join(self.setpath, 'model'), map_location='cpu')['net']
        #device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #net.to(device)
        #net.eval()
        tups = []
        tol = len(test_data)
        for i, (inputs, name) in enumerate(test_data):
            #if (i+1) % 10 != 0:
            #    continue
            inputs = inputs.to(self.device)
            outputs = self.net(inputs)
            pre_label = outputs.max(1)[1]
            lbs = [self.labels[i] for i in pre_label]
            sentc = list(np.array(lbs) == np.array(name))
            sentc = [int(j) for j in sentc]
            sentc = list(self.states[sentc])
            tup = list(zip(name, lbs, sentc))
            tups.extend(tup)
            print('%s/%s' % (i, tol))

        return tups

    def initialize(self):
        filepath = self.filepath + '.zip'
        try:
            z = zipfile.ZipFile(filepath, 'r')
            z.extractall(path=os.path.dirname(filepath))
        except Exception as e:
            for i in a.namelist():
                if os.path.isdir(i):
                    shutil.rmtree(filepath)
                elif os.path.isfile(i):
                    os.remove(filepath)
            self.st_msg = (False, str(e))

        z.close()
        sys.path.append(self.filepath)
        import procdb
        procdb.update(self.filepath)
        sys.path.remove(self.filepath)
        transform = transforms.Compose(
            [
                transforms.ToTensor(), 
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
            ]
        )
        path = os.path.join(self.filepath, 'test_list.txt')
        test_set = XDB_test(path, transform = transform)
        test_data = torch.utils.data.DataLoader(test_set, batch_size = 128, shuffle = False)
        self.net = torch.load(os.path.join(self.setpath, 'model'))['net']
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.net.to(self.device)
        self.net.eval()
        return test_data
        
    def estab_table(self):
        self.create_table()
        test_data = self.initialize()
        print(time.ctime())
        tups = self.get_pics(test_data)
        print(time.ctime())
        self.insert_table_all(tups)
        print(time.ctime())
        shutil.rmtree(self.filepath)

    def get_one_pic(self, t_d):
        for inputs, name in t_d:
            inputs = inputs.to(self.device)
            outputs = self.net(inputs)
            pre_label = outputs.max(1)[1]
            lbs = [self.labels[i] for i in pre_label]
            sentc = list(np.array(lbs) == np.array(name))
            sentc = [int(j) for j in sentc]
            sentc = list(self.states[sentc])
            tup = list(zip(name, lbs, sentc))
            self.lock.acquire()
            self.tups.extend(tup)
            self.lock.release()

    def estab_table2(self):
        self.create_table()
        test_data = self.initialize()
        self.tups = []
        t_d = []
        for i, (inputs, name) in enumerate(test_data):
            t_d.append((inputs, name))
            if (i+1) % 10 == 0:
                thread = threading.Thread(target=self.get_one_pic, args=(t_d,))
                thread.daemon = True
                thread.start()
                print(i)
                t_d = []
                
        if t_d != []:
            thread = threading.Thread(target=self.get_one_pic, args=(t_d,))
            thread.daemon = True
            thread.start()
            print(i)

        thread.join()
        self.insert_table_all(self.tups)
        shutil.rmtree(self.filepath)



    def show(self):
        dm = "SELECT DISTINCT(labelled_img) FROM %s" % (self.tableName)
        data = self.execute_set(dm)
        print(data)
        print("hello")
        #for i in data:
        #    print(i)







