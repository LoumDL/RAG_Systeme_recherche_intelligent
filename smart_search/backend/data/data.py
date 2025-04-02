
import os
from contextlib import chdir

courses_dir = "courses"

with chdir(courses_dir):
    os.system("moodle-dl")