
#验证列表属性
def verify_list_instance(value):
    value = eval(value)
    if not isinstance(value, list):
        return False
    else:
        if len(value) <= 0:
            return False
        else:
            return True


