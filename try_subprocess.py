#!/bin/python

import sys
import subprocess

def execute(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Poll process for new output until finished
    while True:
        nextline = process.stdout.read()
        if nextline == '' and process.poll() != None:
            break
        print nextline

    output = process.communicate()[0]
    exitCode = process.returncode

    if (exitCode == 0):
        return output

execute(['./chessrisk'])
