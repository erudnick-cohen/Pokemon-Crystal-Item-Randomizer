import threading
import subprocess
import sys

class ProcessPrint(threading.Thread):
    stream = None
    output = None
    logFile = None
    allOutput = None

    def __init__(self, dataStream, output, logFile):
        threading.Thread.__init__(self)
        self.stream = dataStream
        self.output = output
        self.logFile = logFile
        self.allOutput = []

    def run(self):
        for item in self.stream:
            item = item.strip()
            print(item, file=self.output)
            self.output.flush()
            self.allOutput.append(item)

            if self.logFile is not None:
                self.logFile.write(item)
                self.logFile.flush()


def create(command, outLog=None, errLog=None):
    process = subprocess.Popen(command, universal_newlines=True,
                               shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = ProcessPrint(process.stdout, sys.stdout, outLog)
    error = ProcessPrint(process.stderr, sys.stderr, errLog)
    output.start()
    error.start()
    output.join()
    error.join()

    error_result = error.allOutput
    standard_result = output.allOutput

    return standard_result, error_result

