
"""
    Format int representing a file size in bytes to a sub 1000 number with appropriate nomination.
    1234567  -> 123.4kB
"""
def formatFilesize(size:int=0, digits:int=1):
    type = ['Bytes', 'kB', 'MB', 'GB', 'TB']
    selector = 0
    fsize = float(size)
    while (fsize > 1000):
        fsize /= 1000
        selector += 1
    if fsize % 1 == 0:
        digits = 0
    return '{:.{prec}f}'.format(fsize, prec=digits) + type[selector]

