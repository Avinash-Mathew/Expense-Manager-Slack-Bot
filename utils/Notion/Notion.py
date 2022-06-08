import requests
import json
import calendar
import os
import re
import numpy as np
import matplotlib.pyplot as plt
import datetime
from dotenv import load_dotenv
from prettytable import PrettyTable

load_dotenv()
INTEGRATION_TOKEN = os.environ['INTEGRATION_TOKEN']
DATABASE_ID = os.environ['DATABASE_ID']
SALARY = os.environ['SALARY']

headers = {
    "Accept": "application/json",
    "Notion-Version": "2022-02-22",
    "Content-Type": "application/json",
    "Authorization": "Bearer " + INTEGRATION_TOKEN,
}


def readDatabase(database_id=DATABASE_ID, headers=headers):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    res = requests.request("POST", url, headers=headers)
    data = res.json()
    table = PrettyTable(["Name", "Mode", "Date", "Net"])
    # print(res.status_code)
    for i in range(0, len(data["results"])):
        # if int(re.findall(r'(?:\d{4})-(\d{2})-(?:\d{2})', data["results"][i]["properties"]["Date"]["date"]["start"])[0])==datetime.datetime.today().month:
        date = data["results"][i]["properties"]["Date"]["date"]["start"]
        net = data["results"][i]["properties"]["Net"]["formula"]["number"]
        mode = data["results"][i]["properties"]["Mode"]["select"]["name"]
        name = data["results"][i]["properties"]["Name"]["title"][0]["text"]["content"]
        table.add_row([name, mode, date, net])

    table.sortby = "Date"
    return str(table).split("\n")


def createPage(name, mode, tag, date, flow, database_id=DATABASE_ID, headers=headers):
    url = 'https://api.notion.com/v1/pages'
    newPageData = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [
                    {
                        "text": {
                            "content": name
                        }
                    }
                ]
            },
            "Mode": {
                "select": {
                    "name": mode
                }
            },
            "Tags": {
                "select": {
                    "name": tag
                }
            },
            "Date": {
                "date": {
                    "start": date
                }
            },
            "Flow": {
                "number": int(flow)
            }
        }
    }

    data = json.dumps(newPageData)

    res = requests.request("POST", url, headers=headers, data=data)
    return res.status_code


def exp_vs_date(database_id=DATABASE_ID, headers=headers, year=datetime.date.today().year):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    res = requests.request("POST", url, headers=headers)
    data = res.json()
    net = [0] * 12
    for i in range(0, len(data["results"])):
        if int(re.findall(r'(\d{4})-(?:\d{2})-(?:\d{2})', data["results"][i]["properties"]["Date"]["date"]["start"])[
                   0]) == year:
            t = int(
                re.findall(r'(?:\d{4})-(\d{2})-(?:\d{2})', data["results"][i]["properties"]["Date"]["date"]["start"])[
                    0]) - 1
            net[t] += data["results"][i]["properties"]["Net"]["formula"]["number"]

    fig = plt.figure(figsize=(10, 5))
    fig.patch.set_facecolor('#121212')

    ax = fig.add_subplot(1, 1, 1)
    ax.set_facecolor('#121212')
    ax.tick_params(axis='x', colors='#787A91')
    ax.tick_params(axis='y', colors='#787A91')
    ax.spines['left'].set_color('#787A91')
    ax.spines['bottom'].set_color('#787A91')
    ax.spines['right'].set_color('#121212')
    ax.spines['top'].set_color('#121212')
    ax.set_ylabel('Net')
    ax.yaxis.label.set_color('#787A91')
    ax.set_xlabel('Month')
    ax.xaxis.label.set_color('#787A91')

    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    plt.bar(months, net,
            color=['#EF6B3A', '#A12D5D', '#ED0e47', '#700460', '#032D7A', '#1A1333', '#FABE54', '#055458', '#ABD96D',
                   '#15C286', '#262949', '#087353'])
    plt.savefig('C:\\Users\\avina\\Documents\\Python\\Projects\\Slack_ExpBot\\Dashboard_Images\\exp_vs_date.png',
                bbox_inches='tight')


def exp_donut(database_id=DATABASE_ID, headers=headers, year=datetime.date.today().year):
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    res = requests.request("POST", url, headers=headers)
    data = res.json()
    net = [0] * 12
    salary = int(SALARY)
    for i in range(0, len(data["results"])):
        if int(re.findall(r'(\d{4})-(?:\d{2})-(?:\d{2})', data["results"][i]["properties"]["Date"]["date"]["start"])[
                   0]) == year:
            t = int(
                re.findall(r'(?:\d{4})-(\d{2})-(?:\d{2})', data["results"][i]["properties"]["Date"]["date"]["start"])[
                    0]) - 1
            net[t] += data["results"][i]["properties"]["Net"]["formula"]["number"]

    fig, ax = plt.subplots(3, 4, figsize=(18, 9), subplot_kw=dict(aspect="equal"))
    fig.patch.set_facecolor('#121212')
    for row in range(3):
        for col in range(4):
            label = ["Spent",
                     "Balance"
                     ]
            month = 4 * row + col
            data = [net[month], salary - net[month]]
            colors = []
            if net[month] < 0.4 * salary:
                colors.append("green")
            elif net[month] < 0.75 * salary and net[month] > 0.4 * salary:
                colors.append("yellow")
            else:
                colors.append("red")

            colors.append("#404040")
            wedges, texts, pcts = ax[row][col].pie(data, wedgeprops=dict(width=0.5, edgecolor="k"),
                                                   startangle=-40, explode=(0.05, 0.05), colors=colors,
                                                   autopct="%1.1f%%",
                                                   pctdistance=0.75, textprops=dict(color='white'), shadow=True)
            bbox_props = dict(boxstyle="square,pad=0.3", fc="#121212", ec="k", lw=0.72)
            kw = dict(arrowprops=dict(arrowstyle="-", color='#787A91'),
                      bbox=bbox_props, zorder=0, va="center")
            for i, p in enumerate(wedges):
                ang = (p.theta2 - p.theta1) / 2. + p.theta1
                y = np.sin(np.deg2rad(ang))
                x = np.cos(np.deg2rad(ang))
                horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
                connectionstyle = "angle,angleA=0,angleB={}".format(ang)
                kw["arrowprops"].update({"connectionstyle": connectionstyle})
                ax[row][col].annotate(label[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y), color="#787A91",
                                      horizontalalignment=horizontalalignment, **kw)

            ax[row][col].set_title(calendar.month_name[int(month) + 1], color='white')

    plt.subplots_adjust(hspace=0.4)
    plt.savefig('C:\\Users\\avina\\Documents\\Python\\Projects\\Slack_ExpBot\\Dashboard_Images\\exp_donut.png',
                bbox_inches='tight')
