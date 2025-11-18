from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("parrot")
except PackageNotFoundError:
    __version__ = "0.0.0"
    
print(__version__)