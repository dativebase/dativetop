"""AOL Performance Tests

These aren't really tests. They are timings of basic AOL operations related to
persistence and file I/O.

Key Take-aways:

1. Since we are primarily adding to the ends of Python lists and appending to
   text files, all basic operations are in O(1).

2. The AOL persistence files can become quite large. An AOL of 80,000 lines is
   13M, one of 800,000 lines is 130M. The former takes 0.4 seconds to load into
   memory, the latter takes 4.8s. As an AOL grows, it should be persisted
   across multiple files.

3. Related to (2), reads from large AOLs should be implemented using multiple
   processes, each responsible for a portion of the AOL.

Detailed Q&As:

- Question: How long does it take to create a large AOL (list of Appendables) in
  memory?

  - Answer: Constant time, regardless of size of AOL. It takes about 0.00002
    seconds to generate a single appendable and append it to an AOL. In the
    following, we have (1) number of OLDInstances in AOL, (2) number of quads
    (entries) in AOL, (3) total time, and (4) time per append:

        >>> [(1, 8, 0.00017189979553222656, 2.148747444152832e-05),
        ...  (1000000, 8000000, 178.8148159980774, 2.2351851999759674e-05)]

- Question: How long does it take to write a large AOL file to disk?

  - Answer: Constant time, regardless of size of AOL. It takes 5e-06 seconds
    per appendable to write an AOL to disk:

        >>> [AOLPersist(entity_count=1, write_time=0.0002300739288330078, file_size=1358),
        ...  AOLPersist(entity_count=100000, write_time=4.107442140579224, file_size=135799993)]
        ...  AOLPersist(entity_count=1000000, write_time=40.92316484451294, file_size=1357999958)]

- Question: How long does it take to read a large AOL file from disk?

  - Answer: Apparently constant time. It takes 6e-06 seconds per appendable to
    read a large AOL from disk.

        >>> [('aol-size-10000.txt', 0.4077169895172119),   # 5.09e-06
        ...  ('aol-size-100000.txt', 4.75993800163269),    # 5.94e-06
        ...  ('aol-size-1000000.txt', 52.32560205459595)]  # 6.54e-06

- Question: How long does it take to append to a large AOL file on disk?

  - Answer: Constant time. It takes about 1.25e-05 seconds to append an
    appendable to an AOL, regardless of the size of the AOL. In the following,
    the times are for appending 8 appendables::

        >>> [('aol-size-1.txt', 0.00011014938354492188),
        ...  ('aol-size-10000.txt', 0.00010776519775390625),
        ...  ('aol-size-100000.txt', 0.0001049041748046875),
        ...  ('aol-size-1000000.txt', 0.000141143798828125)]

"""

from collections import namedtuple
import os
import pprint
import time

import pytest

import dtaoldm.aol as aol_mod
import tests.utils as utils


@pytest.mark.skip
def test_large_aol_creation_time():
    """Question: How long does it take to create a large AOL (list of
    Appendables) in memory?

    Answer: It takes about 0.00002 seconds to generate a single appendable and
    append it to an AOL:

        >>> [(1, 8, 0.00017189979553222656, 2.148747444152832e-05),
        ...  (10, 80, 0.0015330314636230469, 1.9162893295288086e-05),
        ...  (100, 800, 0.016254186630249023, 2.031773328781128e-05),
        ...  (1000, 8000, 0.15737318992614746, 1.9671648740768433e-05),
        ...  (10000, 80000, 1.645500898361206, 2.0568761229515075e-05)]
        ...  (100000, 800000, 17.846626043319702, 2.2308282554149627e-05),
        ...  (1000000, 8000000, 178.8148159980774, 2.2351851999759674e-05)]

    """
    times = []
    ns = (1, 10, 100, 1000, 10000, 100000, 1000000)
    for n in ns:
        t1 = time.time()
        large_aol = utils.generate_large_test_aol(n)
        t2 = time.time()
        tot_time = t2 - t1
        num_appendables = len(large_aol)
        time_per_appendable = tot_time / num_appendables
        times.append((n, num_appendables, tot_time, time_per_appendable))
    pprint.pprint(times)


@pytest.mark.skip
def test_large_aol_write_time():
    """Question: How long does it take to write a large AOL file to disk?

    - It takes 4 seconds to write a 800,000 line (containing 800,000
      appendables, representing 100,000 OLD instances) AOL to disk. That is
      5e-06 (0.000005) seconds to write each appendable when the file is
      800,000 lines long. A 800,000 line AOL file is 136 MB in size.

    - It takes 40 seconds to write a 8,000,000 line (containing 8,000,000
      appendables, representing 1,000,000 OLD instances) AOL to disk. That is
      still 5e-06 (0.000005) seconds to write each appendable. A 8,000,000 line
      AOL file is 1.3 GB in size.

        >>> [AOLPersist(entity_count=1, write_time=0.0002300739288330078, file_size=1358),
        ...  AOLPersist(entity_count=10, write_time=0.0006699562072753906, file_size=13580),
        ...  AOLPersist(entity_count=100, write_time=0.0044438838958740234, file_size=135800),
        ...  AOLPersist(entity_count=1000, write_time=0.04298996925354004, file_size=1358000),
        ...  AOLPersist(entity_count=10000, write_time=0.44002699851989746, file_size=13580000),
        ...  AOLPersist(entity_count=100000, write_time=4.107442140579224, file_size=135799993)]
        ...  AOLPersist(entity_count=1000000, write_time=40.92316484451294, file_size=1357999958)]

    """
    AOLPersist = namedtuple('AOLPersist', 'entity_count, write_time, file_size')
    runs = []
    ns = (1, 10, 100, 1000, 10000, 100000, 1000000)
    for n in ns:
        large_aol = utils.generate_large_test_aol(n)
        path = os.path.join(utils.TMP_PATH, f'aol-size-{n}.txt')
        t1 = time.time()
        aol_mod.persist_aol(large_aol, path)
        t2 = time.time()
        tot_time = t2 - t1
        aol_file_size = os.path.getsize(path)
        aol_persist = AOLPersist(
            entity_count=n,
            write_time=tot_time,
            file_size=aol_file_size)
        runs.append(aol_persist)
    pprint.pprint(runs)


@pytest.mark.skip
def test_large_aol_read_time():
    """Question: How long does it take to read a large AOL file from disk?

    - An 80,000-appendable (10,000 OLDInstances) AOL can be read from disk in
      0.4 seconds. Each read of an appendable takes 5e-06 seconds.
    - An 800,000-appendable (100,000 OLDInstances) AOL can be read from disk in
      4.8 seconds. Each read of an appendable takes 6e-06 seconds.
    - An 8,000,000-appendable (1,000,000 OLDInstances) AOL can be read from
      disk in 52 seconds. Each read of an appendable takes 6.5e-06 seconds.

        >>> [('aol-size-1.txt', 0.0003292560577392578),    # 4.11e-05
        ...  ('aol-size-10.txt', 0.0008230209350585938),   # 1.02e-05
        ...  ('aol-size-100.txt', 0.005694866180419922),   # 7.11e-06
        ...  ('aol-size-1000.txt', 0.05089879035949707),   # 6.36e-06
        ...  ('aol-size-10000.txt', 0.4077169895172119),   # 5.09e-06
        ...  ('aol-size-100000.txt', 4.75993800163269),    # 5.94e-06
        ...  ('aol-size-1000000.txt', 52.32560205459595)]  # 6.54e-06

    """
    fnames = sorted(fn for fn in os.listdir(utils.RESOURCES_PATH))
    runs = []
    for fn in fnames:
        aol_path = os.path.join(utils.RESOURCES_PATH, fn)
        t1 = time.time()
        aol = aol_mod.get_aol(aol_path)
        t2 = time.time()
        tot_time = t2 - t1
        aol = None
        runs.append((fn, tot_time))
    pprint.pprint(runs)


@pytest.mark.skip
def test_large_aol_append_time():
    """Question: How long does it take to append to a large AOL file on disk?

        >>> [('aol-size-1.txt', 0.00011014938354492188),
        ...  ('aol-size-10.txt', 0.000102996826171875),
        ...  ('aol-size-100.txt', 0.00010323524475097656),
        ...  ('aol-size-1000.txt', 0.00010609626770019531),
        ...  ('aol-size-10000.txt', 0.00010776519775390625),
        ...  ('aol-size-100000.txt', 0.0001049041748046875),
        ...  ('aol-size-1000000.txt', 0.000141143798828125)]

    """
    fnames = sorted(fn for fn in os.listdir(utils.RESOURCES_PATH))
    runs = []
    for fn in fnames:
        aol_path = os.path.join(utils.RESOURCES_PATH, fn)
        aol = aol_mod.get_aol(aol_path)
        aol_to_add = utils.generate_large_test_aol(1)
        t1 = time.time()
        for quad in aol_to_add:
            aol = aol_mod.append_to_aol(aol, quad)
        t2 = time.time()
        tot_time = t2 - t1
        runs.append((fn, tot_time))
    pprint.pprint(runs)
