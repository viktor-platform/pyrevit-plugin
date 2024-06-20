"""Triggers a pop-up modal allowing User to fill in PAT"""

from viktor.api import ask_for_personal_access_token


if __name__ == '__main__':
    token = ask_for_personal_access_token()


