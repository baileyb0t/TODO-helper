class Line:
    def __init__(self, section, data):
        self.section = section
        self.data = data
        self.next = None


def insertAtBegin(self, data):
    """"""
    new_line = Line(data)
    if self.head is None:
        self.head = new_line
        return
    new_line.next = self.head
    self.head = new_line
    return 1
