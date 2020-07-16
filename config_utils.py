def isColab():
    try:
        import google.colab
        return True
    except ModuleNotFoundError:
        return False

print(isColab())