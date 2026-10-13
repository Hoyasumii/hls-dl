#!/usr/bin/env python3
"""Baixa streams HLS (.m3u8) sem criptografia e junta em um único arquivo.

Uso:
  python3 hls_dl.py LINK [LINK ...]
  python3 hls_dl.py -f links.txt          # um link por linha
  python3 hls_dl.py LINK -n meu_video     # nome do arquivo (sem extensão)
  python3 hls_dl.py LINK -o ~/Videos -j 16
"""
import argparse
import os
import re
import shutil
import sys
import tempfile
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

DEFAULT_OUT = "/sdcard/Download"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(url, retries=5, timeout=60):
    for i in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
                return r.read()
        except Exception:
            if i == retries - 1:
                raise
            time.sleep(2)


def parse_playlist(url):
    """Retorna (url_init|None, [urls dos segmentos]). Escolhe a melhor qualidade se for master."""
    text = fetch(url).decode("utf-8", "replace")
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    if any(l.startswith("#EXT-X-STREAM-INF") for l in lines):
        best, best_bw = None, -1
        for i, l in enumerate(lines):
            if l.startswith("#EXT-X-STREAM-INF"):
                m = re.search(r"BANDWIDTH=(\d+)", l)
                bw = int(m.group(1)) if m else 0
                if bw > best_bw and i + 1 < len(lines):
                    best, best_bw = lines[i + 1], bw
        return parse_playlist(urljoin(url, best))

    if any(l.startswith("#EXT-X-KEY") and "METHOD=NONE" not in l for l in lines):
        raise RuntimeError("stream criptografado (EXT-X-KEY), não suportado")

    init = None
    segs = []
    for l in lines:
        if l.startswith("#EXT-X-MAP"):
            m = re.search(r'URI="([^"]+)"', l)
            if m:
                init = urljoin(url, m.group(1))
        elif not l.startswith("#"):
            segs.append(urljoin(url, l))
    if not segs:
        raise RuntimeError("nenhum segmento encontrado na playlist")
    return init, segs


def download(url, workdir, name, jobs):
    init, segs = parse_playlist(url)
    paths = []
    if init:
        paths.append(os.path.join(workdir, "init"))
        with open(paths[0], "wb") as f:
            f.write(fetch(init))

    done = [0]

    def get(i_u):
        i, u = i_u
        p = os.path.join(workdir, f"{i:06d}")
        with open(p, "wb") as f:
            f.write(fetch(u, timeout=120))
        done[0] += 1
        print(f"\r  {done[0]}/{len(segs)} segmentos", end="", flush=True)
        return p

    with ThreadPoolExecutor(jobs) as ex:
        paths += list(ex.map(get, enumerate(segs)))
    print()
    return paths, ("mp4" if init else "ts")


def guess_name(url):
    parts = [p for p in urlparse(url).path.split("/") if p and not p.endswith(".m3u8")]
    return "_".join(parts[-2:]) if parts else f"video_{int(time.time())}"


def main():
    ap = argparse.ArgumentParser(description="Baixador de HLS sem ffmpeg")
    ap.add_argument("links", nargs="*")
    ap.add_argument("-f", "--file", help="arquivo com um link por linha")
    ap.add_argument("-o", "--out", default=DEFAULT_OUT, help=f"pasta de saída (padrão {DEFAULT_OUT})")
    ap.add_argument("-n", "--name", help="nome do arquivo (só vale para 1 link)")
    ap.add_argument("-j", "--jobs", type=int, default=8, help="downloads simultâneos")
    a = ap.parse_args()

    links = list(a.links)
    if a.file:
        links += [l.strip() for l in open(a.file) if l.strip() and not l.startswith("#")]
    if not links:
        ap.error("informe ao menos um link")
    os.makedirs(a.out, exist_ok=True)

    fails = 0
    for n, url in enumerate(links, 1):
        print(f"[{n}/{len(links)}] {url[:90]}")
        workdir = tempfile.mkdtemp(prefix="hls_")
        final = None
        try:
            paths, ext = download(url, workdir, a.name, a.jobs)
            base = a.name if (a.name and len(links) == 1) else guess_name(url)
            final = os.path.join(a.out, f"{base}.{ext}")
            with open(final, "wb") as out:
                for p in paths:
                    with open(p, "rb") as f:
                        shutil.copyfileobj(f, out)
            print(f"  ok -> {final} ({os.path.getsize(final) / 1e6:.1f} MB)")
        except Exception as e:
            fails += 1
            print(f"\n  ERRO: {e}")
            if final and os.path.exists(final):
                os.remove(final)  # não deixa arquivo pela metade
        finally:
            shutil.rmtree(workdir, ignore_errors=True)  # limpa os temporários
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
