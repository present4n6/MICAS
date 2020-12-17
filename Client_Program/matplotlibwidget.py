from PyQt5.QtWidgets import*
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import pymysql
import networkx as nx
import os, sys,math
from tabulate import tabulate
import matplotlib.font_manager
from matplotlib import font_manager, rc
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import platform
import numpy as np
import pickle
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import paramiko
import time,copy
from scp import SCPClient



class matplotlibWidget(QWidget):

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        # self.canvas = FigureCanvas(Figure())
        vertical_layout = QVBoxLayout()
        self.figure = plt.figure('Relation Visualize')
        canvas = FigureCanvas(self.figure)
        graph = nx.Graph()

        cli = paramiko.SSHClient()
        cli.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        cli.connect("218.146.20.50", port=2185, username="hadoopuser", password="bob")
        command = 'cat /home/hadoopuser/Email_Visualize.txt'
        stdin, stdout, stderr = cli.exec_command(command)
        stdout = ''.join(stdout.readlines())

        whitelist = []
        if stdout.startswith('Visualize'):
            for i in range(0, len(stdout.split('\n')[1].split(';')) - 1):
                graph.add_edge(stdout.split('\n')[1].split(';')[i], stdout.split('\n')[2].split(';')[i],
                               weight=stdout.split('\n')[3].split(';')[i])
            for i in range(0, len(stdout.split('\n')[4].split(';')) - 1):
                whitelist.append(stdout.split('\n')[4].split(';')[i])

            pos = nx.spring_layout(graph)
            nx.draw(graph, pos=pos, with_labels=True)
            labels = nx.get_edge_attributes(graph, 'weight')
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)

            nx.draw_networkx_nodes(graph, pos, nodelist=whitelist, node_color='#00CE2C', node_size=500)

            plt.margins(x=0.4, y=0.4)
        elif stdout.startswith('Unknown'):
            for i in range(0, len(stdout.split('\n')[1].split(';')) - 1):
                graph.add_edge(stdout.split('\n')[1].split(';')[i], stdout.split('\n')[2].split(';')[i],
                               weight=stdout.split('\n')[3].split(';')[i])

            pos = nx.spring_layout(graph)
            nx.draw(graph, pos=pos, with_labels=True)
            labels = nx.get_edge_attributes(graph, 'weight')
            nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels)
            plt.margins(x=0.4, y=0.4)

        canvas.draw_idle()
        toolbar = NavigationToolbar(canvas, self)
        vertical_layout.setContentsMargins(1, 1, 1, 1)
        vertical_layout.addWidget(toolbar)
        vertical_layout.addWidget(canvas)

        self.setLayout(vertical_layout)

