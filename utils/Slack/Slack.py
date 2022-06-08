import os
import re
from prettytable import PrettyTable
from utils.Notion import Notion
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

load_dotenv()
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']

app = App(token=SLACK_BOT_TOKEN, name='EXP_BOT')


@app.message("hi")
def message_hi(say):
    say(text="Welcome to expense manager")
    say(text="What would you like me to do")
    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Add Data"
                        },
                        "action_id": "add_data"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Data"
                        },
                        "action_id": "view_data"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Dashboard"
                        },
                        "action_id": "view_dashboard"
                    }
                ]
            }
        ]
    )


@app.action("view_data")
def action_view(ack, say):
    ack()
    data = Notion.readDatabase()
    res = []
    for start in range(0, len(data), 50):
        res.append('')
        if start + 50 <= len(data):
            for line in data[start:start + 50]:
                res[-1] += line + '\n'
        else:
            for line in data[start:]:
                res[-1] += line + '\n'
    for i in res:
        say(text="```\n" + i + "\n```")

    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Okay",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "okay"
                    }
                ]
            }
        ]
    )


@app.action("view_dashboard")
def action_view_dashboard(ack, say):
    ack()
    say("Hold On!")
    Notion.exp_vs_date()
    response = app.client.files_upload(
        file='C:\\Users\\avina\\Documents\\Python\\Projects\\Slack_ExpBot\\Dashboard_Images\\exp_vs_date.png',
        initial_comment="IDK")
    say(response["file"]["permalink"])

    Notion.exp_donut()
    response = app.client.files_upload(
        file='C:\\Users\\avina\\Documents\\Python\\Projects\\Slack_ExpBot\\Dashboard_Images\\exp_donut.png',
        initial_comment="IDK")
    say(response["file"]["permalink"])
    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Okay",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "okay"
                    }
                ]
            }
        ]
    )


@app.event("message")
def handle_message_events(body):
    pass


@app.action("add_data")
def action_add(ack, say):
    ack()
    say(
        blocks=[
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "name",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "\n"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter your Expense Name",
                }
            }
        ]
    )


@app.action("name")
def action_name(body, ack, say):
    ack()
    global NAME
    NAME = body["actions"][0]["value"]
    # say(text=NAME)
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Choose Mode of Payment"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select an item",
                        "emoji": True
                    },
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Google Pay",
                                "emoji": True
                            },
                            "value": "google_pay"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Phone Pe",
                                "emoji": True
                            },
                            "value": "phone_pe"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Amazon Pay",
                                "emoji": True
                            },
                            "value": "amazon_pay"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Cash",
                                "emoji": True
                            },
                            "value": "cash"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Card",
                                "emoji": True
                            },
                            "value": "card"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Net Banking",
                                "emoji": True
                            },
                            "value": "net_banking"
                        }
                    ],
                    "action_id": "mode"
                }
            }
        ]
    )


@app.action("mode")
def action_mode(body, ack, say):
    ack()
    global MODE
    MODE = body["actions"][0]["selected_option"]["text"]["text"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Choose Direction of Flow"
                },
                "accessory": {
                    "type": "radio_buttons",
                    "options": [
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "In",
                                "emoji": True
                            },
                            "value": "value-0"
                        },
                        {
                            "text": {
                                "type": "plain_text",
                                "text": "Out",
                                "emoji": True
                            },
                            "value": "value-1"
                        }
                    ],
                    "action_id": "tag"
                }
            }
        ]
    )


@app.action("tag")
def action_tag(body, ack, say):
    ack()
    global TAG
    TAG = body["actions"][0]["selected_option"]["text"]["text"]
    say(
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Choose Date of Payment"
                },
                "accessory": {
                    "type": "datepicker",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Select a date",
                        "emoji": True
                    },
                    "action_id": "date"
                }
            }
        ]
    )


@app.action("date")
def action_date(body, ack, say):
    ack()
    global DATE
    DATE = body["actions"][0]["selected_date"]
    say(
        blocks=[
            {
                "dispatch_action": True,
                "type": "input",
                "element": {
                    "type": "plain_text_input",
                    "action_id": "flow",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "\n"
                    }
                },
                "label": {
                    "type": "plain_text",
                    "text": "Enter Amount",
                    "emoji": True
                }
            }
        ]
    )


@app.action("flow")
def action_flow(body, ack, say):
    ack()
    global FLOW
    FLOW = body["actions"][0]["value"]
    if re.search('\D', FLOW):
        say(text="Invalid string. String should only contain numbers")
        say(
            blocks=[
                {
                    "dispatch_action": True,
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "flow",
                        "placeholder": {
                            "type": "plain_text",
                            "text": "\n"
                        }
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "Enter Amount",
                        "emoji": True
                    }
                }
            ]
        )
    else:
        table = PrettyTable(["Name", "Mode", "Tag", "Date", "Flow"])
        table.add_row([NAME, MODE, TAG, DATE, FLOW])
        say(text="```\n" + str(table) + "\n```")
        say(
            blocks=[
                {
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Confirm action?"
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Yes"
                            },
                            "action_id": "confirm_yes"
                        },
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "No"
                            },
                            "action_id": "confirm_no"
                        }
                    ]
                }
            ]
        )


@app.action("confirm_yes")
def action_confirm_yes(ack, say):
    ack()
    status = Notion.createPage(NAME, MODE, TAG, DATE, FLOW)
    if status == 200:
        say(text="Data has been added to the database")
    else:
        say(text="Could not add Data to the database")
    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Okay",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "okay"
                    }
                ]
            }
        ]
    )


@app.action("confirm_no")
def action_confirm_no(ack, say):
    ack()
    say(text="Data has not been added to the database")
    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Okay",
                            "emoji": True
                        },
                        "value": "click_me_123",
                        "action_id": "okay"
                    }
                ]
            }
        ]
    )


@app.action("exit")
def action_exit(ack, say):
    ack()
    say(text="\nBye!!!!")


@app.action("okay")
def action_okay(ack, say):
    ack()
    say(
        blocks=[
            {
                "type": "divider"
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Add Data"
                        },
                        "action_id": "add_data"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Data"
                        },
                        "action_id": "view_data"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "View Dashboard"
                        },
                        "action_id": "view_dashboard"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Exit"
                        },
                        "action_id": "exit"
                    }
                ]
            }
        ]
    )


def main():
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
