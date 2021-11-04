class FileServerError(Exception):
  def __init__(self, *args):
    if args:
      self.message = args[0]
    else:
      self.message = None

  def __str__(self):
    if self.message:
      return 'FileServerError, {0} '.format(self.message)
    else:
      return 'FileServerError has been raised'