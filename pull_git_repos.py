#!/usr/bin/env python

"""Run this utility manually from a command line to refresh all Git repository clones used in this documentation."""

import os
from globals import REPO_BASE, REPO_BRANCH
from conf.projects import projects


def main():

    for repo in projects:
        os.chdir(REPO_BASE + repo)
        try:
            os.system(f"git pull origin {REPO_BRANCH}")
            print(f"{repo}: Success")
        except BaseException as err:
            print(f"{repo}: {err}")


if __name__ == "__main__":
    main()
