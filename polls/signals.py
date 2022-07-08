from django import dispatch
from . import models


author_changed = dispatch.Signal()

