#!/usr/bin/env python
# coding: utf-8

# In[1]:


get_ipython().system('pip install python-doi')


# In[ ]:


# todo: use namedtuple


# In[2]:


import doi
import os
import shutil
from pprint import pprint
from collections import Counter


# In[3]:


errors = Counter()


# In[5]:


a = []
for path, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".pdf"):
            a.append((path, file, doi.pdf_to_doi(os.path.join(path, file))))
a


# In[6]:


len(list(filter(lambda x: x[2] is None, a)))


# In[7]:


len(list(filter(lambda x: bool(x[2]), a)))


# In[8]:


len(a)


# In[10]:


b = []
for path, file, DOI in a:
    try:
        clean = doi.get_clean_doi(DOI)
    except TypeError:
        errors["type_error"] += 1
    else:
        b.append((path, file, clean))


# In[11]:


len(b), b


# In[12]:


import re
import sys
import logging

from typing import Optional


__version__ = '0.1.1'
logger = logging.getLogger("doi")   # type: logging.Logger

def validate_doi(doi: str) -> Optional[str]:
    """We check that the DOI can be resolved by
    `official means <http://www.doi.org/factsheets/DOIProxy.html>`_. If so, we
    return the resolved URL, otherwise, we return ``None`` (which means the
    DOI is invalid).

    :param doi: Identifier.
    :returns: The URL assigned to the DOI or ``None``.
    """
    from urllib.error import HTTPError
    import urllib.request
    import urllib.parse
    import json
    url = "https://doi.org/api/handles/{doi}".format(doi=doi)
    logger.debug('handle url %s', url)
    request = urllib.request.Request(url)

    try:
        result = json.loads(urllib.request.urlopen(request).read().decode())
    except HTTPError:
        raise ValueError('HTTP 404: DOI not found')
    else:
        urls = [v['data']['value']
                for v in result['values'] if v.get('type') == 'URL']
        return (doi, urls[0]) if urls else None


# In[13]:


c = []
for path, file, DOI in b:
    try:
        doi, url = validate_doi(DOI)
    except: # todo: handle InvalidURL better
        errors["invalid_url"] += 1
    else:
        c.append((path, file, doi, url))


# In[14]:


len(c), c, errors


# In[15]:


def safe_filename(s):
    """/ \ :* " ? < >"""
    return re.sub(r"/", "_", s)


# In[16]:


d = [(x[0], x[1], safe_filename(x[2]) + ".pdf") for x in c]
d


# In[17]:


for i in d:
    new = os.path.join(i[0], i[2])
    if not os.path.exists(new):
        old = os.path.join(i[0], i[1])
        os.rename(old, new)


# In[ ]:




