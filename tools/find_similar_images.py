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

from oslo_config import cfg,types

CONF = cfg.CONF

opts = [
    cfg.StrOpt("memcache-server", help="Memcached server sddress", default="localhost"),
    cfg.MultiOpt("path", item_type=types.String(), help="Pictures path(s)", default="."),
    cfg.IntOpt("threads", help="Number of processing threads", default=2*multiprocessing.cpu_count()),
    cfg.BoolOpt("delete-bad-files", help="Remove files that fail to process", default=True),
    cfg.BoolOpt("delete-duplicates", help="Remove duplicate files and keep the one with the higest resolution", default=False),
    cfg.StrOpt("tombstone", help="Tombstone sufix for deleted duplicates", default=".tombstone")
]

CONF.register_cli_opts(opts)
CONF(sys.argv[1:])

cache = MemcacheClient(CONF.memcache_server, serde=serde.pickle_serde)
img_queue = PriorityQueue()
hash_queue = PriorityQueue()

MAIN_FUNC = imagehash.average_hash
SECOND_FUNC = imagehash.dhash

STD_PRIO = 100
HIGH_PRIO = 10

def image_size(img):
    img_key = hashlib.md5(str(img).encode('utf-8')).hexdigest()
    img_hashes = cache.get(img_key)
    if img_hashes:
        return img_hashes.get("size", 0)
    return 0

def is_image(path):
    suffix = path.suffix.lower()
    return suffix in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".jpg", ".svg"]

def get_image_hash():
    while True:
        _prio, img_path, hashfunc = img_queue.get()
        if not img_path.exists():
            # Don't waste cycles for removed images
            img_queue.task_done()
            continue
        img_key = hashlib.md5(str(img_path).encode('utf-8')).hexdigest()
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
            if CONF.delete_bad_files:
                print("Removing: '{0}' due to {1}".format(img_path, e))
                img_path.unlink(missing_ok=True)
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
            file_list = sorted(cache_item, key=image_size, reverse=True)
            print("Duplicates: {}".format(" ".join(["'{0}'".format(img) for img in file_list])))
            if CONF.delete_duplicates:
                for path in file_list[1:]:
                    print(f"Removing {path} duplicate of {file_list[0]}")
                    path.unlink(missing_ok=True)
                    tombstone = path.with_suffix(CONF.tombstone)
                    tombstone.write_text(str(file_list[0]))
        hash_queue.task_done()

def find_similar_images(userpaths):
    image_filenames = []
    for userpath in userpaths:
        image_filenames += [f for f in Path(userpath).iterdir() if f.is_file() and is_image(f)]
    for img in sorted(image_filenames):
        img_queue.put((STD_PRIO, img, MAIN_FUNC))

if __name__ == '__main__':
    for i in range(CONF.threads):
        Thread(target=get_image_hash, daemon=True).start()
    Thread(target=check_image_hash, daemon=True).start()
    t = Thread(target=find_similar_images, daemon=False, args=(CONF.path,))
    t.start()
    try:
        t.join()
        img_queue.join()
        hash_queue.join()
    except KeyboardInterrupt:
        sys.exit()
