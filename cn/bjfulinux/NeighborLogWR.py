class NeighborLogWR():
    def __init__(self, protocol):
        self.protocol = protocol

    def openfile(self, methrod):
        self.file = open('neighbor-log-'+self.protocol+'.txt', methrod)

    def writelog(self, time, x1, y1, x2, y2):
        print(str(round(time, 3)), str(x1), str(y1), str(x2), str(y2), file=self.file)

    def readlog(self):
        return self.file.readlines()

    def close(self):
        self.file.close()

