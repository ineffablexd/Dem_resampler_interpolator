
def classFactory(iface):
    from .plugin import DEMResamplePlugin
    return DEMResamplePlugin(iface)
