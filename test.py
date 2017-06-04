from pywinauto.atspi_element_info import AtspiElementInfo

a = AtspiElementInfo()


def print_tree(root, level = 0):
    formater = "-"*level
    formater += "{}     {:^30}".format(root.class_name, root.name)
    print(formater)
    for el in root.children():
        print_tree(el, level=level+1)


def print_childrens(children):
    for ch in children:
        # print(ch.name)
        print(ch.class_name)
'{:^30}'.format('centered')
# a = a.children()[-2]
print_tree(root=a)
