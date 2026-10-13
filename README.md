# hls_dl

Baixa streams HLS (`.m3u8`) sem precisar de ffmpeg ou yt-dlp. Baixa os segmentos em paralelo, junta em ordem num único arquivo e apaga os temporários.

## Stack

<p>
  <img src="https://skill-icons.alanreisanjo.workers.dev/svg/python-dark.svg" alt="Python" width="48" />
  <img src="https://skill-icons.alanreisanjo.workers.dev/svg/bash-dark.svg" alt="Bash" width="48" />
  <img src="https://skill-icons.alanreisanjo.workers.dev/svg/android-dark.svg" alt="Android / Termux" width="48" />
  <img src="https://skill-icons.alanreisanjo.workers.dev/svg/linux-dark.svg" alt="Linux" width="48" />
</p>

- **Python 3**: apenas biblioteca padrão, sem dependências
- **Bash/sh**: script de instalação
- **Termux / Linux**: feito para rodar no Termux, funciona em qualquer Linux

## Instalação

Copie e cole no terminal:

```sh
curl -fsSL https://raw.githubusercontent.com/Hoyasumii/hls-dl/main/install.sh | sh
```

O script baixa o `hls_dl` para `$PREFIX/bin` (Termux) ou `~/.local/bin` (outros) e adiciona ao PATH se necessário.

## Uso

```sh
hls_dl "LINK.m3u8"                 # um link
hls_dl "LINK1" "LINK2"             # vários links
hls_dl -f links.txt                # um link por linha
hls_dl "LINK" -n meu_video         # nome do arquivo (sem extensão)
hls_dl "LINK" -o ~/Videos -j 16    # pasta de saída e downloads paralelos
```

Saída padrão: `/sdcard/Download`.

## Limitações

- Não suporta streams criptografados (`EXT-X-KEY`)
- Links com `expires=` vencido falham
