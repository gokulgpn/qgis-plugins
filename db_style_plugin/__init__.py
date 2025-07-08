from .apply_style import DbStylePlugin

def classFactory(iface):
    return DbStylePlugin(iface)


