#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
from functools import reduce
from PIL import Image

import sys
import os

import six
import hashlib

from pathlib import Path

import imagehash
from pymemcache.client.base import PooledClient as MemcacheClient
from pymemcache import serde

import threading
from queue import PriorityQueue
from threading import Thread

import warnings
warnings.filterwarnings("ignore")

import multiprocessing

cache = MemcacheClient('localhost', serde=serde.pickle_serde)
img_queue = PriorityQueue()
hash_queue = PriorityQueue()

MAIN_FUNC = imagehash.average_hash
SECOND_FUNC = imagehash.dhash

STD_PRIO = 100
HIGH_PRIO = 10

def image_size(img):
    img_key = hashlib.md5(img.encode('utf-8')).hexdigest()
    img_hashes = cache.get(img_key)
    if img_hashes:
        return img_hashes.get("size", 0)
    return 0

def get_image_hash():
    while True:
        _prio, img_path, hashfunc = img_queue.get()
        img_key = hashlib.md5(img_path.encode('utf-8')).hexdigest()
        img_hashes = cache.get(img_key)
        if img_hashes:
            if img_hashes.get(getattr(hashfunc,"__name__")):
                # We computed this hash before no need to bother but we need to mark work as completed
                img_queue.task_done()
                continue
        try:
            img = Image.open(img_path)
            img_size = reduce((lambda x,y: x*y), img.size)
            img_hash = hashfunc(img)
            if img_hashes:
                img_hashes.update({getattr(hashfunc,"__name__"): str(img_hash)})
            else:
                img_hashes = {getattr(hashfunc,"__name__"): str(img_hash)}
            img_hashes.update({"size": img_size})
            cache.set(img_key, img_hashes)
            hash_queue.put((STD_PRIO, img_path, hashfunc, img_hash, img_size))
        except Exception as e:
            print("Removing: '{0}' due to {1}".format(img_path, e))
            path = Path(img_path)
            path.unlink(missing_ok=True)
        finally:
            img_queue.task_done()

def check_image_hash():
    while True:
        _prio, img_path, hashfunc, img_hash, img_size = hash_queue.get()
        hash_str = '{0}:{1}'.format(getattr(hashfunc,"__name__"), str(img_hash))
        cache_item = cache.get(hash_str)
        if cache_item:
            if img_path not in set(cache_item):
                # We found a genuine duplicate, now we should try to compute other hashes
                cache_item.append(img_path)
                if hashfunc == MAIN_FUNC:
                    for _img in cache_item:
                        img_queue.put((HIGH_PRIO, _img, SECOND_FUNC))
        else:
            cache_item = [img_path]
        cache.set(hash_str, cache_item)
        if len(cache_item) > 1 and hashfunc==SECOND_FUNC:
            print("Duplicates: {}".format(" ".join(["'{0}'".format(img) for img in sorted(cache_item, key=image_size, reverse=True)])))
        hash_queue.task_done()

def find_similar_images(userpaths):
    def is_image(filename):
        f = filename.lower()
        return f.endswith(".png") or f.endswith(".jpg") or \
            f.endswith(".jpeg") or f.endswith(".bmp") or \
            f.endswith(".gif") or '.jpg' in f or  f.endswith(".svg")
    
    image_filenames = []
    for userpath in userpaths:
        image_filenames += [os.path.join(userpath, path) for path in os.listdir(userpath) if is_image(path)]
    for img in sorted(image_filenames):
        img_queue.put((STD_PRIO, img, MAIN_FUNC))

if __name__ == '__main__':
    userpaths = sys.argv[1:] if len(sys.argv) > 1 else "."
    for i in range(2*multiprocessing.cpu_count()):
        Thread(target=get_image_hash, daemon=True).start()
    Thread(target=check_image_hash, daemon=True).start()
    find_similar_images(userpaths)
    img_queue.join()
    hash_queue.join()
